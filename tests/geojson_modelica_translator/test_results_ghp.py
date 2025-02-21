# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md


from pathlib import Path

import pandas as pd

from geojson_modelica_translator.results_ghp import ResultsModelica
from tests.base_test_case import TestCaseBase


class ResultsTest(TestCaseBase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"

    def test_result(self):
        # Construct the path to the Modelica project directory
        modelica_path = Path(self.data_dir) / "modelica_5"
        modelica_path = modelica_path.resolve()

        # Construct the path to the CSV file
        csv_file_path = (
            modelica_path
            / "modelica_5.Districts.DistrictEnergySystem_results"
            / "modelica_5.Districts.DistrictEnergySystem_result.csv"
        )

        # Delete csv path if it exists
        if csv_file_path.exists():
            csv_file_path.unlink()

        result = ResultsModelica(modelica_path)
        result.calculate_results()

        # Check if the CSV file exists
        assert csv_file_path.exists(), f"File does not exist at path: {csv_file_path}"

        # Read the CSV file into a DataFrame
        csv_data = pd.read_csv(csv_file_path)

        assert "Datetime" in csv_data.columns, "The 'Datetime' column is missing from the CSV file."

        assert "heating_electric_power_d55aa383" in csv_data.columns, (
            "The heating_electric_power column is missing from the CSV file."
        )

        assert "pump_power_3da62a1d" in csv_data.columns, "The pump_power column is missing from the CSV file."

        assert "electrical_power_consumed" in csv_data.columns, (
            "The electrical_power_consumed column is missing from the CSV file."
        )

    def test_result_multiple_ghp(self):
        # Construct the path to the Modelica project directory
        modelica_path = Path(self.data_dir) / "modelica_multiple"
        modelica_path = modelica_path.resolve()

        # Construct the path to the CSV file
        csv_file_path = (
            modelica_path
            / "modelica_multiple.Districts.DistrictEnergySystem_results"
            / "modelica_multiple.Districts.DistrictEnergySystem_result.csv"
        )

        # Delete csv path if it exists
        if csv_file_path.exists():
            csv_file_path.unlink()

        result = ResultsModelica(modelica_path)
        result.calculate_results()

        # Check if the CSV file exists
        assert csv_file_path.exists(), f"File does not exist at path: {csv_file_path}"

        # Read the CSV file into a DataFrame
        csv_data_multiple = pd.read_csv(csv_file_path)

        assert "Datetime" in csv_data_multiple.columns, "The 'Datetime' column is missing from the CSV file."

        # Check if any columns contain the "heating_electric_power_" substring
        heating_electric_power = [col for col in csv_data_multiple.columns if "heating_electric_power_" in col]

        assert heating_electric_power, "No columns with 'heating_electric_power' found in the CSV file."

        assert len(heating_electric_power) == 13, (
            f"Expected 13 columns with 'heating_electric_power_' but found {len(heating_electric_power)}."
        )

        pump_power = [col for col in csv_data_multiple.columns if "pump_power_" in col]

        # Assert that there is at least one column with the substring
        assert pump_power, "No columns with 'pump_power' found in the CSV file."

        assert len(pump_power) == 26, f"Expected 26 columns with 'pump_power' but found {len(pump_power)}."

        assert "electrical_power_consumed" in csv_data_multiple.columns, (
            "The electrical_power_consumed column is missing from the CSV file."
        )
