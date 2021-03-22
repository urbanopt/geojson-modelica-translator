.. _getting_started:

Getting Started
===============

There are three major steps to running the GeoJSON to Modelica Translator (GMT):

#. generating the GeoJSON and System Parameter JSON files,
#. creating of the Modelica package containing the district system, and
#. running the Modelica packge.

Depending on the use case, the need to run all the steps above may not be needed. For example:
it may be desirable to only generate the Modelica package and then open and run the model
in a Modelica user interface such as Dymola. Or, there may be a case to simply generate the
GeoJSON and System Parameter file from results of an URBANopt SDK simulation result set.

This Getting Started guide is broken up into three major setup steps:

#. Installing the GMT from PyPi
#. Installing and configuring the Modelica Buildings Library (MBL)
#. Installing and configuring Docker in order to run simulations using JModelica

GMT Installation
----------------

After installing Python and PIP run the following in a terminal (requires Python 3):

.. code-block:: bash

    pip install geojson-modelica-translator

After installation of the GMT, a new command line interface (called the URBANopt District Energy Systems [UO DES] CLI) can be used to run various commands. Without needing to install the `MBL`_ the user can use the CLI to build the system parameters file from the results of the URBANopt SDK. For more information run the following:

.. code-block:: bash

    uo_des -h
    uo_des build-system-param -h

    # example
    uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json

MBL Installation
----------------

The Modelica Buildings Library contains many models that are needed to assemble the district systems.
Installation of the MBL is done through Git and GitHub. Follow the instructions below to install the MBL needed for the GMT:

* Clone the `MBL`_ into a working directory outside of the GMT directory
* Change to the directory inside the modelica-buildings repo you just checked out. (:code:`cd modelica-buildings`)
* Install git-lfs
    * Mac: :code:`brew install git-lfs; git lfs install`
    * Ubuntu: :code:`sudo apt install git-lfs; git lfs install`
* Pull the correct staging branch for this project with: :code:`git checkout issue2204_gmt_mbl`
* Add the Modelica Buildings Library path to your MODELICAPATH environment variable (e.g., export MODELICAPATH=${MODELICAPATH}:$HOME/path/to/modelica-buildings). Restart your terminal to ensure that the MBL library is exported correctly.

Once the MBL is installed, then the CLI can be used to create the model with the following command:

.. code-block:: bash

    uo_des create-model -h

    # example
    uo_des create-model sys_param.json

The resulting Modelica package will be created and can be opened in a Modelica editor. Open the :code:`pacakge.mo` file in the root directory of the generated package. You will also need to
load the MBL into your Modelica editor.

Docker Installation
-------------------

The preferred method of running the simulations would be within Dymola; however, that is not a
practical solution for many based on the license requirement. The GMT enables the running of the
models using JModelica which requires the installtion of `Docker`_. To configure Docker, do the
following:

* Install `Docker <https://docs.docker.com/get-docker/>`_ for your system.
* Configure Docker on your local desktop to have at least 4 GB Ram and 2 cores. This is configured under the Docker Preferences.
* It is recommended to test the installation of Docker by simply running :code:`docker run hello-world` in a terminal.

After Docker is installed and configured, you can use the CLI to run the model using the following
command:

.. code-block:: bash

    uo_des run-model -h

    # example
    uo_des run-model model_from_sdk


.. _MBL: https://github.com/lbl-srg/modelica-buildings/
.. _Poetry: https://python-poetry.org/docs/
.. _Docker: https://docs.docker.com/get-docker/
