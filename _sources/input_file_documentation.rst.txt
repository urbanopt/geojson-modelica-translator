.. _documentation:

Input File Documentation
========================

There are two input files that need to be defined to use the GeoJSON to Modelica Translator: a GeoJSON file and
a System Parameters file.

GeoJSON Documentation
---------------------

Presently only the building_properties.json of URBANopt's GeoJSON schemas is leveraged in the GMT.

Building Properties
*******************

Bolded elements are required fields.

.. jsonschema:: ../geojson_modelica_translator/geojson/data/schemas/building_properties.json

System Parameters Schema
------------------------

Bolded elements are required fields.

.. jsonschema:: ../geojson_modelica_translator/system_parameters/schema.json
