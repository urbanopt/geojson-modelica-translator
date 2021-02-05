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
from geojson_modelica_translator.model_connectors.couplings.coupling import (
    Coupling
)
from geojson_modelica_translator.model_connectors.couplings.graph import (
    CouplingGraph
)
from geojson_modelica_translator.model_connectors.districts.district import (
    District
)
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_cold_water_stub import (
    EtsColdWaterStub
)
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_hot_water_stub import (
    EtsHotWaterStub
)
from geojson_modelica_translator.model_connectors.load_connectors.spawn import (
    Spawn
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class SpawnModelConnectorSingleBuildingTest(TestCaseBase):
    def test_spawn_single(self):
        project_name = "spawn_single"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single offie building
        filename = os.path.join(self.data_dir, "spawn_geojson_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "spawn_system_params_ex1.json")
        sys_params = SystemParameters(filename)

        # build spawn model with hot and cold water stubbed out
        spawn = Spawn(sys_params, self.gj.json_loads[0])
        hot_stub = EtsHotWaterStub(sys_params)
        cold_stub = EtsColdWaterStub(sys_params)

        graph = CouplingGraph([
            Coupling(spawn, hot_stub),
            Coupling(spawn, cold_stub),
        ])

        district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )

        district.to_modelica()

        root_path = os.path.abspath(os.path.join(district._scaffold.districts_path.files_dir))
        self.run_and_assert_in_docker(os.path.join(root_path, 'DistrictEnergySystem.mo'),
                                      project_path=district._scaffold.project_path,
                                      project_name=district._scaffold.project_name)
