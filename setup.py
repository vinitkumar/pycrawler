"""Setuptools."""
from __future__ import absolute_import
from setuptools import setup, find_packages

version = '3.0.0'

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
        'beautifulsoup4==4.9.3',
        'future==0.14.3',
        'pytest==2.9.2',
        'six==1.9.0',
        'rich==10.3.0',
        'tqdm==4.66.3',
    ],
)
