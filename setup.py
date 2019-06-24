#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from management.update_schemas import UpdateSchemas

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='',
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
        # 'create_example': CreateExample,
        # 'add_copyrights': AddCopyrights,
    },
)
