# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.utils import convert_c_to_k, simple_uuid


class HeatingPlantWithOptionalCHP(PlantBase):
    model_name = 'HeatingPlant'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'chpPla_' + simple_uuid()
        self.chp_installed = self.system_parameters.get_param(
            "$.district_system.fourth_generation.central_heating_plant_parameters.chp_installed"
        )
        if self.chp_installed is not True:
            self.required_mo_files.append(Path(self.template_dir) / 'CentralHeatingPlant.mo')
            self.id = 'heaPla' + simple_uuid()

        self.required_mo_files.append(Path(self.template_dir) / 'Boiler_TParallel.mo')
        self.required_mo_files.append(Path(self.template_dir) / 'BoilerStage.mo')
        self.required_mo_files.append(Path(self.template_dir) / 'HeatingWaterPumpSpeed.mo')
        self.required_mo_files.append(Path(self.template_dir) / 'PartialPlantParallel.mo')
        self.required_mo_files.append(Path(self.template_dir) / 'PartialPlantParallelInterface.mo')
        self.required_mo_files.append(Path(self.template_dir) / 'ValveParameters.mo')

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        if self.chp_installed:
            template_data = {
                "nominal_values": {
                    "heat_flow_nominal": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.heat_flow_nominal"
                    ),
                    "mass_hhw_flow_nominal": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.mass_hhw_flow_nominal"
                    ),
                    "boiler_water_flow_minimum": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.boiler_water_flow_minimum"
                    ),
                    "pressure_drop_hhw_nominal": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.pressure_drop_hhw_nominal"
                    ),
                    "pressure_drop_setpoint": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.pressure_drop_setpoint"
                    ),
                    "temp_setpoint_hhw": convert_c_to_k(self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.temp_setpoint_hhw"
                    )),
                    "pressure_drop_hhw_valve_nominal": self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.pressure_drop_hhw_valve_nominal"
                    ),
                },
                "signals": {
                    "thermal_following": str(self.system_parameters.get_param(
                        "$.district_system.fourth_generation.central_heating_plant_parameters.chp_thermal_following"
                    )).lower(),  # Booleans in Python start with a capital letter. Modelica wants it lowercase, hence this.
                },
            }
            plant_template = self.template_env.get_template("HeatingPlantWithCHP.mot")
            self.run_template(
                template=plant_template,
                save_file_name=Path(scaffold.plants_path.files_dir) / "CentralHeatingPlant.mo",
                project_name=scaffold.project_name,
                data=template_data
            )

        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir,
            within=f'{scaffold.project_name}.Plants')

        package = PackageParser(scaffold.project_path)
        if 'Plants' not in package.order:
            package.add_model('Plants')
            package.save()

        if self.chp_installed:
            package_models = ['CentralHeatingPlant'] + [Path(mo).stem for mo in self.required_mo_files]
        else:
            package_models = [Path(mo).stem for mo in self.required_mo_files]
        plants_package = PackageParser(scaffold.plants_path.files_dir)
        if plants_package.order_data is None:
            plants_package = PackageParser.new_from_template(
                path=scaffold.plants_path.files_dir,
                name="Plants",
                order=package_models,
                within=scaffold.project_name)
        else:
            for model_name in package_models:
                plants_package.add_model(model_name)
        plants_package.save()

    def get_modelica_type(self, scaffold):
        return 'Plants.CentralHeatingPlant'
