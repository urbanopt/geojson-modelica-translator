# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import shutil

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.load_connectors.load_base import LoadBase
from geojson_modelica_translator.utils import ModelicaPath


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

        building_template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "minimum_load_fraction": self.system_parameters.get_param(
                "$.district_system.first_generation.central_steam_plant_parameters.minimum_load_fraction"
            )
            or 0.02,
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
        }

        # Copy the building's load file into its Resources directory
        new_file = os.path.join(b_modelica_path.resources_dir, os.path.basename(time_series_filename))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        shutil.copy(time_series_filename, new_file)

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
