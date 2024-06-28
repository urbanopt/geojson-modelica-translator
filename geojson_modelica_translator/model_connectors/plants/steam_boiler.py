# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import simple_uuid


class SteamPlant(PlantBase):
    model_name = "SteamBoiler"

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "steBoi" + simple_uuid()

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        template_data = {
            "nominal_values": {
                "boiler_efficiency": self.system_parameters.get_param(
                    "$.district_system.first_generation.central_steam_plant_parameters.boiler_efficiency"
                )
            }
        }

        plant_template = self.template_env.get_template("SteamBoiler.mot")
        self.run_template(
            template=plant_template,
            save_file_name=Path(scaffold.plants_path.files_dir) / "SteamBoiler.mo",
            project_name=scaffold.project_name,
            data=template_data,
        )

        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir, within=f"{scaffold.project_name}.Plants"
        )

        package = PackageParser(scaffold.project_path)
        if "Plants" not in package.order:
            package.add_model("Plants")
            package.save()

        package_models = ["SteamBoiler"] + [Path(mo).stem for mo in self.required_mo_files]
        plants_package = PackageParser(scaffold.plants_path.files_dir)
        if plants_package.order_data is None:
            plants_package = PackageParser.new_from_template(
                path=scaffold.plants_path.files_dir, name="Plants", order=package_models, within=scaffold.project_name
            )
        else:
            for model_name in package_models:
                plants_package.add_model(model_name)
        plants_package.save()

    def get_modelica_type(self, scaffold):
        return "Plants.SteamBoiler"
