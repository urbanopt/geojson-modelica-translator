.. _getting_started:

Getting Started
===============

There are three major steps to running the GeoJSON to Modelica Translator (GMT):

#. generating the GeoJSON and System Parameter JSON files,
#. creating of the Modelica package containing the district system, and
#. running the Modelica package.

Depending on the use case, the need to run all the steps above may not be needed. For example:
it may be desirable to only generate the Modelica package and then open and run the model
in a Modelica user interface such as Dymola. Or, there may be a case to simply generate the
GeoJSON and System Parameter file from results of an URBANopt SDK simulation result set.

This Getting Started guide is broken up into three major setup steps:

#. Installing the GMT from PyPi
#. Installing and configuring the Modelica Buildings Library (MBL)
#. Installing and configuring Docker in order to run simulations using JModelica. This step is currently not required due to the MSL v4 upgrade not supporting JModelica. Therefore, it is recommended to run the models in Dymola.

GMT Installation
----------------

You must have PIP and Python 3.7 or later installed (run :code:`python --version` to see what version you're using). After installing Python and PIP run the following in a terminal (requires Python 3):

.. code-block:: bash

    pip install geojson-modelica-translator

After installation of the GMT, a new command line interface (called the URBANopt District Energy Systems [UO DES] CLI) can be used to run various commands. Without needing to install the `MBL`_ the user can use the CLI to build the system parameters file from the results of the URBANopt SDK. For more information run the following:

.. code-block:: bash

    uo_des -h
    uo_des build-system-param -h

    # the command below is only an example; however, it will run if the repository
    # is checked out and run in the following path: ./tests/management/data/sdk_project_scraps
    uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json

MBL Installation
----------------

The Modelica Buildings Library contains many models that are needed to assemble the district systems. Installation of the MBL is done through Git and GitHub. Follow the instructions below to install the MBL needed for the GMT:

* Download and extract the newest 9.1 version of the MBL from `<https://simulationresearch.lbl.gov/modelica/downloads/archive/modelica-buildings.html>`_
* Add the Modelica Buildings Library path to your MODELICAPATH environment variable (e.g., export MODELICAPATH=${MODELICAPATH}:$HOME/path/to/modelica-buildings). Restart your terminal to ensure that the MBL library is exported correctly.

Once the MBL is installed, then the CLI can be used to create the model with the following command:

.. code-block:: bash

    uo_des create-model -h

    # the command below is only an example; however, it will run if the repository
    # is checked out and run in the following path: ./tests/management/data/sdk_project_scraps
    uo_des create-model sys_param.json example_project.json model_from_sdk

The resulting Modelica package will be created and can be opened in a Modelica editor. Open the :code:`package.mo` file in the root directory of the generated package. You will also need to
load the MBL into your Modelica editor.

The latest version of this repository uses MBL v9.0.0. This version does not support running JModelica due to the upgrade to Modelica Standard Library (MSL) version 4. For this reason, the unit tests no longer run the models; therefore, you will need to mark the pytest to not run the simulations with :code:`poetry run pytest -m 'not simulation'`.

Test running the models with Dymola or OpenModelica. Dymola is used to test these models during development.


Docker Installation
-------------------

The preferred method of running the simulations would be within Dymola; however, that is not a
practical solution for many based on the license requirement. The GMT enables the running of the
models using JModelica which requires the installation of `Docker`_. To configure Docker, do the
following:

* Install `Docker <https://docs.docker.com/get-docker/>`_ for your system.
* Configure Docker Desktop to have at least 4 GB Ram and 2 cores. This is configured under the Docker Preferences.
* It is recommended to test the installation of Docker by simply running :code:`docker run hello-world` in a terminal.

After Docker is installed and configured, you can use the CLI to run the model using the following
command:

.. code-block:: bash

    uo_des run-model -h

    # the command below is only an example; however, it will run if the repository
    # is checked out and run in the following path: ./tests/management/data/sdk_project_scraps
    uo_des run-model model_from_sdk


.. _MBL: https://github.com/lbl-srg/modelica-buildings/
.. _Poetry: https://python-poetry.org/docs/
.. _Docker: https://docs.docker.com/get-docker/
