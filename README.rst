GeoJSON / Modelica Translator
=============================

.. image:: https://travis-ci.org/urbanopt/geojson-modelica-translator.svg?branch=develop
    :target: https://travis-ci.org/urbanopt/geojson-modelica-translator

.. image:: https://coveralls.io/repos/github/urbanopt/geojson-modelica-translator/badge.svg?branch=develop
    :target: https://coveralls.io/github/urbanopt/geojson-modelica-translator?branch=develop


Description
-----------

The GeoJSON / Modelica Translator is a one-way trip from GeoJSON with a well-defined property's schema to a set of Modelica buildings. The project will eventually allow multiple paths to model the loads portion of the building models; however, the initial implementation uses the Teaser library to create the RC models with the appropriate coefficients.

Getting Started
***************

The GeoJSON / Modelica Translator is still in early alpha-phase development and the functionality is limited. Currently, the proposed approach for getting started is to run the following

.. code-block::bash

    pip install -r requirements.txt
    py.test

The py.test tests should all pass assuming the libraries are installed correctly on your development computer. Also, there will be a set of Modelica models that are created and persisted into the `tests/output` folder.

Modules
*******

GeoJSON
+++++++

This module manages the connection to the GeoJSON file including any calculations that are needed. Calculations can include distance calculations, number of buildings, number of connections, etc.

The GeoJSON model should include checks for ensuring the accuracy of the area calculations, non-overlapping building areas and coordinates, and various others.

Load Model Connectors
+++++++++++++++++++++

The Model Connectors are libraries that are used to connect between the data that exist in the GeoJSON with a model-based engine for calculating loads (and potentially energy consumption). Examples includes, TEASER, Data-Driven Model (DDM), CSV, Spawn, etc.


Simulation Mapper Class / Translator
++++++++++++++++++++++++++++++++++++

The Simulation Mapper Class can operate at mulitple levels:

1. The GeoJSON level -- input: geojson, output: geojson+
2. The Load Model Connection -- input: geojson+, output: multiple files related to building load models (spawn, rom, csv)
3. The Translation to Modelica -- input: custom format, output: .mo (example inputs: geojson+, system design parameters). The translators are implicit to the load model connectors as each load model requires different paramters to calculate the loads.

In some cases, the Level 3 case (transalation to Modelica) is a blackbox method (e.g. TEASER) which prevents a simulation mapper class from existing at that level.

Adjacency Matrix
++++++++++++++++


Topology Maker
++++++++++++++


Managed Tasks
-------------

Updating Schemas
****************

There is managed task to automatically pull updated GeoJSON schemas from the `urbanopt-geojson-gem` GitHub project. A developer can run this command by calling

.. code-block::bash

    ./setup.py update_schemas

The developer should run the test suite after updating the schemas to ensure that nothing appears to have broken. Note that the tests do not cover all of the properties and should not be used as proof that everything works with the updated schemas.

Updating Copyrights
*******************


Todos
-----

* handle weather
* Validate remaining schema objects
