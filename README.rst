GeoJSON / Modelica Translator
=============================


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

* copyrights task
* Modelica path object to break up between loads and resources, etc.
* Validate remaining schema objects
* handle weather
* install tox
* hook up travis
