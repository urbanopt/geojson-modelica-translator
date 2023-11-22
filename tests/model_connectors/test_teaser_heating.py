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
from geojson_modelica_translator.model_connectors.energy_transfer_systems.heating_indirect import (
    HeatingIndirect
)
from geojson_modelica_translator.model_connectors.load_connectors.teaser import (
    Teaser
)
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import (
    Network2Pipe
)
from geojson_modelica_translator.model_connectors.plants.chp import (
    HeatingPlantWithOptionalCHP
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TestTeaserHeating(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = 'teaser_district_heating'
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "teaser_geojson_two_loads.json")
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = os.path.join(self.data_dir, "teaser_system_params_two_loads.json")
        sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(sys_params)
        heating_plant = HeatingPlantWithOptionalCHP(sys_params)

        # create our our load/ets/stubs
        all_couplings = [
            Coupling(network, heating_plant)
        ]
        for geojson_load in self.gj.buildings:
            teaser_load = Teaser(sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            heating_indirect_system = HeatingIndirect(sys_params, geojson_load_id)
            cold_water_stub = EtsColdWaterStub(sys_params)
            all_couplings.append(Coupling(teaser_load, heating_indirect_system))
            all_couplings.append(Coupling(teaser_load, cold_water_stub))
            all_couplings.append(Coupling(heating_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph
        )
        self.district.to_modelica()

    def test_build_teaser_heating(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    @pytest.mark.skip(reason="Takes forever to run, might be crashing.")
    def test_simulate_teaser_heating(self):
        self.run_and_assert_in_docker(
            f'{self.district._scaffold.project_name}.Districts.DistrictEnergySystem',
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600  # (in seconds)
        )
