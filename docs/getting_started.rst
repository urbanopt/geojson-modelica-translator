.. _getting_started:

Getting Started
===============

:code:`pip install geojson-modelica-translator`

* Install `Docker <https://docs.docker.com/get-docker/>`_ for your platform
* Configure Docker on your local desktop to have at least 4 GB Ram and 2 cores. This is configured under the Docker Preferences.

For help and command documentation in the terminal: :code:`uo_des -h`

Documentation for each command can be found at:

* :code:`uo_des build-system-param -h`
* :code:`uo_des create-model -h`
* :code:`uo_des run-model -h`

Library Installation
--------------------

The GeoJSON Modelica Translator is in alpha-phase development and the functionality is limited. Currently, the proposed approach for getting started is outlined in this readme. You need Python 3, pip 3, and Poetry to install/build the packages. Note that the best approach is to use Docker to run the Modelica models as this approach does not require Python 2.

* Clone this repo into a working directory
* (optional/as-needed) Add Python 3 to the environment variables
* Install Poetry (:code:`pip install poetry`). More information on Poetry can be found `here <https://python-poetry.org/docs/>`_.
* Install `Docker <https://docs.docker.com/get-docker/>`_ for your platform
* Configure Docker on your local desktop to have at least 4 GB Ram and 2 cores. This is configured under the Docker Preferences.
* Install the Modelica Buildings Library from GitHub
    * Clone https://github.com/lbl-srg/modelica-buildings/ into a working directory outside of the GMT directory
    * Change to the directory inside the modelica-buildings repo you just checked out. (:code:`cd modelica-buildings`)
    * Install git-lfs
        * Mac: :code:`brew install git-lfs; git lfs install`
        * Ubuntu: :code:`sudo apt install git-lfs; git lfs install`
    * Pull the correct staging branch for this project with: :code:`git checkout issue2204_gmt_mbl`
    * Add the Modelica Buildings Library path to your MODELICAPATH environment variable (e.g., export MODELICAPATH=${MODELICAPATH}:$HOME/path/to/modelica-buildings).
* Return to the GMT root directory and run :code:`poetry install`
* Test if everything is installed correctly by running :code:`poetry run tox`
    * This should run all unit tests, pre-commit, and build the docs.

The tests should all pass assuming the libraries are installed correctly on your computer. Also, there will be a set of Modelica models that are created and persisted into the :code:`tests/output` folder and the :code:`tests/model_connectors/output` folder. These files can be inspected in your favorite Modelica editor.
