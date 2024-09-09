# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings import Coupling, CouplingGraph
from geojson_modelica_translator.model_connectors.districts import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems import CoolingIndirect, HeatingIndirect
from geojson_modelica_translator.model_connectors.load_connectors import Spawn, Teaser, TimeSeries
from geojson_modelica_translator.model_connectors.networks import Network2Pipe
from geojson_modelica_translator.model_connectors.plants import CoolingPlant
from geojson_modelica_translator.model_connectors.plants.chp import HeatingPlantWithOptionalCHP
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


@pytest.mark.simulation
class MixedLoadsTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        self.project_name = "mixed_loads"
        _, self.output_dir = self.set_up(Path(__file__).parent, self.project_name)

        filename = self.SHARED_DATA_DIR / "mixed_loads_district" / "geojson.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = self.SHARED_DATA_DIR / "mixed_loads_district" / "system_params.json"
        self.sys_params = SystemParameters(filename)

        # create cooling network and plant
        cooling_network = Network2Pipe(self.sys_params)
        cooling_plant = CoolingPlant(self.sys_params)

        # create heating network and plant
        heating_network = Network2Pipe(self.sys_params)
        heating_plant = HeatingPlantWithOptionalCHP(self.sys_params)

        # store all couplings to construct the District system
        all_couplings = [
            Coupling(cooling_network, cooling_plant),
            Coupling(heating_network, heating_plant),
        ]

        # keep track of separate loads and etses for testing purposes
        loads = []
        heat_etses = []
        cool_etses = []
        load_model_map = {"spawn": Spawn, "rc": Teaser, "time_series": TimeSeries}
        for geojson_load in self.gj.buildings:
            load_model_name = self.sys_params.get_param_by_id(geojson_load.id, "load_model")
            load_model = load_model_map[load_model_name]
            load = load_model(self.sys_params, geojson_load)
            loads.append(load)
            geojson_load_id = geojson_load.feature.properties["id"]

            cooling_indirect = CoolingIndirect(self.sys_params, geojson_load_id)
            cool_etses.append(cooling_indirect)
            all_couplings.append(Coupling(load, cooling_indirect))
            all_couplings.append(Coupling(cooling_indirect, cooling_network))

            heating_indirect = HeatingIndirect(self.sys_params, geojson_load_id)
            heat_etses.append(heating_indirect)
            all_couplings.append(Coupling(load, heating_indirect))
            all_couplings.append(Coupling(heating_indirect, heating_network))

        # verify we used all load types in the model
        used_classes = [type(x) for x in loads]
        for expected_load in load_model_map.values():
            assert expected_load in used_classes

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
        )
        self.district.to_modelica()

    def test_build_mixed_loads_district_energy_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation
    @pytest.mark.skip("OMC Spawn - Failed to find spawn executable in Buildings Library")
    def test_simulate_mixed_loads_district_energy_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600,  # (in seconds)
        )
