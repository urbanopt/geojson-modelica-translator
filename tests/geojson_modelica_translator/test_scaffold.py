# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


import os
import shutil
import unittest

from geojson_modelica_translator.scaffold import Scaffold


class ScaffoldTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def test_scaffold(self):
        scaffold = Scaffold(self.output_dir, "scaffold_01", overwrite=True)
        scaffold.create()
        self.assertTrue(
            os.path.exists(os.path.join(self.output_dir, "scaffold_01", "Resources", "Scripts", "Loads", "Dymola"))
        )

    # def test_add_building(self):
    #     scaffold = Scaffold(self.output_dir, "scaffold_02", overwrite=True)
    #     load_1 = FakeConnector(None)
    #     self.assertIsInstance(load_1, building_base)
    #     scaffold.loads.append(load_1)
    #     scaffold.create()
    #
    #     r = scaffold.to_modelica()
    #     self.assertTrue(r)
