# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


import unittest
from pathlib import Path

import pandas as pd

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
        csv_file_path = (
            modelica_path
            / "modelica_5.Districts.DistrictEnergySystem_results"
            / "modelica_5.Districts.DistrictEnergySystem_result.csv"
        )

        # Check if the CSV file exists
        assert csv_file_path.exists(), f"File does not exist at path: {csv_file_path}"

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        # Check if the 'Datetime' column exists
        assert "Datetime" in df.columns, "The 'Datetime' column is missing from the CSV file."

        # TO DO uncomment when input arguments are set for 1 year simulation with 15 min intervals
        # Check the length of the 'Datetime' column
        expected_length = 35_040  # Number of 15-minute intervals in a standard year
        # assert len(df['Datetime']) == expected_length, f"Expected {expected_length} rows but found {len(df['Datetime'])}."
