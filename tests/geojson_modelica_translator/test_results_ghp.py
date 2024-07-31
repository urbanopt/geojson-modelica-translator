# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


import shutil
import unittest
import os
from pathlib import Path

from geojson_modelica_translator.results_ghp import ResultsModelica

class ResultsTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"
        # self.output_dir = Path(__file__).parent / "output"
        # if self.output_dir.exists():
        #     shutil.rmtree(self.output_dir)
        # self.output_dir.mkdir(exist_ok=True)

    def test_result(self):

        # Construct the path to the Modelica project directory
        modelica_path = Path(self.data_dir) / "modelica_5"
        modelica_path = modelica_path.resolve()
        
        result = ResultsModelica(modelica_path)
        result.calculate_results()

        # Construct the path to the CSV file
        csv_file_path = modelica_path / "modelica_5.Districts.DistrictEnergySystem_results" / "modelica_5.Districts.DistrictEnergySystem_result.csv"
        print(csv_file_path)

        # Check if the CSV file exists
        assert csv_file_path.exists(), f"File does not exist at path: {csv_file_path}"