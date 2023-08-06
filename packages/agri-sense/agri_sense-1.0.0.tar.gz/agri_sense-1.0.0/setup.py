from setuptools import setup

setup(
    name='agri_sense',
    version='1.0.0',
    description='A package for agricultural sensing in India',
    packages=['agri_sense'],
    install_requires=[
     # list your package dependencies here
    'numpy==1.17.4',
    'pandas==1.1.5',
    'geopandas==0.13.0',
    'matplotlib==3.1.2',
    'descartes==1.1.0',
    'rasterio==1.3.6',
    'Pillow==9.5.0',
    ]
    )