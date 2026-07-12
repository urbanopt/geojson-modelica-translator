# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

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

        steam_params_path = "$.district_system.first_generation.central_steam_plant_parameters"
        template_data = {
            "nominal_values": {
                "boiler_efficiency": self.system_parameters.get_param(f"{steam_params_path}.boiler_efficiency"),
                "steam_pressure_setpoint": self.system_parameters.get_param(
                    f"{steam_params_path}.steam_pressure_setpoint"
                ),
                "reduced_pressure_setpoint": self.system_parameters.get_param(
                    f"{steam_params_path}.reduced_pressure_setpoint"
                ),
                "condensate_pressure_drop_nominal": self.system_parameters.get_param(
                    f"{steam_params_path}.condensate_pressure_drop_nominal"
                ),
                "heat_flow_nominal_building": self.system_parameters.get_param(
                    f"{steam_params_path}.heat_flow_nominal_building"
                ),
                "number_of_loads": len(self.system_parameters.get_param("$.buildings")),
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

        # Add models to Plants package using scaffold's PackageParser
        package_models = ["SteamBoiler"] + [Path(mo).stem for mo in self.required_mo_files]
        for model_name in package_models:
            scaffold.package.plants.add_model(model_name, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return "Plants.SteamBoiler"
