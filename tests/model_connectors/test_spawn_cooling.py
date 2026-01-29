# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems.cooling_indirect import CoolingIndirect
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_hot_water_stub import EtsHotWaterStub
from geojson_modelica_translator.model_connectors.load_connectors.spawn import Spawn
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import Network2Pipe
from geojson_modelica_translator.model_connectors.plants.cooling_plant import CoolingPlant
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class TestSpawnCooling(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "spawn_district_cooling"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "spawn_geojson_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = Path(self.data_dir) / "spawn_system_params_ex1.json"
        sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(sys_params)
        cooling_plant = CoolingPlant(sys_params)

        # create our our load/ets/stubs
        all_couplings = [Coupling(network, cooling_plant)]
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
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
        )
        self.district.to_modelica()

    def test_build_spawn_cooling(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation
    @pytest.mark.skip("OMC Failed to find spawn executable in Buildings Library")
    def test_simulate_spawn_cooling(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600,  # (in seconds)
        )
