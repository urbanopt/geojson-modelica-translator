"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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

from pathlib import Path

from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import convert_c_to_k, simple_uuid


class HeatingPlantWithOptionalCHP(PlantBase):
    model_name = 'HeatingPlant'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'chpPla_' + simple_uuid()
        self.chp_installed = self.system_parameters.get_param(
            "$.district_system.default.central_heating_plant_parameters.chp_installed"
        )
        if not self.chp_installed:
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
                        "$.district_system.default.central_heating_plant_parameters.heat_flow_nominal"
                    ),
                    "mass_hhw_flow_nominal": self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.mass_hhw_flow_nominal"
                    ),
                    "boiler_water_flow_minimum": self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.boiler_water_flow_minimum"
                    ),
                    "pressure_drop_hhw_nominal": self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.pressure_drop_hhw_nominal"
                    ),
                    "pressure_drop_setpoint": self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.pressure_drop_setpoint"
                    ),
                    "temp_setpoint_hhw": convert_c_to_k(self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.temp_setpoint_hhw"
                    )),
                    "pressure_drop_hhw_valve_nominal": self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.pressure_drop_hhw_valve_nominal"
                    ),
                },
                "signals": {
                    "thermal_following": str(self.system_parameters.get_param(
                        "$.district_system.default.central_heating_plant_parameters.chp_thermal_following"
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

        package_models = ['CentralHeatingPlant'] + [Path(mo).stem for mo in self.required_mo_files]
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
        return f'{scaffold.project_name}.Plants.CentralHeatingPlant'
