Change Log
==========

Version 0.3.0
-------------
* Use MBL v9 (current master branch) for all models. Note that JModelica no longer works with this version. User must now use either Dymola or Optimica. A new solution is forthcoming.
* Update unit tests to break out building the tests and running the tests.

Version 0.2.3
-------------
* Add GMT Lib methods for Level 1 translation of Modelica-templated objects (for microgrid).
* Use MBL v9 (current master branch) for GMT Lib. The DES models still require the usage of the `issue2204_gmt_mbl` branch.
* Updated Jinja and Sphinx dependencies. Jinja is now a required dependency (no longer a testing dependency).
* Fix bug in CLI where commands only work in Unix-like operating systems, not Windows
* Fix bug in TEASER model for four-element RC models.
* Fix bug in TEASER infinite heating/cooling coupling template.

Version 0.2.2
-------------
* Fix bug in CLI which required the user to be in a specific directory to run. Updated CLI is more flexible.
* Update documentation.

Version 0.2.1
-------------
* New command line interface (CLI) for scaffolding project using results of URBANopt SDK's OpenStudio results
* New script for converting CSV file into Modelica mos file
* Cleanup of System Parameter Schema including renaming elements, adding definitions, and adding units
* Redesign the couplings and remove redundant model connector files
* Promote DES configuration variables to be accessible in the System Parameter file
* Extended flexibility of setting parameter values programmatically for Teaser, TimeSeries, and Spawn building load models models
* Upgrade to TEASER 0.7.5
* Upgrade to MBL 2.1.0
* Migrate to Poetry for development
* Add regression testing to full district energy system
* Auto-layout of templated components. This is a work in progress and the next version will include "pooling" of components.

Version 0.2.0
-------------
* Add ETS data for indirect cooling to system parameters schema
* Add district system example
* Add time series model using massflow rates and temperatures
* Add district heating (1GDH and 4GDH) and heating indirect ETS
* Add district cooling (4GDC) and cooling indirect ETS
* Add distribution network
* Update scaffolding to allow for mixed models
* Create initial documentation

Version 0.1.0
-------------

This is the initial release of the package and includes the following functionality:

* Initial implementation of a ModelicaRunner to call a Docker container to run the model.
* Create an RC model using Modelica 3.2.x, Modelica Buildings Library 7.0 and TEASER 0.7.2.
* Create a Spawn-based models which loads an IDF file.
