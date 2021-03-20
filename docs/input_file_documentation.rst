.. _documentation:

Input File Documentation
========================

There are two input files that need to be defined to use the GeoJSON to Modelica Translator: a GeoJSON file and a System Parameters file.

GeoJSON Documentation
---------------------

There are multiple GeoJSON schemas that are used to define the expected properties of GeoJSON
features. The reason is because the only element that we are leveraging in GeoJSON is the 'properties'
field; all the other fields are protected GeoJSON fields. Presently only the building_properties are
leveraged in the GMT; however, the thermal_connector_properties and thermal_junction_properties will
eventually be used.

Building Properties
*******************

.. jsonschema:: ../geojson_modelica_translator/geojson/data/schemas/building_properties.json

System Parameters Schema
------------------------

.. jsonschema:: ../geojson_modelica_translator/system_parameters/schema.json
