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
from geojson_modelica_translator.model_connectors.energy_transfer_systems import (
    CoolingIndirect,
    HeatingIndirect
)
from geojson_modelica_translator.model_connectors.load_connectors.time_series_mft_ets_coupling import (
    TimeSeriesMFT
)
from geojson_modelica_translator.model_connectors.networks import (
    NetworkChilledWaterStub,
    NetworkHeatedWaterStub
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TimeSeriesModelConnectorSingleBuildingMFTETSTest(TestCaseBase):
    def test_mft_time_series_to_modelica_and_run(self):
        project_name = "time_series_massflow"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_massflow_ex1.json")
        sys_params = SystemParameters(filename)

        # create the load, ETSes and their couplings
        time_series_mft_load = TimeSeriesMFT(sys_params, self.gj.json_loads[0])
        geojson_load_id = self.gj.json_loads[0].feature.properties["id"]

        heating_indirect_system = HeatingIndirect(sys_params, geojson_load_id)
        ts_hi_coupling = Coupling(time_series_mft_load, heating_indirect_system)

        cooling_indirect_system = CoolingIndirect(sys_params, geojson_load_id)
        ts_ci_coupling = Coupling(time_series_mft_load, cooling_indirect_system)

        # create network stubs for the ETSes
        heated_water_stub = NetworkHeatedWaterStub(sys_params)
        hi_hw_coupling = Coupling(heating_indirect_system, heated_water_stub)

        chilled_water_stub = NetworkChilledWaterStub(sys_params)
        ci_cw_coupling = Coupling(cooling_indirect_system, chilled_water_stub)

        # build the district system
        district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=CouplingGraph([
                ts_hi_coupling,
                ts_ci_coupling,
                hi_hw_coupling,
                ci_cw_coupling,
            ])
        )
        district.to_modelica()

        root_path = os.path.abspath(os.path.join(district._scaffold.districts_path.files_dir))
        self.run_and_assert_in_docker(os.path.join(root_path, 'DistrictEnergySystem.mo'),
                                      project_path=district._scaffold.project_path,
                                      project_name=district._scaffold.project_name)
