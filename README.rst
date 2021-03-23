GeoJSON Modelica Translator (GMT)
---------------------------------

.. image:: https://github.com/urbanopt/geojson-modelica-translator/actions/workflows/ci.yml/badge.svg?branch=develop
    :target: https://github.com/urbanopt/geojson-modelica-translator/actions/workflows/ci.yml

.. image:: https://coveralls.io/repos/github/urbanopt/geojson-modelica-translator/badge.svg?branch=develop
    :target: https://coveralls.io/github/urbanopt/geojson-modelica-translator?branch=develop

.. image:: https://badge.fury.io/py/GeoJSON-Modelica-Translator.svg
    :target: https://pypi.org/project/GeoJSON-Modelica-Translator/

Description
-----------

The GeoJSON Modelica Translator (GMT) is a one-way trip from GeoJSON in combination with a well-defined instance of the system parameters schema to a Modelica package with multiple buildings loads, energy transfer stations, distribution networks, and central plants. The project will eventually allow multiple paths to build up different district heating and cooling system topologies; however, the initial implementation is limited to 1GDH and 4GDHC.

The project is motivated by the need to easily evaluate district energy systems. The goal is to eventually cover the various generations of heating and cooling systems as shown in the figure below. The need to move towards 5GDHC systems results in higher efficiencies and greater access to additional waste-heat sources.

.. image:: https://raw.githubusercontent.com/urbanopt/geojson-modelica-translator/develop/docs/images/des-generations.png

Getting Started
---------------

It is possible to test the GeoJSON to Modelica Translator (GMT) by simpling installing the Python package and running the
command line interface (CLI) with results from and URBANopt SDK set of results. However, to fully leverage the
functionality of this package (e.g., running simulations), then you must also install the Modelica Buildings
library (MBL) and Docker. Instructions for installing and configuring the MBL and Docker are available
`here <docs/getting_started.rst>`_

To simply scaffold out a Modelica package that can be inspected in a Modelica environment (e.g., Dymola) then
run the following code below up to the point of run-model. The example generates a complete 4th Generation District
Heating and Cooling (4GDHC) system with time series loads that were generated from the URBANopt SDK using
OpenStudio/EnergyPlus simulations.

.. code-block:: bash

    pip install geojson-modelica-translator

    # from the simulation results within a checkout of this repository
    # in the ./tests/management/data/sdk_project_scraps path.

    # generate the system parameter from the results of the URBANopt SDK and OpenStudio Simulations
    uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json

    # create the modelica package (requires installation of the MBL)
    uo_des create-model sys_param.json

    # test running the new Modelica package (requires installation of Docker)
    uo_des run-model model_from_sdk

More example projects are available in an accompanying
`example repository <https://github.com/urbanopt/geojson-modelica-translator-examples>`_.

Architecture Overview
---------------------

The GMT is designed to enable "easy" swapping of building loads, district systems, and newtork topologies. Some
of these functionalities are more developed than others, for instance swapping building loads between Spawn and
RC models (using TEASER) is fleshed out; however, swapping between a first and fifth generation heating system has
yet to be fully implemented.

The diagram below is meant to illustrate the future proposed interconnectivity and functionality of the
GMT project.

.. image:: https://raw.githubusercontent.com/urbanopt/geojson-modelica-translator/develop/docs/images/des-connections.png

There are various models that exist in the GMT and are described in the subsections below. See the more `comprehensive
documentation on the GMT <https://docs.urbanopt.net/geojson-modelica-translator/>`_ or the `documentation on
URBANopt SDK  <https://docs.urbanopt.net/>`_.

GeoJSON and System Parameter Files
++++++++++++++++++++++++++++++++++

This module manages the connection to the GeoJSON file including any calculations that are needed. Calculations
can include distance calculations, number of buildings, number of connections, etc.

The GeoJSON model should include checks for ensuring the accuracy of the area calculations, non-overlapping building
areas and coordinates, and various others.

Load Model Connectors
+++++++++++++++++++++

The Model Connectors are libraries that are used to connect between the data that exist in the GeoJSON with a
model-based engine for calculating loads (and potentially energy consumption). Examples includes, TEASER,
Data-Driven Model (DDM), CSV, Spawn, etc.

Simulation Mapper Class / Translator
++++++++++++++++++++++++++++++++++++

The Simulation Mapper Class can operate at mulitple levels:

1. The GeoJSON level -- input: geojson, output: geojson+
2. The Load Model Connection -- input: geojson+, output: multiple files related to building load models (spawn, rom, csv)
3. The Translation to Modelica -- input: custom format, output: .mo (example inputs: geojson+, system design parameters). The translators are implicit to the load model connectors as each load model requires different paramters to calculate the loads.

In some cases, the Level 3 case (translation to Modelica) is a blackbox method (e.g. TEASER) which prevents a
simulation mapper class from existing at that level.
