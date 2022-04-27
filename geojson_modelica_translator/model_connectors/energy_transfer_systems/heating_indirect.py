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

import os

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import simple_uuid


class HeatingIndirect(EnergyTransferBase):
    model_name = 'HeatingIndirect'

    def __init__(self, system_parameters, geojson_load_id):
        super().__init__(system_parameters, geojson_load_id)
        self.id = 'heaInd_' + simple_uuid()
        # _model_filename is the name of the file we generate, and thus the actual
        # model to be referenced when instantiating in the District model
        # TODO: refactor these property names (model_name and model_filename) because
        # it's confusing
        self._model_filename = f'HeatingIndirect_{self._geojson_load_id}'

    def to_modelica(self, scaffold):
        """
        Create indirect heating models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        heating_indirect_template = self.template_env.get_template("HeatingIndirect.mot")

        ets_data = self.system_parameters.get_param_by_building_id(
            self._geojson_load_id,
            "ets_model_parameters.indirect"
        )

        combined_template_data = {**ets_data, **self.district_template_data}

        self.run_template(
            template=heating_indirect_template,
            save_file_name=os.path.join(scaffold.project_path, 'Substations', f'{self._model_filename}.mo'),
            project_name=scaffold.project_name,
            model_filename=self._model_filename,
            ets_data=combined_template_data,
        )

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if 'Substations' not in package.order:
            package.add_model('Substations')
            package.save()

        package_models = [self._model_filename]
        ets_package = PackageParser(scaffold.substations_path.files_dir)
        if ets_package.order_data is None:
            ets_package = PackageParser.new_from_template(
                path=scaffold.substations_path.files_dir,
                name="Substations",
                order=package_models,
                within=scaffold.project_name)
        else:
            for model_name in package_models:
                if model_name not in ets_package.order:
                    ets_package.add_model(model_name)
        ets_package.save()

    def get_modelica_type(self, scaffold):
        return f'{scaffold.project_name}.Substations.{self._model_filename}'
