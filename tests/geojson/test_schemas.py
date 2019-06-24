# -*- coding: utf-8 -*-

from ..context import geojson_modelica_translator  # Do not remove this line

import unittest

from geojson_modelica_translator.geojson.schemas import Schemas


class SchemasTest(unittest.TestCase):
    def test_load_schemas(self):
        s = Schemas()
        data = s.retrieve('building')
        self.assertEqual(data['title'], 'Building object')

    def test_invalid_retrieve(self):
        s = Schemas()
        with self.assertRaises(Exception) as context:
            s.retrieve('judicate')
        self.assertEqual('Schema for judicate does not exist', str(context.exception))

    def test_validate_schema(self):
        s = Schemas()
        data = s.retrieve('building')

        # verify that the schema can validate an instance with simple parameters
        instance = {
            "id": "5a6b99ec37f4de7f94020090",
            "type": "Building",
            "name": "Medium Office",
            "footprint_area": 17059,
            "footprint_perimeter": 533,
            "building_type": "Office",
            "number_of_stories": 3,
            "system_type": "PTAC with hot water heat",
            "number_of_stories_above_ground": 3,
            "building_status": "Proposed",
            "floor_area": 51177,
            "year_built": 2010
        }
        res = s.validate('building', instance)
        self.assertEqual(len(res), 0)

        # bad system_type
        instance['type'] = 'MagicBuilding'
        res = s.validate('building', instance)
        self.assertIn("'MagicBuilding' is not one of ['Building']", res[0])
        self.assertEqual(len(res), 1)


if __name__ == '__main__':
    unittest.main()
