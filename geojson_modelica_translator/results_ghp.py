# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from buildingspy.io.outputfile import Reader


class ResultsModelica:
    """Results from Modelica Project Simulation"""

    def __init__(self, modelica_project):
        self._modelica_project = Path(modelica_project).resolve()

    def calculate_results(self):
        # Extract the project name from the modelica_project path
        project_name = self._modelica_project.name

        # Construct the path for the .mat file
        result_mat_file = (
            self._modelica_project
            / f"{project_name}.Districts.DistrictEnergySystem_results"
            / f"{project_name}.Districts.DistrictEnergySystem_res.mat"
        )

        # Print the resulting path for debugging purposes
        print(f"Generated path: {result_mat_file}")

        if result_mat_file.exists():
            print(f"The path {result_mat_file} exists.")
        else:
            print(f"The path {result_mat_file} does not exist.")
            return

        # Initialize the Reader object
        results = Reader(result_mat_file, "dymola")

        # Define patterns and output variable names
        patterns = {
            "heating_electric_power": r"^TimeSerLoa_\w+\.PHea$",
            "cooling_electric_power": r"^TimeSerLoa_\w+\.PCoo$",
            "pump_power": r"^TimeSerLoa_\w+\.PPum$",
            "ets_pump_power": r"^TimeSerLoa_\w+\.PPumETS$",
            "Heating system capacity": r"^TimeSerLoa_\w+\.ets.QHeaWat_flow_nominal$",
            "Cooling system capacity": r"^TimeSerLoa_\w+\.ets.QChiWat_flow_nominal$",
            "electrical_power_consumed": "pumDis.P",
        }

        key_value_pairs = {}
        time_values = None

        for name, pattern in patterns.items():
            for var in results.varNames(pattern):
                time, values = results.values(var)  # Unpack the tuple
                if time_values is None:
                    time_values = time.tolist()  # Initialize time_values from the first variable
                key_value_pairs[var] = values.tolist()

        # Convert seconds to timezone-aware datetime and adjust year to 2017
        def adjust_year(dt):
            return dt.replace(year=2017)

        # Convert timestamps to timezone-aware datetime objects in UTC
        time_values = [datetime.fromtimestamp(t, tz=timezone.utc) for t in time_values]
        adjusted_time_values = [adjust_year(dt) for dt in time_values]

        data_for_df = {
            "Datetime": adjusted_time_values,
            "TimeInSeconds": [int(dt.timestamp()) for dt in adjusted_time_values],
        }

        for var, values in key_value_pairs.items():
            if len(values) < len(adjusted_time_values):
                values.extend([None] * (len(adjusted_time_values) - len(values)))
            elif len(values) > len(adjusted_time_values):
                trimmed_values = values[: len(adjusted_time_values)]
                data_for_df[var] = trimmed_values
            else:
                data_for_df[var] = values

        df_values = pd.DataFrame(data_for_df)

        # Convert 'Datetime' to datetime and set it as index
        df_values["Datetime"] = pd.to_datetime(df_values["Datetime"])
        df_values = df_values.set_index("Datetime")

        # Resample to 1 hour data, taking the first occurrence for each interval
        df_resampled = df_values.resample("1h").first().reset_index()

        # Format datetime to desired format
        df_resampled["Datetime"] = df_resampled["Datetime"].dt.strftime("%m/%d/%Y %H:%M")

        # Interpolate only numeric columns
        numeric_columns = df_resampled.select_dtypes(include=["number"]).columns
        df_resampled[numeric_columns] = df_resampled[numeric_columns].interpolate(method="linear", inplace=False)

        # Check if the number of rows is not equal to 8760 (hourly) or 8760 * 4 (15-minute)
        if df_resampled.shape[0] != 8760 or df_resampled.shape[0] != 8760 * 4:
            print("Data length is incorrect. Expected 8760 (hourly) or 8760 * 4 (15-minute) entries.")

        # Define patterns with placeholders
        patterns = {
            "heating_electric_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PHea$",
            "cooling_electric_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PCoo$",
            "pump_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PPum$",
            "ets_pump_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PPumETS$",
            "heating_system_capacity_#{building_id}": r"^TimeSerLoa_(\w+)\.ets.QHeaWat_flow_nominal$",
            "cooling_system_capacity_#{building_id}": r"^TimeSerLoa_(\w+)\.ets.QChiWat_flow_nominal$",
            "electrical_power_consumed": "pumDis.P",
        }

        # Function to rename columns based on patterns
        def rename_column(col_name):
            for key, pattern in patterns.items():
                match = re.match(pattern, col_name)
                if match:
                    if key == "electrical_power_consumed":
                        return key
                    try:
                        building_id = match.group(1)
                        return key.replace("#{building_id}", building_id)
                    except IndexError:
                        print(f"Error: Column '{col_name}' does not match expected pattern.")
                        return col_name
            # If no pattern matches, return the original column name
            return col_name

        # Rename columns
        df_resampled.columns = [rename_column(col) for col in df_resampled.columns]

        # Define the path to save the CSV file
        results_dir = self._modelica_project / f"{project_name}.Districts.DistrictEnergySystem_results"
        csv_file_path = results_dir / f"{project_name}.Districts.DistrictEnergySystem_result.csv"

        # Ensure the results directory exists
        results_dir.mkdir(parents=True, exist_ok=True)

        df_resampled.to_csv(csv_file_path, index=False)

        print(f"Results saved at: {csv_file_path}")
