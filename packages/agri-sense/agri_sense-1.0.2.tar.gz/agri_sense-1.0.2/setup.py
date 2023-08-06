from setuptools import setup

setup(
    name='agri_sense',
    version='1.0.2',
    description='A package for agricultural sensing in India',
    packages=['agri_sense'],
    install_requires=[
     # list your package dependencies here
    'numpy',
    'pandas',
    'geopandas',
    'matplotlib',
    'descartes',
    'rasterio',
    'Pillow',
    ]
    )