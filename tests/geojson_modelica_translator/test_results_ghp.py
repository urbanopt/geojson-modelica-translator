# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


import unittest
from pathlib import Path

import pandas as pd

from geojson_modelica_translator.results_ghp import ResultsModelica


class ResultsTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"

    def test_result(self):
        # Construct the path to the Modelica project directory
        modelica_path = Path(self.data_dir) / "modelica_5"
        modelica_path = modelica_path.resolve()

        result = ResultsModelica(modelica_path)
        result.calculate_results()

        # Construct the path to the CSV file
        csv_file_path = (
            modelica_path
            / "modelica_5.Districts.DistrictEnergySystem_results"
            / "modelica_5.Districts.DistrictEnergySystem_result.csv"
        )

        # Check if the CSV file exists
        assert csv_file_path.exists(), f"File does not exist at path: {csv_file_path}"

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        assert "Datetime" in df.columns, "The 'Datetime' column is missing from the CSV file."

        assert "heating_electric_power_d55aa383" in df.columns, "The heating_electric_power column is missing from the CSV file."

        assert "pump_power_3da62a1d" in df.columns, "The pump_power column is missing from the CSV file."

        assert "electrical_power_consumed" in df.columns, "The electrical_power_consumed column is missing from the CSV file."
