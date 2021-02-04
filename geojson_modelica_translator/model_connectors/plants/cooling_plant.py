"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import os
from pathlib import Path

from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
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
        mos_wet_bulb_filename = self.system_parameters.get_param(
            "$.district_system.default.central_cooling_plant_parameters.mos_wet_bulb_filename"
        )
        template_data = {
            "nominal_values": {
                "delta_temp": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.cooling_tower_water_temperature_difference_nominal"
                ),
                "fan_power": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.cooling_tower_fan_power_nominal"
                ),
                "chilled_water_pump_pressure_head": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.chw_pump_head"
                ),
                "condenser_water_pump_pressure_head": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.cw_pump_head"
                ),
                "heat_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.heat_flow_nominal"
                ),
                "mass_chw_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.mass_chw_flow_nominal"
                ),
                "mass_cw_flow_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.mass_cw_flow_nominal"
                ),
                "chiller_water_flow_minimum": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.chiller_water_flow_minimum"
                ),
                "pressure_drop_chw_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.pressure_drop_chw_nominal"
                ),
                "pressure_drop_cw_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.pressure_drop_cw_nominal"
                ),
                "pressure_drop_setpoint": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.pressure_drop_setpoint"
                ),
                "pressure_drop_chw_valve_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.pressure_drop_chw_valve_nominal"
                ),
                "pressure_drop_cw_pum_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.pressure_drop_cw_pum_nominal"
                ),
                "temp_cw_in_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.temp_cw_in_nominal"
                ),
                "delta_temp_approach": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.delta_temp_approach"
                ),
                "ratio_water_air_nominal": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.ratio_water_air_nominal"
                ),
            },
            "wet_bulb_calc": {
                "mos_wet_bulb_filename": mos_wet_bulb_filename,
                "filename": Path(mos_wet_bulb_filename).name,
                "path": Path(mos_wet_bulb_filename).parent,
                "modelica_path": self.modelica_path(mos_wet_bulb_filename),
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
        return f'{scaffold.project_name}.Plants.CentralCoolingPlant'
