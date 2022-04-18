"""
****************************************************************************************************
:copyright (c) 2019-2022 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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
from geojson_modelica_translator.model_connectors.load_connectors.time_series_ets import (
    TimeSeriesETS
)
from geojson_modelica_translator.model_connectors.networks.network_chilled_water_stub import (
    NetworkChilledWaterStub
)
from geojson_modelica_translator.model_connectors.networks.network_heated_water_stub import (
    NetworkHeatedWaterStub
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)
from tests.base_test_case import TestCaseBase


@pytest.mark.simulation
class TimeSeriesETSTest(TestCaseBase):
    def test_time_series_ets(self):
        project_name = "time_series_ets"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = self.data_dir / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = self.data_dir / "time_series_system_params_ets.json"
        sys_params = SystemParameters(filename)

        # Create the time series load, ets and their coupling
        time_series_load = TimeSeriesETS(sys_params, self.gj.buildings[0])

        # create heated water stub for the ets
        heated_water_stub = NetworkHeatedWaterStub(sys_params)
        hi_hw_coupling = Coupling(time_series_load, heated_water_stub)

        #  create cold water stub for the load
        cold_water_stub = NetworkChilledWaterStub(sys_params)
        ts_cw_coupling = Coupling(time_series_load, cold_water_stub)

        graph = CouplingGraph([
            # ts_hi_coupling,
            hi_hw_coupling,
            ts_cw_coupling,
        ])

        district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )
        district.to_modelica()

        # Disable running the modelica model until we are off JModelica
        # root_path = Path(district._scaffold.districts_path.files_dir)
        # self.run_and_assert_in_docker(root_path / 'DistrictEnergySystem.mo',
        #                               project_path=district._scaffold.project_path,
        #                               project_name=district._scaffold.project_name)
