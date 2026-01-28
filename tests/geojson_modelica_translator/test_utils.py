# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import unittest
from pathlib import Path

from geojson_modelica_translator.utils import ModelicaPath


class ModelicaPathTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(__file__).parent / "output"

    def test_properties(self):
        mp = ModelicaPath("Loads", root_dir=None)
        assert mp.files_dir == "Loads"
        assert mp.resources_dir == "Resources/Data/Loads"

    def test_single_sub_resource(self):
        root_dir = self.output_dir / "modelica_path_01"
        ModelicaPath("RandomContainer", root_dir, overwrite=True)
        assert (Path(root_dir) / "RandomContainer").exists()
        assert (Path(root_dir) / "Resources" / "Data" / "RandomContainer").exists()
