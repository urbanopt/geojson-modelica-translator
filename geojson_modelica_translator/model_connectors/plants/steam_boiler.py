# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import modelica_array_literal, simple_uuid


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

        # Get number_of_boilers, default to 1 if not specified
        number_of_boilers = self.system_parameters.get_param(f"{steam_params_path}.number_of_boilers") or 1

        # boiler_efficiency may be provided as a single number (constant efficiency) or as a
        # list of numbers (coefficients for the boiler efficiency curve), per the schema.
        # The underlying Modelica parameter (boi.a) is always Real[:], so normalize either
        # form into a valid Modelica array literal, e.g. "{0.7}" or "{0.9, 0.005, -0.0001}".
        boiler_efficiency = self.system_parameters.get_param(f"{steam_params_path}.boiler_efficiency")
        if boiler_efficiency is None:
            boiler_efficiency = 0.7  # schema default

        template_data = {
            "nominal_values": {
                "boiler_efficiency": modelica_array_literal(boiler_efficiency),
                "steam_pressure_setpoint": self.system_parameters.get_param(
                    f"{steam_params_path}.steam_pressure_setpoint"
                ),
                "number_of_boilers": number_of_boilers,
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
