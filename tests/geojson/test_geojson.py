# -*- coding: utf-8 -*-

import os
import unittest

from ..context import geojson_modelica_translator  # Do not remove this line
from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson


class GeoJSONTest(unittest.TestCase):

    def test_load_geojson(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        json = UrbanOptGeoJson(filename)
        self.assertIsNotNone(json.data)
        self.assertEqual(len(json.data.features), 4)

    def test_validate(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        json = UrbanOptGeoJson(filename)
        valid, results = json.validate()
        self.assertFalse(valid)
        self.assertEqual(len(results['building']), 3)
        self.assertEqual(results['building'][0]['id'], '5a6b99ec37f4de7f94020090')


if __name__ == '__main__':
    unittest.main()
