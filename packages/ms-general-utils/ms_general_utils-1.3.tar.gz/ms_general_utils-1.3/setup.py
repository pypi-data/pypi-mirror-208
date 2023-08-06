"""
Setup configuration file
"""
from setuptools import setup, find_packages

setup(
    name='ms_general_utils',
    packages=find_packages(),
    include_package_data=True,
    version='1.3',
    description='General functions for the implementation of microservices.',
    authors=[
        {"name": "Alejandro A. Serrano Correa", "email": "alejandroasc93@gmail.com"},
        {"name": "Rene Gonzalez Ramos", "email": "rgramos9310@gmail.com"}
    ],
    license="GPLv3",
    url="https://github.com/rgramos/ms-utils.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
