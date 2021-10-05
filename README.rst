GeoJSON Modelica Translator (GMT)
---------------------------------

.. image:: https://github.com/urbanopt/geojson-modelica-translator/actions/workflows/ci.yml/badge.svg?branch=develop
    :target: https://github.com/urbanopt/geojson-modelica-translator/actions/workflows/ci.yml

.. image:: https://coveralls.io/repos/github/urbanopt/geojson-modelica-translator/badge.svg?branch=develop
    :target: https://coveralls.io/github/urbanopt/geojson-modelica-translator?branch=develop

.. image:: https://badge.fury.io/py/geojson-modelica-translator.svg
    :target: https://badge.fury.io/py/geojson-modelica-translator

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
`here <docs/getting_started.rst>`_.

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
    uo_des create-model sys_param.json example_project.json model_from_sdk

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

As shown in the image, there are multiple building loads that can be deployed with the GMT and are described in the `Building Load Models`_ section below. These models, and the associated design parameters, are required to create a fully runnable Modelica model. The GMT leverages two file formats for generating the Modelica project and are the GeoJSON feature file and a System Parameter JSON file. See the more `comprehensive
documentation on the GMT <https://docs.urbanopt.net/geojson-modelica-translator/>`_ or the `documentation on
URBANopt SDK  <https://docs.urbanopt.net/>`_.

Building Load Models
++++++++++++++++++++

The building loads can be defined multiple ways depending on the fidelity of the required models. Each of the building load models are easily replaced using configuration settings within the System Parameters file. The 4 different building load models include:

#. Time Series in Watts: This building load is the total heating, cooling, and domestic hot water loads represented in a CSV type file (MOS file). The units are Watts and should be reported at an hour interval; however, finer resolution is possible. The load is defined as the load seen by the ETS.
#. Time Series as mass flow rate and delta temperature: This building load is similar to the other Time Series model but uses the load as seen by the ETS in the form of mass flow rate and delta temperature. The file format is similar to the other Time Series model but the columns are mass flow rate and delta temperature for heating and cooling separately.
#. RC Model: This model leverages the TEASER framework to generate an RC model with the correct coefficients based on high level parameters that are extracted from the GeoJSON file including building area and building type.
#. Spawn of EnergyPlus: This model uses EnergyPlus models to represent the thermal zone heat balance portion of the models while using Modelica for the remaining components. Spawn of EnergyPlus is still under development and currently only works on Linux-based systems.
