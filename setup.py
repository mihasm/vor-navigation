import setuptools
from os import path
import pathlib

with pathlib.Path("requirements.txt").open() as requirements_txt:
    install_requires = [line.strip() for line in requirements_txt if line.strip() and not line.startswith('#')]

setuptools.setup(
    name="vor-navigation",
    version="0.2.0",
    author="VOR Navigation Contributors",
    author_email="vor-navigation@example.com",
    description="A VOR (VHF Omnidirectional Range) navigation tool for aviation route planning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vor-navigation/vor-navigation",
    include_package_data=True,
    data_files=[('data', ['vor_mod/data/airports.xlsx','vor_mod/data/earth_nav.dat'])],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'vor-navigation=vor_mod.vor:main',
        ],
    },
    install_requires=install_requires,
)
