"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

from buildingspy.io.outputfile import Reader
from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
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


class DistrictHeatingAndCoolingSystemsTest(TestCaseBase):
    def setUp(self):
        self.project_name = 'district_heating_and_cooling_systems'
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), self.project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_ets.json")
        self.sys_params = SystemParameters(filename)

    def test_district_heating_and_cooling_systems(self):
        # create cooling network and plant
        cooling_network = Network2Pipe(self.sys_params)
        cooling_plant = CoolingPlant(self.sys_params)

        # create heating network and plant
        heating_network = Network2Pipe(self.sys_params)
        heating_plant = HeatingPlant(self.sys_params)

        # create our load/ets/stubs
        all_couplings = [
            Coupling(cooling_network, cooling_plant),
            Coupling(heating_network, heating_plant),
        ]
        loads = []
        for geojson_load in self.gj.json_loads:
            time_series_load = TimeSeries(self.sys_params, geojson_load)
            loads.append(time_series_load)
            geojson_load_id = geojson_load.feature.properties["id"]

            cooling_indirect = CoolingIndirect(self.sys_params, geojson_load_id)
            all_couplings.append(Coupling(time_series_load, cooling_indirect))
            all_couplings.append(Coupling(cooling_indirect, cooling_network))

            heating_indirect = HeatingIndirect(self.sys_params, geojson_load_id)
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

        root_path = os.path.abspath(os.path.join(district._scaffold.districts_path.files_dir))
        self.run_and_assert_in_docker(os.path.join(root_path, 'DistrictEnergySystem.mo'),
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
        (_, cool_m_flow) = mat_results.values(f'{load.id}.ports_aHeaWat[1].m_flow')
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
