# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

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
from geojson_modelica_translator.model_connectors.load_connectors.time_series import (
    TimeSeries
)
from geojson_modelica_translator.model_connectors.networks.network_ambient_water_stub import (
    NetworkAmbientWaterStub
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_5g"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = UrbanOptGeoJson(filename)
        single_building = self.gj.buildings[0]

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_5g_sys_params.json")
        sys_params = SystemParameters(filename)

        # Create the time series load, ets and their coupling
        time_series_load = TimeSeries(sys_params, single_building)

        # create ambient water stub
        ambient_water_stub = NetworkAmbientWaterStub(sys_params)
        five_g_coupling = Coupling(time_series_load, ambient_water_stub, district_type='5G')

        graph = CouplingGraph([
            five_g_coupling,
            # ts_cw_coupling,
        ])

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    # test_district_5g.py is this same test but with both buildings, and it works.
    @pytest.mark.skip(reason="https://github.com/urbanopt/geojson-modelica-translator/issues/572")
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f'{self.district._scaffold.project_name}.Districts.DistrictEnergySystem',
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path
        )

    @pytest.mark.dymola
    @pytest.mark.skip(reason="Structurally singular error in Dymola.")
    def test_simulate_district_system_in_dymola(self):
        # need to just pass the dir, dymola runner looks for package.mo
        self.run_and_assert_in_dymola(
            f'{self.district._scaffold.project_name}.Districts.DistrictEnergySystem',
            file_to_load=self.district._scaffold.project_path,
            run_path=self.district._scaffold.project_path,
            # debug=True
        )
