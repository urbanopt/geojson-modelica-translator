.. _developer_resources:

.. autosummary::
   :toctree: _autosummary
   :recursive:

   geojson_modelica_translator

Developer Resources
===================

Design Overview
---------------

The GMT is designed to create an arbitrary number of user-configured models connected to other user-configured models to represent a district energy system.
GMT has "building blocks" that it uses to define and connect models, which currently include: Energy Transfer Stations (ETSs), Loads, Networks, and Plants.

.. image:: images/models-overview.png

Each block type is a collection of models, e.g. the Loads includes time series and spawn models. A model in GMT refers to an abstracted Modelica model. It generates Modelica code (the Modelica model) and is used to define connections to other models.

Each block type can "connect" (note this "connect" does not refer to Modelica's concept of "connect") to other specific block types. For example, you can connect a load to an ETS, but you cannot connect a load to a network.

Each block type has a corresponding directory inside of :code:`geojson_modelica_translator/model_connectors`, which contains its different model types (e.g. for Loads it contains the Time Series model and others).

Because models are different, even within a block type (e.g. different properties and maybe even ports), the GMT uses the concept of couplings for connecting models. Couplings define how two *specific* models connect in modelica.
For example, a coupling could define how the time series load actually connects to the heating indirect ETS.

    -- As an aside, if the GMT reached a point where all models within a block type implemented the same interface then couplings would not be necessary.

Getting Started as a Developer
------------------------------

There are a few steps that are imperative to complete when starting as a developer of the GMT. First, make sure
to follow the detailed instructions for setting up MBL and Docker in the `getting started <getting_started>`_ guide.

Follow the instructions below in order to configure your local environment:

* Clone this repo into a working directory
* (optional/as-needed) Add Python 3 to the environment variables
* For developers, dependency management is through `Poetry`_. Installation is accomplished by running :code:`pip install poetry`.
* Return to the GMT root directory and run :code:`poetry install`
* Test if everything is installed correctly by running :code:`poetry run pytest`. This will run all the unit and integration tests.
* Follow the instructions below to install pre-commit.
* To test pre-commit and building the documentation, you can run :code:`poetry run tox`

The tests should all pass assuming the libraries are installed correctly on your computer. Also, there will be a set
of Modelica models that are created and persisted into the :code:`tests/output` folder and the
:code:`tests/model_connectors/output` folder. These files can be inspected in your favorite Modelica editor.

Pre-commit
**********

This project uses `pre-commit <https://pre-commit.com/>`_ to ensure code consistency.
To enable pre-commit on every commit run the following from the command line from within the git checkout of the
GMT:

.. code-block:: bash

    pre-commit install

To run pre-commit against the files without calling git commit, then run the following. This is useful when cleaning up the repo before committing.

.. code-block:: bash

    pre-commit run --all-files

Managed Tasks
*************

Updating Schemas
^^^^^^^^^^^^^^^^

There is managed task to automatically pull updated GeoJSON schemas from the :code:`urbanopt-geojson-gem` GitHub
project. A developer can run this command by calling

.. code-block:: bash

    poetry run update_schemas

The developer should run the test suite after updating the schemas to ensure that nothing appears to have broken. Note that the tests do not cover all of the properties and should not be used as proof that everything works with the updated schemas.

Updating Licenses
^^^^^^^^^^^^^^^^^

To apply the copyright/license to all the files, run the following managed task

.. code-block:: bash

    poetry run update_licenses

Adding New Models
-----------------

To add a new model you have to do the following:

1. Define the model's python class: First, create a new python file and class under its respective directory in model_connectors. Follow the patterns of existing classes.

2. Create coupling files: For every model that can be linked to, create a <ModelA>_<ModelB> directory in the couplings directory. The two files ComponentDefinitions.mopt and ConnectStatements.mopt must exist in this directory. See more information on the content of the coupling files below in the *Couplings* sections.

3. Create the instance file: In the templates directory, you must define <ModelName>_Instance.mopt which is the template that instantiates the system in the district model.

See the notes below for more information.

Couplings
*********

A coupling defines the Modelica code necessary for interfacing two specific models, e.g. a time series load and heating indirect ETS.
Each coupling is unique in its requirements:

- what additional components are necessary, for example there might be some sensor between system A and B, or maybe B requires a pump when A is a specific model type
- what ports are connected, for example connecting ports of model A and model B

Thus each coupling must define two template files, ComponentDefinitions.mopt and ConnectStatements.mopt, respectively. These files must be placed in the directory :code:`couplings/templates/<model A>_<model B>/`.
In general, the order of the names should follow the order of system types if you laid out the district system starting with loads on the far left and plants on the far right (e.g. load before ETS, ETS before network, network before plant)

District system
***************

A district system is the model which incorporates all of the models and their couplings.

Templating Flow
***************

When rendering the district system model file, it must:

1. call to_modelica() for each model to generate its Modelica code
2. render the coupling partial templates (ie the Modelica code required for couplings)
3. render the model instance definition (ie the Modelica code which instantiates the model)
4. insert the coupling partials and model instance definitions into the district Modelica file

Refer to `DistrictEnergySystem.mot <https://github.com/urbanopt/geojson-modelica-translator/blob/develop/geojson_modelica_translator/model_connectors/districts/templates/DistrictEnergySystem.mot>`_ and :meth:`~geojson_modelica_translator.model_connectors.districts.district.District` for reference.

Each templating step has access to a particular set of variables, which is defined below.

Summary of Templating Contexts
******************************

Model Definition
^^^^^^^^^^^^^^^^

Each model generates one or more Modelica files to define its model. The templating context is implementation dependent, so refer to its :code:`to_modelica()` method.

Component Definitions
^^^^^^^^^^^^^^^^^^^^^

This is the template which defines new components/variables necessary for a coupling. It has access to:

- :code:`globals`: global variables (those defined in the district.py, such as medium_w = MediumW)
- :code:`coupling`: contains the coupling id, as well as references to the coupled models under their respective types (e.g. coupling.load.id or coupling.network.id). You should append :code:`coupling.id` to any variable identifiers to prevent name collisions. For example, instead of just writing :code:`parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal` you should do :code:`parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_{{ coupling.id }}` as well as any place where you would reference that variable.
- :code:`graph`: an instance of the CouplingGraph class, where all couplings are located. It can provide useful methods for accessing couplings throughout the entire system. Refer to the python class to see what it can do.

Connect Statements
^^^^^^^^^^^^^^^^^^

This is the template which defines connect statements to be inserted into the equation section.

- :code:`globals`
- :code:`coupling`: just like with the component definitions template, you should use the coupling.id to avoid variable name collisions.
- :code:`graph`

Model Instance
^^^^^^^^^^^^^^

This template is used to declare a model instance.

- :code:`globals`
- :code:`graph`
- :code:`couplings`: contains each coupling the model is associated with. For example, if our ETS was coupled to a load and network, couplings would look like :code:`{ load_couplings: [<load coupling>], network_couplings: [<network coupling>] }`. This can be used to access coupling and model ids.
- :code:`model`: contains info about the model instance, including :code:`modelica_type` and :code:`id`. These should be used to define the model, for example :code:`{{ model.modelica_type }} {{ model.id }}(...)`

Running Simulations
-------------------

The GeoJSON to Modelica Translator contains a :code:`ModelicaRunner.run_in_docker(...)` method. It is recommended
to use this method in a python script as it will copy the required files into the correct location. If
desired, a user can run the simulations manually using JModelica (via Docker). Follow the steps below to configure
the runner to work locally.

* Make sure jm_ipython.sh is in your local path.
* After running the :code:`py.test`, go into the :code:`geojson_modelica_translator/modelica/lib/runner/` directory.
* Copy :code:`jmodelica.py` to the :code:`tests/model_connectors/output` directory.
* From the :code:`tests/model_connectors/output` directory, run examples using either of the the following:
    * :code:`jm_ipython.sh jmodelica.py spawn_single.Loads.B5a6b99ec37f4de7f94020090.coupling`
    * :code:`jm_ipython.sh jmodelica.py spawn_single/Loads/B5a6b99ec37f4de7f94020090/coupling.mo`
    * The warnings from the simulations can be ignored. A successful simulation will return Final Run Statistics.
* Install matplotlib package. :code:`pip install matplotlib`
* Visualize the results by inspecting the resulting mat file using BuildingsPy. Run this from the root directory of the GMT.

    .. code-block:: python

        %matplotlib inline
        import os
        import matplotlib.pyplot as plt

        from buildingspy.io.outputfile import Reader

        mat = Reader(os.path.join(
            "tests", "model_connectors", "output", "spawn_single_Loads_B5a6b99ec37f4de7f94020090_coupling_result.mat"),
            "dymola"
        )
        # List off all the variables
        for var in mat.varNames():
            print(var)

        (time1, zn_1_temp) = mat.values("bui.znPerimeter_ZN_3.TAir")
        (_time1, zn_4_temp) = mat.values("bui.znPerimeter_ZN_4.TAir")
        plt.style.use('seaborn-whitegrid')

        fig = plt.figure(figsize=(16, 8))
        ax = fig.add_subplot(211)
        ax.plot(time1 / 3600, zn_1_temp - 273.15, 'r', label='$T_1$')
        ax.plot(time1 / 3600, zn_4_temp - 273.15, 'b', label='$T_4$')
        ax.set_xlabel('time [h]')
        ax.set_ylabel(r'temperature [$^\circ$C]')
        # Simulation is only for 168 hours?
        ax.set_xlim([0, 168])
        ax.legend()
        ax.grid(True)
        fig.savefig('indoor_temp_example.png')


Release Instructions
--------------------

* Bump version to <NEW_VERSION> in setup.py (use semantic versioning).
* Run :code:`pre-commit run --all-files` to ensure code is formatted properly.
* Create a PR against develop into main.
* After main branch passes, merge and checkout the main branch. Build the distribution using the following code:

.. code-block:: bash

    # Remove old dist packages
    rm -rf dist/*
    poetry build

* Run `git tag <NEW_VERSION>`.
* Verify that the files in the dist/* folder have the correct version (no dirty, no sha).
* Run the following to release.

.. code-block:: bash

    poetry publish

* Build and release the documentation.

.. code-block:: bash

    # Build and verify with the following
    cd docs
    poetry run make html
    cd ..

    # release using
    ./docs/publish_docs.sh

* Push the tag to GitHub after everything is published to PyPi, then go to GitHub and add in the CHANGELOG.rst notes into the tagged release and officially release.

.. code-block:: bash

    git push origin <NEW_VERSION>


Code Documentation
------------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   geojson_modelica_translator


.. _Poetry: https://python-poetry.org/docs/
