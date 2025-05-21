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

        rate_schedule_path = Path(
            self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.rate_schedule_path"
            )
        )
        temperature_schedule_path = Path(
            self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.temperature_schedule_path"
            )
        )

        # Handle relative paths to schedule files (relative to sys-param file)
        sys_param_dir = Path(self.system_parameters.filename).parent.resolve()
        if not rate_schedule_path.expanduser().is_absolute():
            rate_schedule_path = sys_param_dir / rate_schedule_path.name
            if not rate_schedule_path.is_file():
                raise SystemExit(
                    f"Can't find rate schedule file.\n"
                    "If using a relative path, your path "
                    f" '{rate_schedule_path}' must be relative to the dir your "
                    "sys-param file is in."
                )
        if not temperature_schedule_path.expanduser().is_absolute():
            temperature_schedule_path = sys_param_dir / temperature_schedule_path.name
            if not temperature_schedule_path.is_file():
                raise SystemExit(
                    f"Can't find temperature schedule file.\n"
                    "If using a relative path, your path "
                    f" '{temperature_schedule_path}' must be relative to the dir your "
                    "sys-param file is in."
                )

        # copy over the waste heat schedule files
        # TODO: move some of this over to a validation step
        rate_schedule_path_in_package = (
            Path(p_modelica_path.root_dir).parent / "Schedules" / rate_schedule_path.name
        ).resolve()
        shutil.copy(rate_schedule_path, rate_schedule_path_in_package)

        temperature_schedule_path_in_package = (
            Path(p_modelica_path.root_dir).parent / "Schedules" / temperature_schedule_path.name
        ).resolve()
        shutil.copy(temperature_schedule_path, temperature_schedule_path_in_package)

        self.run_template(
            template=waste_heat_template,
            save_file_name=Path(p_modelica_path.files_dir) / "WasteHeatRecovery.mo",
            project_name=scaffold.project_name,
            model_name=self.waste_heat_name,
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
