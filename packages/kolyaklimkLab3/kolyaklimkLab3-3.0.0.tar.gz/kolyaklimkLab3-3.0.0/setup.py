# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

import kolyaklimkLab3

setup(
    name="kolyaklimkLab3",
    version="3.0.0",
    description=open('README.MD').read(),
    author_email="kolyaklimk@gmail.com",
    packages=find_packages(include=["kolyaklimkLab3", "kolyaklimkLab3.*"]),
    zip_safe=False
)
