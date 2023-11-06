# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import shutil
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.utils import simple_uuid


class CoolingPlant(PlantBase):
    model_name = 'CoolingPlant'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'cooPla_' + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, 'CoolingTowerWithBypass.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'CoolingTowerParallel.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ChilledWaterPumpSpeed.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ChillerStage.mo'))

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        weather_filepath = Path(self.system_parameters.get_param("$.weather"))

        # verify that the weather file exists
        if not weather_filepath.exists():
            raise FileNotFoundError(
                f"Missing MOS weather file for CoolingPlant: {str(weather_filepath)}")
        else:
            # copy the weather file to resources for the Plant and
            # update the string that will be in the .mo file (weather_file_modelica_string)
            shutil.copy(
                str(weather_filepath),
                os.path.join(scaffold.plants_path.resources_dir, weather_filepath.name)
            )
            weather_file_modelica_string = f'modelica://{scaffold.project_name}/' \
                                           f'{scaffold.plants_path.resources_relative_dir}/' \
                                           f'{weather_filepath.name}'

        template_data = {
            "nominal_values": {
                "delta_temp": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.cooling_tower_water_temperature_difference_nominal"  # noqa: E501
                ),
                "fan_power": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.cooling_tower_fan_power_nominal"
                ),
                "chilled_water_pump_pressure_head": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.chw_pump_head"
                ),
                "condenser_water_pump_pressure_head": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.cw_pump_head"
                ),
                "heat_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.heat_flow_nominal"
                ),
                "mass_chw_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.mass_chw_flow_nominal"
                ),
                "mass_cw_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.mass_cw_flow_nominal"
                ),
                "chiller_water_flow_minimum": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.chiller_water_flow_minimum"
                ),
                "pressure_drop_chw_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.pressure_drop_chw_nominal"
                ),
                "pressure_drop_cw_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.pressure_drop_cw_nominal"
                ),
                "pressure_drop_setpoint": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.pressure_drop_setpoint"
                ),
                "temp_setpoint_chw": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.temp_setpoint_chw"
                ),
                "pressure_drop_chw_valve_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.pressure_drop_chw_valve_nominal"
                ),
                "pressure_drop_cw_pum_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.pressure_drop_cw_pum_nominal"
                ),
                "temp_air_wb_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.temp_air_wb_nominal"
                ),
                "temp_cw_in_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.temp_cw_in_nominal"
                ),
                "delta_temp_approach": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.delta_temp_approach"
                ),
                "ratio_water_air_nominal": self.system_parameters.get_param(
                    "$.district_system.fourth_generation.central_cooling_plant_parameters.ratio_water_air_nominal"
                ),
            },
            "wet_bulb_calc": {
                "modelica_path": weather_file_modelica_string,
            },
        }

        plant_template = self.template_env.get_template("CentralCoolingPlant.mot")
        self.run_template(
            plant_template,
            os.path.join(scaffold.plants_path.files_dir, "CentralCoolingPlant.mo"),
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

        package_models = ['CentralCoolingPlant'] + [Path(mo).stem for mo in self.required_mo_files]
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
        return 'Plants.CentralCoolingPlant'
