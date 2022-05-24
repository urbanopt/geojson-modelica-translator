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
from pathlib import Path

import pytest
from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
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
from geojson_modelica_translator.model_connectors.energy_transfer_systems.cooling_indirect import (
    CoolingIndirect
)
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_hot_water_stub import (
    EtsHotWaterStub
)
from geojson_modelica_translator.model_connectors.load_connectors.spawn import (
    Spawn
)
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import (
    Network2Pipe
)
from geojson_modelica_translator.model_connectors.plants.cooling_plant import (
    CoolingPlant
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TestSpawnCooling(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = 'spawn_district_cooling'
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "spawn_geojson_ex1.json")
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "spawn_district_system_params_ex1.json")
        sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(sys_params)
        cooling_plant = CoolingPlant(sys_params)

        # create our our load/ets/stubs
        all_couplings = [
            Coupling(network, cooling_plant)
        ]
        for geojson_load in self.gj.buildings:
            spawn_load = Spawn(sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            cooling_indirect_system = CoolingIndirect(sys_params, geojson_load_id)
            hot_water_stub = EtsHotWaterStub(sys_params)
            all_couplings.append(Coupling(spawn_load, cooling_indirect_system))
            all_couplings.append(Coupling(spawn_load, hot_water_stub))
            all_couplings.append(Coupling(cooling_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )
        self.district.to_modelica()

    def test_build_spawn_cooling(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert ((root_path) / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    def test_simulate_spawn_cooling(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        self.run_and_assert_in_docker(Path(root_path) / 'DistrictEnergySystem.mo',
                                      project_path=self.district._scaffold.project_path,
                                      project_name=self.district._scaffold.project_name)
