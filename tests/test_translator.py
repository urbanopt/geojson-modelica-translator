# -*- coding: utf-8 -*-

from .context import geojson_modelica_translator  # Do not remove this line

import os
import unittest

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator


class GeoJSONTranslatorTest(unittest.TestCase):
    def test_init(self):
        gj = GeoJSONTranslatorTest()
        self.assertIsNotNone(gj)

    def test_from_geojson(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        gj = GeoJsonModelicaTranslator.from_geojson(filename)

        self.assertEqual(len(gj.buildings), 3)

    def test_scaffold(self):
        gj = GeoJsonModelicaTranslator()
        p = os.path.abspath(os.path.join('tests', 'output', 'test_01'))
        gj.scaffold_directory(p)

        # check the existence of all the member variables
        self.assertEqual(gj.loads_dir, os.path.join(p, 'Loads'))
        self.assertEqual(gj.substations_dir, os.path.join(p, 'Substations'))
        self.assertEqual(gj.plants_dir, os.path.join(p, 'Plants'))
        self.assertEqual(gj.districts_dir, os.path.join(p, 'Districts'))
        self.assertEqual(gj.resources_dir, os.path.join(p, 'Resources'))
        self.assertEqual(gj.resources_data_root_dir, os.path.join(p, 'Resources', 'Data'))
        self.assertEqual(gj.resources_data_loads_dir, os.path.join(p, 'Resources', 'Data', 'Loads'))
        self.assertEqual(gj.resources_data_districts_dir, os.path.join(p, 'Resources', 'Data', 'Districts'))
        self.assertEqual(gj.resources_data_weather_dir, os.path.join(p, 'Resources', 'Data', 'Weather'))

    def test_to_modelica(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        gj.to_modelica('tests/output/geojson_1')
        self.assertTrue(os.path.exists(gj.loads_dir))


if __name__ == '__main__':
    unittest.main()
