import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
version = "0.12.1"
setuptools.setup(
    name="lcbuilder", # Replace with your own username
    version=version,
    author="M. Dévora-Pajares",
    author_email="mdevorapajares@protonmail.com",
    description="Easy light curve builder from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PlanetHunders/lcbuilder",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['numpy==1.23.5',
                        'astropy==5.0.4',
                        'everest-pipeline==2.0.12',
                        #'eleanor==2.0.5', included with submodule
                        'pandas==1.5.3',
                        "lightkurve==2.4.0",
                        "photutils==1.0.2",
                        "scipy==1.8.0",
                        "statsmodels==0.13.5",
                        "tess-point==0.6.1",
                        'torch==2.0.0',
                        "foldedleastsquares==1.0.42",
                        'typing_extensions==4.3.0', #For astropy version
                        'urllib3==1.26.13',
                        "wotan==1.9",
    ]
)