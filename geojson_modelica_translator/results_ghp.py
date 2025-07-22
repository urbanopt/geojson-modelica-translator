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


        if result_mat_file.exists():
            print(f"The path {result_mat_file} exists.")
        else:
            print(f"The path {result_mat_file} does not exist.")
            return

        # Initialize the Reader object
        results = Reader(result_mat_file, "dymola")

        # Unified patterns with building ID
        patterns = {
            "heating_electric_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PHea$",
            "cooling_electric_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PCoo$",
            "pump_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PPum$",
            "ets_pump_power_#{building_id}": r"^TimeSerLoa_(\w+)\.PPumETS$",
            "heating_system_capacity_#{building_id}": r"^TimeSerLoa_(\w+)\.ets.QHeaWat_flow_nominal$",
            "cooling_system_capacity_#{building_id}": r"^TimeSerLoa_(\w+)\.ets.QChiWat_flow_nominal$",
            "electrical_power_consumed": r"pumDis.P",
        }

        key_value_pairs = {}
        time_values = None

        # Helper: Rename column using building ID
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
            return col_name

        # Collect values and rename
        for key, pattern in patterns.items():
            matching_vars = results.varNames(pattern)
            print(f"\nPattern for '{key}' matched: {matching_vars}")
            for var in matching_vars:
                try:
                    time, values = results.values(var)
                    if time_values is None:
                        time_values = time.tolist()
                    renamed = rename_column(var)
                    key_value_pairs[renamed] = values.tolist()
                except Exception as e:
                    print(f"Error reading values for {var}: {e}")

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
                values = values[: len(adjusted_time_values)]
            data_for_df[var] = values

        df_values = pd.DataFrame(data_for_df)

        # Set Datetime as index
        df_values["Datetime"] = pd.to_datetime(df_values["Datetime"])
        df_values = df_values.set_index("Datetime")

        # Resample to hourly and reset index
        df_resampled = df_values.resample("1h").first().reset_index()

        # Format datetime
        df_resampled["Datetime"] = df_resampled["Datetime"].dt.strftime("%m/%d/%Y %H:%M")

        # Interpolate numeric columns
        numeric_columns = df_resampled.select_dtypes(include=["number"]).columns
        df_resampled[numeric_columns] = df_resampled[numeric_columns].interpolate(method="linear", inplace=False)

        # Print shape check
        if df_resampled.shape[0] != 8760 and df_resampled.shape[0] != 8760 * 4:
            print("Data length is incorrect. Expected 8760 (hourly) or 8760*4 (15-min) entries.")

        # Save CSV
        results_dir = self._modelica_project / f"{project_name}.Districts.DistrictEnergySystem_results"
        csv_file_path = results_dir / f"{project_name}.Districts.DistrictEnergySystem_result.csv"
        results_dir.mkdir(parents=True, exist_ok=True)
        df_resampled.to_csv(csv_file_path, index=False)

        print(f"Results saved at: {csv_file_path}")