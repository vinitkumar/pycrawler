"""Setuptools."""
from __future__ import absolute_import
from setuptools import setup, find_packages

version = '2.1.0'

setup(
    name='pycrawler',
    version=version,
    description='A simple python crawler',
    author='Vinit Kumar',
    author_email='vinit.kumar@changer.nl',
    url='https://github.com/vinitkumar/pycrawler',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'beautifulsoup4==4.8.1',
        'future==0.14.3',
        'pytest==2.9.2',
        'six==1.9.0',
        'tqdm==4.38.0',
        'pytest-cov==2.2.1',
    ],
)
