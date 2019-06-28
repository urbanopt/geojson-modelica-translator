#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from management.update_schemas import UpdateSchemas
from management.update_licenses import UpdateLicenses

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='GeoJSON Modelica Translator',
    version='0.1.0',
    description='Package for converting GeoJSON to Modelica models for Urban Scale Analyses.',
    long_description=readme,
    author='Nicholas Long',
    author_email='nicholas.long@nrel.gov',
    url='https://github.com/urbanopt/geojson_modelica_translator',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    cmdclass={
        'update_schemas': UpdateSchemas,
        'update_licenses': UpdateLicenses,
    },
)
