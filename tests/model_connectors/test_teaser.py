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
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_cold_water_stub import (
    EtsColdWaterStub
)
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_hot_water_stub import (
    EtsHotWaterStub
)
from geojson_modelica_translator.model_connectors.load_connectors.teaser import (
    Teaser
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TeaserModelConnectorSingleBuildingTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "teaser_single"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "teaser_geojson_ex1.json")
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "teaser_system_params_ex1.json")
        sys_params = SystemParameters(filename)

        # build spawn model with hot and cold water stubbed out
        teaser = Teaser(sys_params, self.gj.buildings[0])
        hot_stub = EtsHotWaterStub(sys_params)
        cold_stub = EtsColdWaterStub(sys_params)

        graph = CouplingGraph([
            Coupling(teaser, hot_stub),
            Coupling(teaser, cold_stub),
        ])

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )

        self.district.to_modelica()

    def test_build_teaser_single(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.skip(reason="Fails with OM 1.20. Succeeds with OM 1.21")
    @pytest.mark.simulation
    def test_simulate_teaser_single(self):
        self.run_and_assert_in_docker(
            f'{self.district._scaffold.project_name}.Districts.DistrictEnergySystem',
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path
        )
