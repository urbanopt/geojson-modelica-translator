# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
from pathlib import Path

import pytest

from geojson_modelica_translator.model_connectors.couplings.coupling import (
    Coupling
)
from geojson_modelica_translator.model_connectors.couplings.graph import (
    CouplingGraph
)
from geojson_modelica_translator.model_connectors.districts.district import (
    District
)
from geojson_modelica_translator.model_connectors.networks.network_ambient_water_stub import (
    NetworkAmbientWaterStub
)
from geojson_modelica_translator.model_connectors.plants.borefield import (
    Borefield
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "borefield_stub"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "system_params_ghe.json")
        sys_params = SystemParameters(filename)

        # Create the time series load, ets and their coupling
        borefield = Borefield(sys_params)

        # create ambient water stub
        ambient_water_stub = NetworkAmbientWaterStub(sys_params)
        five_g_coupling = Coupling(borefield, ambient_water_stub, district_type='5G')

        graph = CouplingGraph([
            five_g_coupling,
        ])

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph,
            borehole_pipe_arrangement = borefield.pipe_arrangement,
            borefield_borehole_configuration_type = borefield.borehole_configuration_type,
            borefield_id = borefield.id
        )
        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    @pytest.mark.skip(reason="Need to set use_m_flow_in=false. Then simulation fails in Linux, works on Windows.")
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f'{self.district._scaffold.project_name}.Districts.DistrictEnergySystem',
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path
        )
