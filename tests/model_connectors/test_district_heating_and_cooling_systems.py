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

import numpy as np
import pytest
from buildingspy.io.outputfile import Reader
from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.couplings import (
    Coupling,
    CouplingGraph
)
from geojson_modelica_translator.model_connectors.districts import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems import (
    CoolingIndirect,
    HeatingIndirect
)
from geojson_modelica_translator.model_connectors.load_connectors import (
    TimeSeries
)
from geojson_modelica_translator.model_connectors.networks import Network2Pipe
from geojson_modelica_translator.model_connectors.plants import (
    CoolingPlant,
    HeatingPlant
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


@pytest.mark.simulation
class DistrictHeatingAndCoolingSystemsTest(TestCaseBase):
    def setUp(self):
        self.project_name = 'district_heating_and_cooling_systems'
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, self.project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_ets.json"
        self.sys_params = SystemParameters(filename)

    def test_district_heating_and_cooling_systems(self):
        # create cooling network and plant
        cooling_network = Network2Pipe(self.sys_params)
        cooling_plant = CoolingPlant(self.sys_params)

        # create heating network and plant
        heating_network = Network2Pipe(self.sys_params)
        heating_plant = HeatingPlant(self.sys_params)

        # create our load/ets/stubs
        # store all couplings to construct the District system
        all_couplings = [
            Coupling(cooling_network, cooling_plant),
            Coupling(heating_network, heating_plant),
        ]

        # keep track of separate loads and etses for testing purposes
        loads = []
        heat_etses = []
        cool_etses = []
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(self.sys_params, geojson_load)
            loads.append(time_series_load)
            geojson_load_id = geojson_load.feature.properties["id"]

            cooling_indirect = CoolingIndirect(self.sys_params, geojson_load_id)
            cool_etses.append(cooling_indirect)
            all_couplings.append(Coupling(time_series_load, cooling_indirect))
            all_couplings.append(Coupling(cooling_indirect, cooling_network))

            heating_indirect = HeatingIndirect(self.sys_params, geojson_load_id)
            heat_etses.append(heating_indirect)
            all_couplings.append(Coupling(time_series_load, heating_indirect))
            all_couplings.append(Coupling(heating_indirect, heating_network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph
        )
        district.to_modelica()

        root_path = Path(district._scaffold.districts_path.files_dir).resolve()
        self.run_and_assert_in_docker(Path(root_path) / 'DistrictEnergySystem.mo',
                                      project_path=district._scaffold.project_path,
                                      project_name=district._scaffold.project_name)

        #
        # Validate model outputs
        #
        results_dir = f'{district._scaffold.project_path}_results'
        mat_file = f'{results_dir}/{self.project_name}_Districts_DistrictEnergySystem_result.mat'
        mat_results = Reader(mat_file, 'dymola')

        # check the mass flow rates of the first load are in the expected range
        load = loads[0]
        (_, heat_m_flow) = mat_results.values(f'{load.id}.ports_aHeaWat[1].m_flow')
        # NL: changed the line below to be aChiWat (not repeating aHeaWat).
        (_, cool_m_flow) = mat_results.values(f'{load.id}.ports_aChiWat[1].m_flow')
        self.assertTrue((heat_m_flow >= 0).all(), 'Heating mass flow rate must be greater than or equal to zero')
        self.assertTrue((cool_m_flow >= 0).all(), 'Cooling mass flow rate must be greater than or equal to zero')

        # this tolerance determines how much we allow the actual mass flow rate to exceed the nominal value
        M_FLOW_NOMINAL_TOLERANCE = 0.01
        (_, heat_m_flow_nominal) = mat_results.values(f'{load.id}.mHeaWat_flow_nominal')
        heat_m_flow_nominal = heat_m_flow_nominal[0]
        (_, cool_m_flow_nominal) = mat_results.values(f'{load.id}.mChiWat_flow_nominal')
        cool_m_flow_nominal = cool_m_flow_nominal[0]
        self.assertTrue(
            (heat_m_flow <= heat_m_flow_nominal + (heat_m_flow_nominal * M_FLOW_NOMINAL_TOLERANCE)).all(),
            f'Heating mass flow rate must be less than nominal mass flow rate ({heat_m_flow_nominal}) '
            f'plus a tolerance ({M_FLOW_NOMINAL_TOLERANCE * 100}%)'
        )
        self.assertTrue(
            (cool_m_flow <= cool_m_flow_nominal + (cool_m_flow_nominal * M_FLOW_NOMINAL_TOLERANCE)).all(),
            f'Cooling mass flow rate must be less than nominal mass flow rate ({cool_m_flow_nominal}) '
            f'plus a tolerance ({M_FLOW_NOMINAL_TOLERANCE * 100}%)'
        )

        # check the thermal load
        (_, load_q_req_hea_flow) = mat_results.values(f'{load.id}.QReqHea_flow')
        (_, load_q_req_coo_flow) = mat_results.values(f'{load.id}.QReqCoo_flow')
        (_, load_q_heat_flow) = mat_results.values(f'{load.id}.QHea_flow')
        (_, load_q_cool_flow) = mat_results.values(f'{load.id}.QCoo_flow')

        # make sure the q flow is positive
        load_q_req_hea_flow, load_q_req_coo_flow = np.abs(load_q_req_hea_flow), np.abs(load_q_req_coo_flow)
        load_q_heat_flow, load_q_cool_flow = np.abs(load_q_heat_flow), np.abs(load_q_cool_flow)

        cool_cvrmsd = self.cvrmsd(load_q_cool_flow, load_q_req_coo_flow)
        heat_cvrmsd = self.cvrmsd(load_q_heat_flow, load_q_req_hea_flow)

        CVRMSD_MAX = 0.3
        # TODO: fix q flows to meet the CVRMSD maximum, then make these assertions rather than warnings
        if cool_cvrmsd >= CVRMSD_MAX:
            print(f'WARNING: The difference between the thermal cooling load of the load and ETS is too large (CVRMSD={cool_cvrmsd}). '
                  'TODO: make this warning an assertion.')
        if heat_cvrmsd >= CVRMSD_MAX:
            print(f'WARNING: The difference between the thermal heating load of the load and ETS is too large (CVRMSD={heat_cvrmsd}). '
                  'TODO: make this warning an assertion.')
