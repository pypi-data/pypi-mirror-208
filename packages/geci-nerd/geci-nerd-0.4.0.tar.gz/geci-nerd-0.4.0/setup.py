from setuptools import setup, find_packages

setup(
    author="Ciencia de Datos • GECI",
    author_email="ciencia.datos@islas.org.mx",
    description="Numerical Estimation of Rodenticide Density (NERD)",
    long_description="The eradication of rodents is central to island conservation efforts and the aerial broadcast of rodenticide bait is the preferred dispersal method. To improve accuracy and expedite the evaluation of aerial operations, we developed an algorithm for the numerical estimation of rodenticide density (NERD). The NERD algorithm performs calculations with increased accuracy, displaying results almost in real-time. NERD describes the relationship between bait density, the mass flow rate of rodenticide through the bait bucket, and helicopter speed and produces maps of bait density on the ground. NERD also facilitates the planning of helicopter flight paths and allows for the instant identification of areas with low or high bait density.",
    name="geci-nerd",
    packages=find_packages(),
    url="https://github.com/IslasGECI/nerd",
    version="0.4.0",
    install_requires=[
        "descartes",
        "fiona",
        "geojsoncontour",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "shapely",
        "tqdm",
        "utm",
    ],
)
