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

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.energy_transfer_systems.cooling_indirect import (
    CoolingIndirect
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class CoolingIndirectTest(TestCaseBase):
    def test_cooling_indirect(self):
        project_name = "cooling_indirect"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        self.gj.scaffold_directory(self.output_dir, project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_ets.json")
        sys_params = SystemParameters(filename)

        # currently we must setup the root project before we can run to_modelica
        package = PackageParser.new_from_template(
            self.gj.scaffold.project_path, self.gj.scaffold.project_name, order=[])
        package.save()
        # now test the connector (independent of the larger geojson translator)
        geojson_id = self.gj.json_loads[0].feature.properties["id"]
        self.cooling_indirect = CoolingIndirect(sys_params, geojson_id)
        self.cooling_indirect.to_modelica(self.gj.scaffold)

        root_path = os.path.abspath(os.path.join(self.gj.scaffold.substations_path.files_dir))
        model_filepath = os.path.join(root_path, f'CoolingIndirect_{geojson_id}.mo')
        self.assertTrue(os.path.exists(model_filepath), f"File does not exist: {model_filepath}")
