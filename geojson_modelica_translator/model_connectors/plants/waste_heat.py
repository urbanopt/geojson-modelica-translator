# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)


class WasteHeat(PlantBase):
    model_name = "WasteHeatRecovery"

    def __init__(self, system_parameters, heat_source=None):
        super().__init__(system_parameters)
        self.id = "wasHea_" + simple_uuid()
        self.waste_heat_name = "WasteHeat_" + simple_uuid()
        self.source_id = heat_source["heat_source_id"]

        self.required_mo_files.append(os.path.join(self.template_dir, "WasteHeatController.mo"))

    def to_modelica(self, scaffold):
        """Convert the Waste heat to Modelica code
        Create timeSeries models based on the data in the buildings and GeoJSONs

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        waste_heat_template = self.template_env.get_template("WasteHeatRecovery.mot")

        p_modelica_path = ModelicaPath(self.waste_heat_name, scaffold.plants_path.files_dir, True)

        waste_heat_params = {}

        heat_source_rate = self.system_parameters.get_param_by_id(self.source_id, "heat_source_rate")

        heat_source_temperature = self.system_parameters.get_param_by_id(self.source_id, "heat_source_temperature")

        # Handle relative paths to schedule files (relative to sys-param file)
        sys_param_dir = Path(self.system_parameters.filename).parent.resolve()

        if isinstance(heat_source_rate, str):
            if not Path(heat_source_rate).expanduser().is_absolute():
                heat_source_rate = sys_param_dir / heat_source_rate
            heat_source_rate_in_package = (
                Path(p_modelica_path.root_dir).parent / "Schedules" / Path(heat_source_rate).name
            ).resolve()
            if not Path(heat_source_rate).is_file():
                raise SystemExit(
                    f"Can't find rate schedule file.\n"
                    "If using a relative path, your path "
                    f" '{heat_source_rate}' must be relative to the dir your sys-param file is in."
                )
            # Copy schedule file into the modelica package
            shutil.copy(heat_source_rate, heat_source_rate_in_package)

        elif isinstance(heat_source_rate, int):
            waste_heat_params["heat_source_rate"] = heat_source_rate

        if isinstance(heat_source_temperature, str):
            if not Path(heat_source_temperature).expanduser().is_absolute():
                heat_source_temperature = sys_param_dir / heat_source_temperature
            heat_source_temperature_in_package = (
                Path(p_modelica_path.root_dir).parent / "Schedules" / Path(heat_source_temperature).name
            ).resolve()
            if not Path(heat_source_temperature).is_file():
                raise SystemExit(
                    f"Can't find temperature schedule file.\n"
                    "If using a relative path, your path "
                    f" '{heat_source_temperature}' must be relative to the dir your sys-param file is in."
                )
            # Copy schedule file into the modelica package
            shutil.copy(heat_source_temperature, heat_source_temperature_in_package)
        elif isinstance(heat_source_temperature, int):
            waste_heat_params["heat_source_temperature"] = heat_source_temperature

        self.run_template(
            template=waste_heat_template,
            save_file_name=Path(p_modelica_path.files_dir) / "WasteHeatRecovery.mo",
            project_name=scaffold.project_name,
            model_name=self.waste_heat_name,
            data=waste_heat_params,
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir, within=f"{scaffold.project_name}.Plants"
        )

        # copy the schedule files into the Modelica model scaffold
        # new_file = Path(p_modelica_path.schedules_dir) / schedule_filepath
        # os.makedirs(os.path.dirname(new_file), exist_ok=True)
        # shutil.copy(time_series_filename, new_file)

        # run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """Cleanup the export of waste heat files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Plants project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """

        p_modelica_path = Path(scaffold.plants_path.files_dir) / self.waste_heat_name
        new_package = PackageParser.new_from_template(
            p_modelica_path,
            self.waste_heat_name,
            self.template_files_to_include,
            within=f"{scaffold.project_name}.Plants",
        )
        new_package.save()

        # now create the Loads level package and package.order.
        # Add models to Plants package using scaffold's PackageParser
        package_models = [self.waste_heat_name] + [Path(mo).stem for mo in self.required_mo_files]
        for model_name in package_models:
            scaffold.package.plants.add_model(model_name, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return f"Plants.{self.waste_heat_name}.WasteHeatRecovery"
