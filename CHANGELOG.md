# Change Log

## Version 0.10.0

### Exciting New Features 🎉

* Expose skipping weather download by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/706>
* Enable selecting output variables from Modelica simulation by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/707>
* Add capability to pass Modelica flags to the GMT CLI by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/709>
* More params by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/703>
* Add autosizing flags to sys-param values that may be autosized by TN/GHED by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/708>
* Add new heat pump ETS to 5G loads by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/710>
* Require autosize flags in sys-param files by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/712>

## Version 0.9.3

### Exciting New Features 🎉

* Add horizontal pipe pressure drop to sys-params by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/700>

### Other Changes

* Expand capability of geojson class by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/694>
* Cleanup Lingering RST Doc Extensions by @mitchute in <https://github.com/urbanopt/geojson-modelica-translator/pull/701>

## Version 0.9.2

### Exciting New Features 🎉

* Change thermal connectors to be measured in meters by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/697>

### Other Changes

* Clean up matching district generation types by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/690>
* Handle all-caps soil-temp stations, like Frankfurt by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/689>
* Remove `is_ghe_start_loop` from test geojson files by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/688>

**Full Changelog**: <https://github.com/urbanopt/geojson-modelica-translator/compare/v0.9.1...v0.9.2>

## Version 0.9.1

* Fix incorrect link to documentation site by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/684>
* Use pre-made GHA workflow to publish docs by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/685>

## Version 0.9.0

### Exciting New Features 🎉

* Upgrade OpenModelica & MBL by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/641>
* Support Python 3.13 by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/676>

### Other Changes

* Putting GHEs downstream of the buildings by @JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/677>
* Order horizontal piping correctly between buildings by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/679>
* Allow skipping GeoJSON validation by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/681>
* Switch to MkDocs by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/664>

**Full Changelog**: <https://github.com/urbanopt/geojson-modelica-translator/compare/v0.8.0...v0.9.0>

## Version 0.8.0

### Exciting New Features 🎉

* Add default cop values for 5G district heat pump efficiencies by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/640>
* Support international weather locations by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/654>
* Support multiple GHEs in a single district by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/644>
* Adds method to process modelica results by @tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/646>
* Simplify sys params to closer match reality by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/659>
* Templates and tests for horizontal piping modeling by @JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/627>
* Support single building DES templates by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/670>

### Other Changes

* Improve cli typing & validation by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/662>
* Add detail to Docker setup docs for Windows users by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/643>
* Use the correct ETS heat pump COP by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/642>
* Use feature ids in load names instead of simple_uuid by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/652>
* Remove alfalfa from conftest.py by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/665>
* Update version of Jinja by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/667>
* Clean up sys-param code that reads parameters by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/668>

**Full Changelog**: <https://github.com/urbanopt/geojson-modelica-translator/compare/v0.7.0...v0.8.0>

## Version 0.7.0

### Exciting New Features 🎉

* Rename new modelica models to clarify MBL version by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/618>
* Minor improvements to the CLI by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/620>
* Enable more detail when specifying district types by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/622>
* Force a dummy value for SHW in modelica loads even if not present by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/626>

### Other Changes

* Move README and CHANGELOG to markdown and update deployment notes by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/615>
* Update instructions for releasing documentation publicly by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/617>
* Specify units of GHE flow_rate by @vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/623>
* Code documentation cleanup by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/631>
* Expose borehole variables by @nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/630>

**Full Changelog**: <https://github.com/urbanopt/geojson-modelica-translator/compare/v0.6.0...v0.7.0>

## Version 0.6.0

### Exciting New Features 🎉

* Python 311 by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/518>
* add max_electrical_load to building sys-param data by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/530>
* Modifications for GHE by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/526>
* Add Level 1 5G DES system by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/539>
* Set SWH peak to 1/10th of space heating or min 5000W by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/542>
* Added GHE templates - Issue511 by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/533>
* Add MOS file wrapper and size the 5G mass flow rate by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/548>
* Add OpenModelica compatibility by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/516>
* Modify GHE params by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/537>
* Fixing borefield test breaks due to schema changes by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/550>
* Updating GHE Parameters: Modifying GHE Parameters schema and example files by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/551>
* Enable compile & simulate with OpenModelica in Docker by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/545>
* Enhance and expand microgrid templates and code by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/549>
* Enable numberOfIntervals run option by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/562>
* Breakout package parser class by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/566>
* Add a new GHE district test with new network template models by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/561>
* Add GHE Properties to System Parameter File by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/570>
* Use `filNam` parameter for TEASER loads and add within parsing to PackageParser by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/574>
* Add new `ModelicaProject` class by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/575>
* Add Dymola runner by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/577>
* Template initial microgrid subsystem example by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/569>
* Microgrid heating by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/586>
* Change how ModelicaPaths are built so they also work on Windows computers by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/590>
* Refactoring and enhancing to support multiple GHEs in a single district by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/601>
* Replace shell script with call directly to docker by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/607>
* Implement a PyPI release workflow by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/603>
* Support Python 3.12 by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/593>
* Add district nominal pump head to system parameters file by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/610>

### Other Changes

