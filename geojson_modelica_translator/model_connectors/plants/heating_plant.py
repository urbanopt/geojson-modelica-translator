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


class HeatingPlant(PlantBase):
    model_name = 'HeatingPlant'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'heaPla_' + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, 'CentralHeatingPlant.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'Boiler_TParallel.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'BoilerStage.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'HeatingWaterPumpSpeed.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialPlantParallel.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialPlantParallelInterface.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ValveParameters.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'Heater_T.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialPrescribedOutlet.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PrescribedOutlet.mo'))

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir,
            within=f'{scaffold.project_name}.Plants')

        package = PackageParser(scaffold.project_path)
        if 'Plants' not in package.order:
            package.add_model('Plants')
            package.save()

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
        return f'{scaffold.project_name}.Plants.CentralHeatingPlant'
