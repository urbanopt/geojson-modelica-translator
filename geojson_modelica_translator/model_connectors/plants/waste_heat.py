# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)


class WasteHeat(PlantBase):
    model_name = "WasteHeat"

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "wasHea_" + simple_uuid()
        self.waste_heat_name = "WasteHeat_" + simple_uuid()

    def to_modelica(self, scaffold):
        """Convert the Waste heat to Modelica code
        Create timeSeries models based on the data in the buildings and GeoJSONs

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        waste_heat_template = self.template_env.get_template("WasteHeatRecovery.mot")

        p_modelica_path = ModelicaPath(self.waste_heat_name, scaffold.plants_path.files_dir, True)

        template_data = {
            "rate_schedule_path": self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.rate_schedule_path"
            ),
            "temperature_schedule_path": self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.temperature_schedule_path"
            ),
        }

        self.run_template(
            template=waste_heat_template,
            save_file_name=Path(p_modelica_path.files_dir) / "WasteHeatRecovery.mo",
            project_name=scaffold.project_name,
            model_name=self.waste_heat_name,
            template_data=template_data,
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
        if not (Path(scaffold.plants_path.files_dir) / "package.mo").exists():
            plant_package = PackageParser.new_from_template(
                scaffold.plants_path.files_dir, "Plants", [self.waste_heat_name], within=f"{scaffold.project_name}"
            )
            plant_package.save()
        else:
            plant_package = PackageParser(Path(scaffold.plants_path.files_dir))
            plant_package.add_model(self.waste_heat_name)
            plant_package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if "Plants" not in package.order:
            package.add_model("Plants")
            package.save()

    def get_modelica_type(self, scaffold):
        return f"Plants.{self.waste_heat_name}.WasteHeat"