* specify ports for each time series building in instance template by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/525>
* Update license language by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/529>
* Read correct data from sys-param for microgrid electrical load by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/560>
* Prep for prerelease 0.6.0 by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/578>
* initialize empty variable before potential use by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/579>
* Include 5G partial model in generation by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/580>
* Allow skipping of specific files when cloning a modelica project by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/584>
* Add a quick fix for reading gfunction.csv from ghe_id subfolder by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/589>
* Move modelica methods from GMT to modelica-builder by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/591>
* Add model for controlled distribution loop mass flow rate by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/594>
* Allow user to specify Modelica load filename by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/599>
* Decouple gain for distribution and ghx mass flow rates by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/600>
* Closed-loop changes to existing test_single_ghe test by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/597>
* Update documentation for version 0.6.0 by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/592>
* Use Ubuntu 20 and fix CHP model by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/611>

**Full Changelog**:
<https://github.com/urbanopt/geojson-modelica-translator/compare/v0.5.0...v0.6.0>

## Version 0.5.0

### Exciting New Features 🎉

* Python 3.11 support by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/518>
* Add max_electrical_load to building sys-param data by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/530>
* Modifications for GHE by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/526>
* Add Level 1 - 5G DES system by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/539>
* Set SWH peak to 1/10th of space heating or min 5000W by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/542>
* Added GHE templates by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/533>
* Add OpenModelica compatibility by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/516>
* Modify GHE params by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/537>
* Enable compile & simulate with OpenModelica in Docker by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/545>

### Other Changes

* Specify ports for each time series building in instance template by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/525>
* Update license language by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/529>
* Add MOS file wrapper and size the 5G mass flow rate by \@nllong in <https://github.com/urbanopt/geojson-modelica-translator/pull/548>
* Fixing borefield test breaks due to schema changes by \@JingWang-CUB in <https://github.com/urbanopt/geojson-modelica-translator/pull/550>
* Updating GHE Parameters: Modifying GHE Parameters schema and example files by \@tanushree04 in <https://github.com/urbanopt/geojson-modelica-translator/pull/551>
* Enhance and expand microgrid templates and code by \@vtnate in <https://github.com/urbanopt/geojson-modelica-translator/pull/549>

### New Contributors

* \@tanushree04 made their first contribution in <https://github.com/urbanopt/geojson-modelica-translator/pull/526>

**Full Changelog**:
<https://github.com/urbanopt/geojson-modelica-translator/compare/0.4.1...v0.5.0>

## Version 0.4.1

### What\'s Changed

* Cli bug fixes
* Detailed models
* End-of-year updates to GMT docs
* Remove support for 3.7 in development, update development dependencies
* Update copyrights to 2023

## Version 0.4.0

As of version 0.4.0 changes will be published using Github automated formatting at the release itself. Those changes are copied here.

### Exciting New Features 🎉

* Redeclare the teaser model to use buildings.media.air medium
* Fmu runner
* Spawn docker named args
* Compile & run with Spawn & Optima
* Microgrid lines
* Add 5G to System Parameters file
* Weather file at top level
* Test with 3.10
* 4G or 5G timeseries in Dymola

### Other Changes

* Breakout run in docker command
* Better error message if modelica timeseries files from sdk are not found
* Break out build and simulate tests
* Use Modelica Buildings Library (MBL) v9.0.0
* Point tests to latest mbl release
* Cli less brittle
* Run compilation tasks on CI using spawn Modelica and Optimica
* Update schema.json

## Version 0.3.0

* Use MBL v9 (current master branch) for all models. Note that JModelica no longer works with this version. User must now use either Dymola or Optimica. A new solution is forthcoming.
* Update unit tests to break out building the tests and running the tests.

## Version 0.2.3

* Add GMT Lib methods for Level 1 translation of Modelica-templated objects (for microgrid).
* Use MBL v9 (current master branch) for GMT Lib. The DES models still require the usage of the `issue2204_gmt_mbl` branch.
* Updated Jinja and Sphinx dependencies. Jinja is now a required dependency (no longer a testing dependency).
* Fix bug in CLI where commands only work in Unix-like operating systems, not Windows
* Fix bug in TEASER model for four-element RC models.
* Fix bug in TEASER infinite heating/cooling coupling template.

## Version 0.2.2

* Fix bug in CLI which required the user to be in a specific directory to run. Updated CLI is more flexible.
* Update documentation.

## Version 0.2.1

* New command line interface (CLI) for scaffolding project using results of URBANopt SDK\'s OpenStudio results
* New script for converting CSV file into Modelica mos file.
* Cleanup of System Parameter Schema including renaming elements, adding definitions, and adding units
* Redesign the couplings and remove redundant model connector files
* Promote DES configuration variables to be accessible in the System Parameter file
* Extended flexibility of setting parameter values programmatically for Teaser, TimeSeries, and Spawn building load models models
* Upgrade to TEASER 0.7.5
* Upgrade to MBL 2.1.0
* Migrate to Poetry for development
* Add regression testing to full district energy system
* Auto-layout of templated components. This is a work in progress and  the next version will include \"pooling\" of components.

## Version 0.2.0

* Add ETS data for indirect cooling to system parameters schema
* Add district system example
* Add time series model using mass flow rates and temperatures
* Add district heating (1GDH and 4GDH) and heating indirect ETS
* Add district cooling (4GDC) and cooling indirect ETS
* Add distribution network
* Update scaffolding to allow for mixed models
* Create initial documentation

## Version 0.1.0

This is the initial release of the package and includes the following
functionality:

* Initial implementation of a ModelicaRunner to call a Docker container to run the model.
* Create an RC model using Modelica 3.2.x, Modelica Buildings Library 7.0 and TEASER 0.7.2.
* Create a Spawn-based models which loads an IDF file.
