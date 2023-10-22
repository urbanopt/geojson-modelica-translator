Change Log
==========

Version 0.6.0 RC2
-----------------

## What's Changed
### Exciting New Features 🎉
* Template initial microgrid subsystem example by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/569
* Microgrid heating by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/586
* Change how ModelicaPaths are built so they also work on Windows computers by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/590
### Other Changes
* initialize empty variable before potential use by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/579
* Include 5G partial model in generation by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/580
* Allow skipping of specific files when cloning a modelica project by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/584
* Add a quick fix for reading gfunction.csv from ghe_id subfolder by @JingWang-CUB in https://github.com/urbanopt/geojson-modelica-translator/pull/589
* Move modelica methods from GMT to modelica-builder by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/591

**Full Changelog**: https://github.com/urbanopt/geojson-modelica-translator/compare/v0.6.0-rc1...v0.6.0-rc2


Version 0.6.0 RC1
-----------------
## What's Changed
### Exciting New Features 🎉
* Enable numberOfIntervals run option by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/562
* Breakout package parser class by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/566
* Add a new GHE district test with new network template models by @JingWang-CUB in https://github.com/urbanopt/geojson-modelica-translator/pull/561
* Add GHE Properties to System Parameter File by @tanushree04 in https://github.com/urbanopt/geojson-modelica-translator/pull/570
* Use `filNam` parameter for TEASER loads and add within parsing to PackageParser by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/574
* Add new `ModelicaProject` class by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/575
* Add Dymola runner by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/577

### Other Changes
* Read correct data from sys-param for microgrid electrical load by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/560
* remove ground loads from system parameter by @tanushree04 in https://github.com/urbanopt/geojson-modelica-translator/pull/576

**Full Changelog**: https://github.com/urbanopt/geojson-modelica-translator/compare/0.5.0...v0.6.0-rc1


Version 0.5.0
-------------
## What's Changed
### Exciting New Features 🎉
* Python 3.11 support by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/518
* Add max_electrical_load to building sys-param data by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/530
* Modifications for GHE by @tanushree04 in https://github.com/urbanopt/geojson-modelica-translator/pull/526
* Add Level 1 - 5G DES system by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/539
* Set SWH peak to 1/10th of space heating or min 5000W by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/542
* Added GHE templates by @JingWang-CUB in https://github.com/urbanopt/geojson-modelica-translator/pull/533
* Add OpenModelica compatibility by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/516
* Modify GHE params by @tanushree04 in https://github.com/urbanopt/geojson-modelica-translator/pull/537
* Enable compile & simulate with OpenModelica in Docker by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/545
### Other Changes
* Specify ports for each time series building in instance template by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/525
* Update license language by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/529
* Add MOS file wrapper and size the 5G mass flow rate by @nllong in https://github.com/urbanopt/geojson-modelica-translator/pull/548
* Fixing borefield test breaks due to schema changes by @JingWang-CUB in https://github.com/urbanopt/geojson-modelica-translator/pull/550
* Updating GHE Parameters: Modifying GHE Parameters schema and example files by @tanushree04 in https://github.com/urbanopt/geojson-modelica-translator/pull/551
* Enhance and expand microgrid templates and code by @vtnate in https://github.com/urbanopt/geojson-modelica-translator/pull/549

## New Contributors
* @tanushree04 made their first contribution in https://github.com/urbanopt/geojson-modelica-translator/pull/526

**Full Changelog**: https://github.com/urbanopt/geojson-modelica-translator/compare/0.4.1...v0.5.0

Version 0.4.1
-------------
## What's Changed
* Cli bugfixing
* Detailed models
* End-of-year updates to GMT docs
* Remove support for 3.7 in development, update development dependencies
* Update copyrights to 2023

Version 0.4.0
-------------
As of version 0.4.0 changes will be published using Github automated formatting at the release itself. Those changes are copied here.

Exciting New Features 🎉
* Redeclare the teaser model to use buildings.media.air medium
* Fmu runner
* Spawn docker named args
* Compile & run with Spawn & Optima
* Microgrid lines
* Add 5G to System Parameters file
* Weather file at top level
* Test with 3.10
* 4G or 5G timeseries in Dymola
Other Changes
* Breakout run in docker command
* Better error message if modelica timeseries files from sdk are not found
* Break out build and simulate tests
* Use Modelica Buildings Library (MBL) v9.0.0
* Point tests to latest mbl release
* Cli less brittle
* Run compilation tasks on CI using spawn Modelica and Optimica
* Update schema.json

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
* Add time series model using mass flow rates and temperatures
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
