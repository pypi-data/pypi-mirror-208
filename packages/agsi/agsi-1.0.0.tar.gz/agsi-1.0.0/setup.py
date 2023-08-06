from setuptools import setup, find_packages

setup(
    name='agsi',
    version='1.0.0',
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