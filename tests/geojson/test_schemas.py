# # :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# # See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

# import unittest

# import pytest

# from geojson_modelica_translator.geojson.schemas import Schemas


# class SchemasTest(unittest.TestCase):
#     def test_load_schemas(self):
#         s = Schemas()
#         data = s.retrieve("building")
#         assert data["title"] == "URBANopt Building"

#     def test_invalid_retrieve(self):
#         s = Schemas()
#         with pytest.raises(NameError) as context:
#             s.retrieve("judicate")
#         assert "Schema for judicate does not exist" in str(context.value)

#     def test_validate_schema(self):
#         s = Schemas()
#         s.retrieve("building")

#         # verify that the schema can validate an instance with simple parameters
#         instance = {
#             "id": "5a6b99ec37f4de7f94020090",
#             "type": "Building",
#             "name": "Medium Office",
#             "footprint_area": 17059,
#             "footprint_perimeter": 533,
#             "building_type": "Office",
#             "number_of_stories": 3,
#             "system_type": "PTAC with district hot water",
#             "number_of_stories_above_ground": 3,
#             "building_status": "Proposed",
#             "floor_area": 51177,
#             "year_built": 2010,
#         }
#         res = s.validate("building", instance)
#         assert len(res) == 0

#         # bad system_type
#         instance["type"] = "MagicBuilding"
#         res = s.validate("building", instance)
#         assert "'MagicBuilding' is not one of ['Building']" in res[0]
#         assert len(res) == 1
