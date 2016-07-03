"""Setuptools."""
from __future__ import absolute_import
from setuptools import setup, find_packages

version = '2.0.0'

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
        'beautifulsoup4==4.4.1',
        'modernize==0.4',
        'six==1.9.0',
        'astroid==1.3.6',
        'future==0.14.3',
        'gnureadline==6.3.3',
        'ipython==3.1.0',
        'logilab-common==0.63.2',
        'modernize==0.4',
        'six==1.9.0',
    ],
)
