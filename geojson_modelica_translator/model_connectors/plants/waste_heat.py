# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
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

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "wasHea_" + simple_uuid()
        self.waste_heat_name = "WasteHeat_" + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, "WasteHeatController.mo"))

    def to_modelica(self, scaffold):
        """Convert the Waste heat to Modelica code
        Create timeSeries models based on the data in the buildings and GeoJSONs

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        waste_heat_template = self.template_env.get_template("WasteHeatRecovery.mot")

        p_modelica_path = ModelicaPath(self.waste_heat_name, scaffold.plants_path.files_dir, True)

        waste_heat_params = {}

        waste_heat_rate = Path(
            self.system_parameters.get_param("$.district_system.fifth_generation.waste_heat_parameters.waste_heat_rate")
        )
        waste_heat_temperature = Path(
            self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.waste_heat_temperature"
            )
        )

        # Handle relative paths to schedule files (relative to sys-param file)
        sys_param_dir = Path(self.system_parameters.filename).parent.resolve()

        if isinstance(waste_heat_rate, Path) and not waste_heat_rate.expanduser().is_absolute():
            waste_heat_rate = sys_param_dir / waste_heat_rate.name
            if not waste_heat_rate.is_file():
                raise SystemExit(
                    f"Can't find rate schedule file.\n"
                    "If using a relative path, your path "
                    f" '{waste_heat_rate}' must be relative to the dir your "
                    "sys-param file is in."
                )
            # Copy schedule file into the modelica package
            waste_heat_rate_in_package = (
                Path(p_modelica_path.root_dir).parent / "Schedules" / waste_heat_rate.name
            ).resolve()
            shutil.copy(waste_heat_rate, waste_heat_rate_in_package)

        elif isinstance(waste_heat_rate, int):
            waste_heat_params["waste_heat_rate"] = waste_heat_rate

        if isinstance(waste_heat_temperature, Path) and not waste_heat_temperature.expanduser().is_absolute():
            waste_heat_temperature = sys_param_dir / waste_heat_temperature.name
            if not waste_heat_temperature.is_file():
                raise SystemExit(
                    f"Can't find temperature schedule file.\n"
                    "If using a relative path, your path "
                    f" '{waste_heat_temperature}' must be relative to the dir your "
                    "sys-param file is in."
                )
            # Copy schedule file into the modelica package
            waste_heat_temperature_in_package = (
                Path(p_modelica_path.root_dir).parent / "Schedules" / waste_heat_temperature.name
            ).resolve()
            shutil.copy(waste_heat_temperature, waste_heat_temperature_in_package)
        elif isinstance(waste_heat_temperature, int):
            waste_heat_params["waste_heat_temperature"] = waste_heat_temperature

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
        package_models = [self.waste_heat_name] + [Path(mo).stem for mo in self.required_mo_files]
        if not (Path(scaffold.plants_path.files_dir) / "package.mo").exists():
            plant_package = PackageParser.new_from_template(
                scaffold.plants_path.files_dir, "Plants", [self.waste_heat_name], within=f"{scaffold.project_name}"
            )
            plant_package.save()
        else:
            plant_package = PackageParser(Path(scaffold.plants_path.files_dir))
            for model_name in package_models:
                plant_package.add_model(model_name)
            plant_package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if "Plants" not in package.order:
            package.add_model("Plants")
            package.save()

    def get_modelica_type(self, scaffold):
        return f"Plants.{self.waste_heat_name}.WasteHeatRecovery"
