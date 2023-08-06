# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

import Lab3

setup(
    name="kolyaklimkLab3",
    version="0.2.0",
    description=open('README.MD').read(),
    author="kolyaklimk",
    author_email="kolyaklimk@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["regex"]
)
