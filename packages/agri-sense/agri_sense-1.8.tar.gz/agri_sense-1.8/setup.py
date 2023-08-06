from setuptools import setup, find_packages

setup(
    name='agri_sense',
    version='1.8',
    description='A package for agricultural sensing in India',
    packages=find_packages(),
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