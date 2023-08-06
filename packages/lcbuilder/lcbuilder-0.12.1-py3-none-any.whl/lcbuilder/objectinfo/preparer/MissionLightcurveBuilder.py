import logging
import re
import shutil
import everest
import pandas

import sys

from everest.missions.k2 import Season

import lcbuilder.eleanor
sys.modules['eleanor'] = sys.modules['lcbuilder.eleanor']
import eleanor
from lcbuilder.eleanor.targetdata import TargetData

import numpy as np
from astropy.coordinates import SkyCoord
from lcbuilder import constants
from lcbuilder.LcBuild import LcBuild
from lcbuilder.constants import CUTOUT_SIZE, LIGHTKURVE_CACHE_DIR, ELEANOR_CACHE_DIR
from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder.photometry.aperture_extractor import ApertureExtractor
from lcbuilder.star import starinfo
from lcbuilder.objectinfo.ObjectProcessingError import ObjectProcessingError
from lcbuilder.objectinfo.preparer.LightcurveBuilder import LightcurveBuilder
from astropy import units as u
import lightkurve as lk
import matplotlib.pyplot as plt
import os
from lightkurve import KeplerLightCurve


class MissionLightcurveBuilder(LightcurveBuilder):
    """
    Prepares the data from the mission official repositories of a given target
    """
    def __init__(self):
        super().__init__()

    def build(self, object_info: MissionObjectInfo, sherlock_dir, caches_root_dir, keep_tpfs: bool = True):
        mission_id = object_info.mission_id()
        sherlock_id = object_info.sherlock_id()
        logging.info("Retrieving star catalog info...")
        mission, mission_prefix, id = super().parse_object_id(mission_id)
        if mission_prefix not in self.star_catalogs:
            raise ValueError("Wrong object id " + mission_id)
        cadence = object_info.cadence if object_info.cadence is not None else "short"
        author_extension = '_long' if isinstance(cadence, (int, float)) and cadence >= 600 and mission == constants.MISSION_TESS else ''
        author = object_info.author if object_info.author is not None else self.authors[mission + author_extension]
        logging.info("Downloading lightcurve files...")
        sectors = None if object_info.sectors == 'all' or mission != constants.MISSION_TESS else object_info.sectors
        campaigns = None if object_info.sectors == 'all' or mission != constants.MISSION_K2 else object_info.sectors
        quarters = None if object_info.sectors == 'all' or mission != constants.MISSION_KEPLER else object_info.sectors
        tokens = sectors if sectors is not None else campaigns if campaigns is not None else quarters
        tokens = tokens if tokens is not None else "all"
        transits_min_count = 1
        apertures = {}
        tpf_search_results = lk.search_targetpixelfile(str(mission_id))
        for tpf_search_result in tpf_search_results:
            logging.info("There is data for Mission: %s, Year %.0f, Author: %s, ExpTime: %.0f",
                         tpf_search_result.mission[0], tpf_search_result.year[0], tpf_search_result.author[0],
                         tpf_search_result.exptime[0].value)
        tpfs_dir = sherlock_dir + "/tpfs/"
        if not os.path.exists(tpfs_dir):
            os.mkdir(tpfs_dir)
        lc_data = None
        if object_info.apertures is None:
            if isinstance(cadence, (int, float)) and cadence >= 600 and \
                    mission_prefix == constants.MISSION_ID_TESS and author == constants.ELEANOR_AUTHOR:
                source = "eleanor"
                if object_info.ra is not None and object_info.dec is not None:
                    coords = SkyCoord(ra=object_info.ra, dec=object_info.dec, unit=(u.deg, u.deg))
                    star = eleanor.source.multi_sectors(coords=coords, sectors=object_info.sectors,
                                                        post_dir=caches_root_dir + ELEANOR_CACHE_DIR,
                                                        metadata_path=caches_root_dir + ELEANOR_CACHE_DIR)
                else:
                    object_id_parsed = re.search(super().NUMBERS_REGEX, object_info.id)
                    object_id_parsed = object_info.id[object_id_parsed.regs[0][0]:object_id_parsed.regs[0][1]]
                    star = eleanor.multi_sectors(tic=object_id_parsed, sectors=object_info.sectors,
                                                 post_dir=caches_root_dir + ELEANOR_CACHE_DIR,
                                                 metadata_path=caches_root_dir + ELEANOR_CACHE_DIR)
                if star is None:
                    raise ValueError("No data for this object")
                if star[0].tic:
                    # TODO FIX star info objectid
                    logging.info("Assotiated TIC is " + str(star[0].tic))
                    tpfs = lk.search_tesscut("TIC " + str(star[0].tic), sector=sectors) \
                        .download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                                      cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
                    star_info = starinfo.StarInfo(object_info.sherlock_id(),
                                                  *self.star_catalogs[constants.MISSION_ID_TESS]
                                                  .catalog_info(int(star[0].tic)))
                data = []
                for s in star:
                    datum = TargetData(s, height=CUTOUT_SIZE, width=CUTOUT_SIZE, do_pca=True)
                    data.append(datum)
                    for tpf in tpfs:
                        if tpf.sector == s.sector:
                            apertures[s.sector] = ApertureExtractor.from_boolean_mask(datum.aperture.astype(bool),
                                                                                      tpf.column, tpf.row)
                            if keep_tpfs:
                                shutil.copy(tpf.path, tpfs_dir + os.path.basename(tpf.path))
                quality_bitmask = np.bitwise_and(data[0].quality.astype(int), 175)
                lc_data = self.extract_eleanor_lc_data(data)
                lc = data[0].to_lightkurve(data[0].__dict__[object_info.eleanor_corr_flux],
                                           quality_mask=quality_bitmask).remove_nans().flatten()
                sectors = [datum.source_info.sector for datum in data]
                if len(data) > 1:
                    for datum in data[1:]:
                        quality_bitmask = np.bitwise_and(datum.quality, 175)
                        lc = lc.append(datum.to_lightkurve(datum.pca_flux, quality_mask=quality_bitmask).remove_nans()
                                       .flatten())
                    transits_min_count = 2
            elif mission_prefix == constants.MISSION_ID_KEPLER_2 and author == constants.EVEREST_AUTHOR:
                target_name = str(mission_id)
                source = 'everest'
                if object_info.ra is not None and object_info.dec is not None:
                    target_name = str(object_info.ra) + ' ' + str(object_info.dec)
                    star_info = starinfo.StarInfo(sherlock_id,
                                                  *self.star_catalogs[constants.MISSION_ID_TESS].coords_catalog_info(
                                                      object_info.ra, object_info.dec))
                else:
                    star_info = starinfo.StarInfo(sherlock_id, *self.star_catalogs[mission_prefix].catalog_info(id))
                lc = None
                everest_cadence = 'sc' if isinstance(cadence, str) and (cadence == 'short' or cadence == 'fast') or (isinstance(cadence, int) and cadence < 600) else 'lc'
                if campaigns is None:
                    campaigns = Season(id)
                if not isinstance(campaigns, (list, np.ndarray)):
                    campaigns = [campaigns]
                for campaign in campaigns:
                    try:
                        everest_star = everest.user.Everest(id, campaign, quiet=True, cadence=everest_cadence)
                    except:
                        raise ValueError("Can't find object " + str(id) + " with " + str(cadence) + " cadence and " +
                                     str(campaign) + " campaign in Everest")
                    quality_mask = ((everest_star.quality != 0) & (everest_star.quality != 27))
                    time = np.delete(everest_star.time, quality_mask)
                    flux = np.delete(everest_star.flux, quality_mask)
                    if lc is None:
                        lc = KeplerLightCurve(time, flux).normalize()
                    else:
                        lc = lc.append(KeplerLightCurve(time, flux).normalize())
                lc = lc.remove_nans()
                transits_min_count = 2
            else:
                target_name = str(mission_id)
                if object_info.ra is not None and object_info.dec is not None:
                    target_name = str(object_info.ra) + ' ' + str(object_info.dec)
                    star_info = starinfo.StarInfo(sherlock_id,
                                                  *self.star_catalogs[constants.MISSION_ID_TESS].coords_catalog_info(
                                                      object_info.ra, object_info.dec))
                else:
                    star_info = starinfo.StarInfo(sherlock_id, *self.star_catalogs[mission_prefix].catalog_info(id))
                lcf_search_results = lk.search_lightcurve(target_name, mission=mission, exptime=cadence,
                                               sector=sectors, quarter=quarters,
                                               campaign=campaigns, author=author)
                lcf = lcf_search_results.download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR)
                tpfs = lk.search_targetpixelfile(target_name, mission=mission, exptime=cadence,
                                                 sector=sectors, quarter=quarters,
                                                 campaign=campaigns, author=author)\
                    .download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                                  cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
                if lcf is None:
                    raise ObjectProcessingError("The target " + str(mission_id) + " is not available for the author " + author +
                                     ", cadence " + str(cadence) + "s and sectors " + str(tokens))
                lc_data = self.extract_lc_data(lcf)
                lc = None
                matching_objects = []
                for tpf in tpfs:
                    if keep_tpfs:
                        shutil.copy(tpf.path, tpfs_dir + os.path.basename(tpf.path))
                    if mission_prefix == constants.MISSION_ID_KEPLER:
                        sector = tpf.quarter
                    elif mission_prefix == constants.MISSION_ID_TESS:
                        sector = tpf.sector
                    if mission_prefix == constants.MISSION_ID_KEPLER_2:
                        sector = tpf.campaign
                    apertures[sector] = ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row)
                for i in range(0, len(lcf.data)):
                    if lcf.data[i].label == mission_id:
                        if lc is None:
                            lc = lcf.data[i].normalize()
                        else:
                            lc = lc.append(lcf.data[i].normalize())
                    else:
                        matching_objects.append(lcf.data[i].label)
                matching_objects = set(matching_objects)
                if len(matching_objects) > 0:
                    logging.warning("================================================")
                    logging.warning("TICS IN THE SAME PIXEL: " + str(matching_objects))
                    logging.warning("================================================")
                if lc is None:
                    tokens = sectors if sectors is not None else campaigns if campaigns is not None else quarters
                    tokens = tokens if tokens is not None else "all"
                    raise ObjectProcessingError("The target " + target_name + " is not available for the author " + author +
                                     ", cadence " + str(cadence) + "s and sectors " + str(tokens))
                lc = lc.remove_nans()
                transits_min_count = self.__calculate_transits_min_count(len(lcf))
                if mission_prefix == constants.MISSION_ID_KEPLER:
                    sectors = [lcfile.quarter for lcfile in lcf]
                elif mission_prefix == constants.MISSION_ID_TESS:
                    sectors = [file.sector for file in lcf]
                elif mission_prefix == constants.MISSION_ID_KEPLER_2:
                    logging.info("Correcting K2 motion in light curve...")
                    sectors = [lcfile.campaign for lcfile in lcf]
                    lc = lc.to_corrector("sff").correct(windows=20)
                source = "tpf"
        else:
            logging.info("Using user apertures!")
            tpf_search_results = lk.search_targetpixelfile(str(mission_id), mission=mission, exptime=cadence,
                                             sector=sectors, quarter=quarters, campaign=campaigns,
                                             author=author)
            tpfs = tpf_search_results.download_all(download_dir=caches_root_dir + LIGHTKURVE_CACHE_DIR,
                                                   cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
            source = "tpf"
            apertures = object_info.apertures
            lc = None
            for tpf in tpfs:
                if keep_tpfs:
                    shutil.copy(tpf.path, tpfs_dir + os.path.basename(tpf.path))
                if mission_prefix == constants.MISSION_ID_KEPLER:
                    sector = tpf.quarter
                elif mission_prefix == constants.MISSION_ID_TESS:
                    sector = tpf.sector
                elif mission_prefix == constants.MISSION_ID_KEPLER_2:
                    sector = tpf.campaign
                boolean_aperture = ApertureExtractor.from_pixels_to_boolean_mask(apertures[sector], tpf.column, tpf.row,
                                                                         CUTOUT_SIZE, CUTOUT_SIZE)
                tpf.plot(aperture_mask=boolean_aperture, mask_color='red')
                plt.savefig(sherlock_dir + "/fov/Aperture_[" + str(sector) + "].png")
                plt.close()
                if mission_prefix == constants.MISSION_ID_KEPLER:
                    corrector = lk.KeplerCBVCorrector(tpf)
                    corrector.plot_cbvs([1, 2, 3, 4, 5, 6, 7])
                    raw_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture).remove_nans()
                    plt.savefig(sherlock_dir + "/Corrector_components[" + str(sector) + "].png")
                    plt.close()
                    it_lc = corrector.correct([1, 2, 3, 4, 5])
                    ax = raw_lc.plot(color='C3', label='SAP Flux', linestyle='-')
                    it_lc.plot(ax=ax, color='C2', label='CBV Corrected SAP Flux', linestyle='-')
                    plt.savefig(sherlock_dir + "/Raw_vs_CBVcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                elif mission_prefix == constants.MISSION_ID_KEPLER_2:
                    raw_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture).remove_nans()
                    it_lc = raw_lc.to_corrector("sff").correct(windows=20)
                    ax = raw_lc.plot(color='C3', label='SAP Flux', linestyle='-')
                    it_lc.plot(ax=ax, color='C2', label='CBV Corrected SAP Flux', linestyle='-')
                    plt.savefig(sherlock_dir + "/Raw_vs_SFFcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                elif mission_prefix == constants.MISSION_ID_TESS:
                    temp_lc = tpf.to_lightcurve(aperture_mask=boolean_aperture)
                    where_are_NaNs = np.isnan(temp_lc.flux)
                    temp_lc = temp_lc[np.where(~where_are_NaNs)]
                    regressors = tpf.flux[np.argwhere(~where_are_NaNs), ~boolean_aperture]
                    temp_token_lc = [temp_lc[i: i + 2000] for i in range(0, len(temp_lc), 2000)]
                    regressors_token = [regressors[i: i + 2000] for i in range(0, len(regressors), 2000)]
                    it_lc = None
                    raw_it_lc = None
                    item_index = 0
                    for temp_token_lc_item in temp_token_lc:
                        regressors_token_item = regressors_token[item_index]
                        design_matrix = lk.DesignMatrix(regressors_token_item, name='regressors').pca(5).append_constant()
                        corr_lc = lk.RegressionCorrector(temp_token_lc_item).correct(design_matrix)
                        if it_lc is None:
                            it_lc = corr_lc
                            raw_it_lc = temp_token_lc_item
                        else:
                            it_lc = it_lc.append(corr_lc)
                            raw_it_lc = raw_it_lc.append(temp_token_lc_item)
                        item_index = item_index + 1
                    ax = raw_it_lc.plot(label='Raw light curve')
                    it_lc.plot(ax=ax, label='Corrected light curve')
                    plt.savefig(sherlock_dir + "/Raw_vs_DMcorrected_lc[" + str(sector) + "].png")
                    plt.close()
                if lc is None:
                    lc = it_lc.normalize()
                else:
                    lc = lc.append(it_lc.normalize())
            lc = lc.remove_nans()
            lc.plot(label="Normalized light curve")
            plt.savefig(sherlock_dir + "/Normalized_lc[" + str(sector) + "].png")
            plt.close()
            transits_min_count = self.__calculate_transits_min_count(len(tpfs))
            if mission_prefix == constants.MISSION_ID_KEPLER or mission_id == constants.MISSION_ID_KEPLER_2:
                sectors = [lcfile.quarter for lcfile in tpfs]
            elif mission_prefix == constants.MISSION_ID_TESS:
                sectors = [file.sector for file in tpfs]
            if mission_prefix == constants.MISSION_ID_KEPLER_2:
                logging.info("Correcting K2 motion in light curve...")
                sectors = [lcfile.campaign for lcfile in tpfs]
            sectors = None if sectors is None else np.unique(sectors)
            lc_data = None
        return LcBuild(lc, lc_data, star_info, transits_min_count, cadence, None, sectors, source, apertures)

    def __calculate_transits_min_count(self, len_data):
        return 1 if len_data == 1 else 2

    def extract_eleanor_lc_data(self, eleanor_data):
        time = []
        flux = []
        flux_err = []
        background_flux = []
        quality = []
        centroids_x = []
        centroids_y = []
        motion_x = []
        motion_y = []
        [time.append(data.time) for data in eleanor_data]
        [flux.append(data.pca_flux) for data in eleanor_data]
        [flux_err.append(data.flux_err) for data in eleanor_data]
        [background_flux.append(data.flux_bkg) for data in eleanor_data]
        try:
            [quality.append(data.quality) for data in eleanor_data]
        except KeyError:
            logging.info("QUALITY info is not available.")
            [quality.append(np.full(len(data.time), np.nan)) for data in eleanor_data]
        [centroids_x.append(data.centroid_xs - data.cen_x) for data in eleanor_data]
        [centroids_y.append(data.centroid_ys - data.cen_y) for data in eleanor_data]
        [motion_x.append(data.x_com) for data in eleanor_data]
        [motion_y.append(data.y_com) for data in eleanor_data]
        time = np.concatenate(time)
        flux = np.concatenate(flux)
        flux_err = np.concatenate(flux_err)
        background_flux = np.concatenate(background_flux)
        quality = np.concatenate(quality)
        centroids_x = np.concatenate(centroids_x)
        centroids_y = np.concatenate(centroids_y)
        motion_x = np.concatenate(motion_x)
        motion_y = np.concatenate(motion_y)
        lc_data = pandas.DataFrame(columns=['time', 'flux', 'flux_err', 'background_flux', 'quality', 'centroids_x',
                                            'centroids_y', 'motion_x', 'motion_y'])
        lc_data['time'] = time
        lc_data['flux'] = flux
        lc_data['flux_err'] = flux_err
        lc_data['background_flux'] = background_flux
        lc_data['quality'] = quality
        lc_data['centroids_x'] = centroids_x
        lc_data['centroids_y'] = centroids_y
        lc_data['motion_x'] = motion_x
        lc_data['motion_y'] = motion_y
        return lc_data

