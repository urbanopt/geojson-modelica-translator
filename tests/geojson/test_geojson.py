# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import unittest

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    GeoJsonValidationError,
    UrbanOptGeoJson
)


class GeoJSONTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_load_geojson(self):
        filename = os.path.join(self.data_dir, "geojson_1.json")
        json = UrbanOptGeoJson(filename)
        self.assertIsNotNone(json.data)
        self.assertEqual(len(json.data.features), 4)

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            UrbanOptGeoJson(fn)
        self.assertEqual(
            f"URBANopt GeoJSON file does not exist: {fn}", str(exc.exception)
        )

    def test_valid_instance(self):
        """No exception should be raised when the geojson file is valid"""
        filename = os.path.join(self.data_dir, "geojson_1.json")
        UrbanOptGeoJson(filename)

    def test_validate(self):
        filename = os.path.join(self.data_dir, "geojson_1_invalid.json")
        with self.assertRaises(GeoJsonValidationError) as ctx:
            UrbanOptGeoJson(filename)

        self.assertIn("is not valid under any of the given schemas", str(ctx.exception))
