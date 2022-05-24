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
import re
from pathlib import Path

import pytest
from buildingspy.io.outputfile import Reader
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
from modelica_builder.model import Model

from ..base_test_case import TestCaseBase


class TimeSeriesModelConnectorSingleBuildingMFTETSTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_massflow"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_massflow_ex1.json")
        sys_params = SystemParameters(filename)

        # create the load, ETSes and their couplings
        time_series_mft_load = TimeSeriesMFT(sys_params, self.gj.buildings[0])
        geojson_load_id = self.gj.buildings[0].feature.properties["id"]

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
        self.district = District(
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
        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    def test_mft_time_series_to_modelica_and_run(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        mo_file_name = Path(root_path) / 'DistrictEnergySystem.mo'
        # set the run time to 31536000 (full year in seconds)
        mofile = Model(mo_file_name)
        mofile.update_model_annotation({"experiment": {"StopTime": 31536000}})
        mofile.save()
        self.run_and_assert_in_docker(mo_file_name,
                                      project_path=self.district._scaffold.project_path,
                                      project_name=self.district._scaffold.project_name)

        # Check the results
        results_dir = f'{self.district._scaffold.project_path}_results'
        mat_file = f'{results_dir}/time_series_massflow_Districts_DistrictEnergySystem_result.mat'
        mat_results = Reader(mat_file, 'dymola')

        # hack to get the name of the loads (rather the 8 character connector shas)
        timeseries_load_var = None
        coolflow_var = None
        heatflow_var = None
        for var in mat_results.varNames():
            m = re.match("TimeSerMFTLoa_(.{8})", var)
            if m:
                timeseries_load_var = m[1]
                continue

            m = re.match("cooInd_(.{8})", var)
            if m:
                coolflow_var = m[1]
                continue

            m = re.match("heaInd_(.{8})", var)
            if m:
                heatflow_var = m[1]
                continue

            if None not in (timeseries_load_var, coolflow_var, heatflow_var):
                break

        (time1, ts_hea_load) = mat_results.values(f"TimeSerMFTLoa_{timeseries_load_var}.ports_aChiWat[1].m_flow")
        (_time1, ts_chi_load) = mat_results.values(f"TimeSerMFTLoa_{timeseries_load_var}.ports_aHeaWat[1].m_flow")
        (_time1, cool_q_flow) = mat_results.values(f"cooInd_{coolflow_var}.Q_flow")
        (_time1, heat_q_flow) = mat_results.values(f"heaInd_{heatflow_var}.Q_flow")

        # if any of these assertions fail, then it is likely that the change in the timeseries massflow model
        # has been updated and we need to revalidate the models.
        self.assertEqual(ts_hea_load.min(), 0)
        self.assertAlmostEqual(ts_hea_load.max(), 51, delta=1)
        self.assertAlmostEqual(ts_hea_load.mean(), 4, delta=1)

        self.assertEqual(ts_chi_load.min(), 0)
        self.assertAlmostEqual(ts_chi_load.max(), 61, delta=1)
        self.assertAlmostEqual(ts_chi_load.mean(), 4, delta=1)

        self.assertAlmostEqual(cool_q_flow.min(), -51750, delta=10)
        self.assertAlmostEqual(cool_q_flow.max(), 354100, delta=10)
        self.assertAlmostEqual(cool_q_flow.mean(), 3160, delta=10)

        self.assertAlmostEqual(heat_q_flow.min(), -343210, delta=10)
        self.assertAlmostEqual(heat_q_flow.max(), 39475, delta=10)
        self.assertAlmostEqual(heat_q_flow.mean(), -23270, delta=10)
