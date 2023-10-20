# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import unittest

from geojson_modelica_translator.utils import ModelicaPath


class ModelicaPathTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")

    def test_properties(self):
        mp = ModelicaPath("Loads", root_dir=None)
        self.assertEqual(mp.files_dir, "Loads")
        self.assertEqual(mp.resources_dir, "Resources/Data/Loads")

    def test_single_sub_resource(self):
        root_dir = os.path.join(self.output_dir, "modelica_path_01")
        ModelicaPath("RandomContainer", root_dir, overwrite=True)
        self.assertTrue(os.path.exists(os.path.join(root_dir, "RandomContainer")))
        self.assertTrue(os.path.exists(os.path.join(root_dir, "Resources", "Data", "RandomContainer")))
