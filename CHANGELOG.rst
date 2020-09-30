Change Log
==========

Version 0.2.0
--------------------------
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
