# # :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# # See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


# import shutil
# import unittest
# from pathlib import Path

# from geojson_modelica_translator.scaffold import Scaffold


# class ScaffoldTest(unittest.TestCase):
#     def setUp(self):
#         self.data_dir = Path(__file__).parent / "data"
#         self.output_dir = Path(__file__).parent / "output"
#         if self.output_dir.exists():
#             shutil.rmtree(self.output_dir)
#         self.output_dir.mkdir(exist_ok=True)

#     def test_scaffold(self):
#         scaffold = Scaffold(self.output_dir, "scaffold_01", overwrite=True)
#         scaffold.create()
#         assert (Path(self.output_dir) / "scaffold_01" / "Resources" / "Scripts" / "Loads" / "Dymola").exists()

#     # def test_add_building(self):
#     #     scaffold = Scaffold(self.output_dir, "scaffold_02", overwrite=True)
#     #     load_1 = FakeConnector(None)
#     #     self.assertIsInstance(load_1, building_base)
#     #     scaffold.loads.append(load_1)
#     #     scaffold.create()
#     #
#     #     r = scaffold.to_modelica()
#     #     self.assertTrue(r)
