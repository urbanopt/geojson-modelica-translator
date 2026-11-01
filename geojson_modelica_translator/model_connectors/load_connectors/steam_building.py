# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import re

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.load_connectors.load_base import LoadBase
from geojson_modelica_translator.utils import ModelicaPath

# Column of the space heating load in GMT time-series (MOS) load files:
# 0 = time (s), 1 = cooling (W, negative), 2 = space heating (W), 3 = water heating (W)
MOS_HEATING_COLUMN = 2


def _mos_separator(line: str) -> str:
    """Field separator of a MOS data row: ';', ',' or whitespace."""
    for separator in (";", ","):
        if separator in line:
            return separator
    return " "


_PEAK_HEATING_RE = re.compile(r"^#\s*Peak space heating load\s*=\s*([-+0-9.eE]+)")


def write_steam_load_file(source: str, destination: str, minimum_load_fraction: float) -> dict:
    """Copy a MOS load file, applying a minimum (standby) space heating load as a floor.

    Every hour with a space heating load below ``minimum_load_fraction * peak`` is raised to that
    value. Hours above it are unchanged, so the annual heating energy only grows by the standby
    load during low-load hours (unlike adding a constant offset to every hour). Header lines and
    all other columns are copied unchanged.

    :param source: path of the original MOS file
    :param destination: path of the file to write
    :param minimum_load_fraction: standby load as a fraction of the peak space heating load (0 = none)
    :return: dict with the peak, the minimum load, the number of raised hours and the heating energy
             of the original and new files (Wh, assuming hourly rows)
    """
    if not 0.0 <= minimum_load_fraction < 1.0:
        raise ValueError(f"minimum_load_fraction must be in [0, 1), got {minimum_load_fraction}")

    with open(source, newline="") as f:
        lines = f.readlines()

    # Peak from the header (used by the model for Q_flow_nominal); fall back to the data maximum
    peak = None
    rows = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        match = _PEAK_HEATING_RE.match(stripped)
        if match:
            peak = float(match.group(1))
        if not stripped or stripped.startswith("#") or stripped[0].isalpha():
            continue
        separator = _mos_separator(stripped)
        fields = stripped.split(separator) if separator != " " else stripped.split()
        if len(fields) > MOS_HEATING_COLUMN:
            rows.append((i, fields, separator))
    if peak is None:
        peak = max(float(fields[MOS_HEATING_COLUMN]) for _, fields, _ in rows) if rows else 0.0

    q_min = minimum_load_fraction * peak
    raised = 0
    energy_before = 0.0
    energy_after = 0.0
    for i, fields, separator in rows:
        value = float(fields[MOS_HEATING_COLUMN])
        energy_before += value
        if value < q_min:
            raised += 1
            new_fields = list(fields)
            new_fields[MOS_HEATING_COLUMN] = repr(q_min)
            ending = lines[i][len(lines[i].rstrip("\r\n")) :]
            lines[i] = separator.join(new_fields) + ending
            value = q_min
        energy_after += value

    with open(destination, "w", newline="") as f:
        f.writelines(lines)

    return {
        "peak": peak,
        "minimum_load": q_min,
        "hours_raised": raised,
        "heating_energy_original": energy_before,
        "heating_energy_with_minimum": energy_after,
    }


class SteamBuilding(LoadBase):
    """Load connector for a 1st-generation (steam) building.

    Generates a GMT wrapper around Buildings.DHC.Loads.Steam.BuildingTimeSeriesAtETS that
    supplies the building heating load from the building's time-series (MOS) load file.
    """

    model_name = "SteamBuilding"

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = f"SteamBldg_{self.building_name}"

    def to_modelica(self, scaffold):
        """Generate the steam building-with-ETS model for this building.

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        steam_building_template = self.template_env.get_template("SteamBuildingTimeSeriesAtETS.mot")

        b_modelica_path = ModelicaPath(self.building_name, scaffold.loads_path.files_dir, True)
        self.copy_required_mo_files(b_modelica_path.files_dir, within=f"{scaffold.project_name}.Loads")

        # Resolve the building's time-series load file (fully resolved by the system_parameters object)
        time_series_filename = self.system_parameters.get_param_by_id(
            self.building_id, "load_model_parameters.time_series.filepath"
        )
        if not os.path.exists(time_series_filename):
            raise Exception(
                f"Missing MOS file for time series: {time_series_filename}\n"
                "If providing a relative path, ensure it is relative to the system parameters file."
            )
        if os.path.splitext(time_series_filename)[1].lower() == ".csv":
            raise Exception("The timeseries file is CSV format. This must be converted to an MOS file for use.")

        minimum_load_fraction = self.system_parameters.get_param(
            "$.district_system.first_generation.central_steam_plant_parameters.minimum_load_fraction"
        )
        if minimum_load_fraction is None:
            minimum_load_fraction = 0.02  # schema default

        building_template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "minimum_load_fraction": float(minimum_load_fraction),
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
        }

        # Copy the building's load file into its Resources directory, applying the minimum (standby)
        # space heating load as a floor. The steam ETS (PRV and condensate pump) is not numerically
        # well posed at zero steam flow, so low-load hours are raised to the standby load.
        new_file = os.path.join(b_modelica_path.resources_dir, os.path.basename(time_series_filename))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        self.load_file_stats = write_steam_load_file(time_series_filename, new_file, float(minimum_load_fraction))

        self.run_template(
            template=steam_building_template,
            save_file_name=os.path.join(b_modelica_path.files_dir, "building.mo"),
            project_name=scaffold.project_name,
            model_name=self.building_name,
            data=building_template_data,
        )

        self.post_process(scaffold)

    def post_process(self, scaffold):
        """Register the building subpackage within the Loads package.

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        b_modelica_path = os.path.join(scaffold.loads_path.files_dir, self.building_name)
        order_files = sorted(
            os.path.splitext(fname)[0]
            for fname in os.listdir(b_modelica_path)
            if fname.endswith(".mo") and fname != "package.mo"
        )
        new_package = PackageParser.new_from_template(
            b_modelica_path, self.building_name, order_files, within=f"{scaffold.project_name}.Loads"
        )
        new_package.save()

        scaffold.package.loads.add_model(self.building_name, create_subpackage=True)
        scaffold.package.loads.save()

    def get_modelica_type(self, scaffold):
        return f"Loads.{self.building_name}.building"
