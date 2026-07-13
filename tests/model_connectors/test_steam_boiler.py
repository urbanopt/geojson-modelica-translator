# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
#
# Test suite for 1st-generation (steam) district energy systems.
#
# All tests generate explicit Modelica models for buildings, loads, ETS, network, and plant
# components from coupling graph definitions in the test setup.
#
# - SteamPlantMultipleTest: Tests a steam district with 2 buildings (time_series_ex1.json)
#   and 3 parallel boilers via time_series_sys_params_steam_3_boilers.json (number_of_boilers=3).
#
# - FullSteamDistrictTest: Tests a complete district with 3 buildings (time_series_ex2.json).
#   All buildings are coupled as TimeSeries loads → HeatingIndirect ETS → Network2Pipe.
#   Plant: 1-boiler SteamBoiler (default). All components generated explicitly.

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_cold_water_stub import EtsColdWaterStub
from geojson_modelica_translator.model_connectors.energy_transfer_systems.heating_indirect import HeatingIndirect
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import Network2Pipe
from geojson_modelica_translator.model_connectors.plants.steam_boiler import SteamPlant
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class SteamPlantMultipleTest(TestCaseBase):
    """Test steam boiler plant with multiple parallel boilers"""

    def setUp(self):
        super().setUp()

        self.project_name = "steam_plant_3_boilers"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, self.project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data with 3 boilers
        filename = Path(self.data_dir) / "time_series_sys_params_steam_3_boilers.json"
        self.sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(self.sys_params)
        heating_plant = SteamPlant(self.sys_params)

        # create our load/ets/stubs
        all_couplings = [Coupling(network, heating_plant)]
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(self.sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            heating_indirect_system = HeatingIndirect(self.sys_params, geojson_load_id)
            cold_water_stub = EtsColdWaterStub(self.sys_params)
            all_couplings.append(Coupling(time_series_load, heating_indirect_system))
            all_couplings.append(Coupling(time_series_load, cold_water_stub))
            all_couplings.append(Coupling(heating_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
        )
        self.district.to_modelica()

    def test_steam_boiler_with_multiple_boilers_parameter(self):
        """Verify that the steam boiler model includes the n_boilers parameter"""
        steam_boiler_model = Path(self.district._scaffold.plants_path.files_dir) / "SteamBoiler.mo"
        steam_boiler_mo = steam_boiler_model.read_text()

        # Check that the model has the n_boilers parameter set to 3
        assert "parameter Integer n_boilers=3" in steam_boiler_mo
        assert "Number of parallel steam boilers in the plant" in steam_boiler_mo

    @pytest.mark.simulation
    def test_simulate_steam_system_with_3_boilers(self):
        """Test that the steam system with 3 boilers can simulate successfully"""
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=0,  # Day 0 (in seconds)
            stop_time=86400,  # For 1 day duration (in seconds)
            step_size=3600,  # At 1 hour step size (in seconds)
        )


class FullSteamDistrictTest(TestCaseBase):
    """Test a complete steam district system with buildings, loads, ETSs, network, and plant"""

    def setUp(self):
        super().setUp()

        self.project_name = "district_steam"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, self.project_name)

        # load in the larger example geojson with 3 office buildings
        filename = Path(self.data_dir) / "time_series_ex2.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data with 3 buildings
        filename = Path(self.data_dir) / "time_series_sys_params_steam_3buildings.json"
        self.sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(self.sys_params)
        heating_plant = SteamPlant(self.sys_params)

        # create our load/ets/stubs for all 3 buildings
        all_couplings = [Coupling(network, heating_plant)]
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(self.sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            heating_indirect_system = HeatingIndirect(self.sys_params, geojson_load_id)
            cold_water_stub = EtsColdWaterStub(self.sys_params)
            all_couplings.append(Coupling(time_series_load, heating_indirect_system))
            all_couplings.append(Coupling(time_series_load, cold_water_stub))
            all_couplings.append(Coupling(heating_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
        )
        self.district.to_modelica()

    def test_build_large_steam_district(self):
        """Verify that a 3-building district can be generated"""
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    def test_large_district_has_correct_building_count(self):
        """Verify that the steam boiler model reflects 3 buildings"""
        steam_boiler_model = Path(self.district._scaffold.plants_path.files_dir) / "SteamBoiler.mo"
        steam_boiler_mo = steam_boiler_model.read_text()

        # Verify N_GMT=3 for 3 buildings (ex2 has 3 buildings)
        assert "parameter Integer N_GMT=3" in steam_boiler_mo
        # Total heat flow should be 60,000 (20,000 per building * 3)
        assert "parameter Modelica.Units.SI.HeatFlowRate QBui_flow_nominal_GMT=20000" in steam_boiler_mo

    def test_full_district_has_all_components(self):
        """Verify that the full district includes Loads, ETS, and Network packages"""
        loads_path = Path(self.district._scaffold.loads_path.files_dir)
        networks_path = Path(self.district._scaffold.networks_path.files_dir)
        plants_path = Path(self.district._scaffold.plants_path.files_dir)

        # Verify all component packages exist
        assert (loads_path / "package.mo").exists(), "Loads package should exist"
        assert (networks_path / "package.mo").exists(), "Network package should exist"
        assert (plants_path / "package.mo").exists(), "Plants package should exist"

    @pytest.mark.simulation
    def test_simulate_full_steam_district_one_day(self):
        """Test that the complete steam district can simulate for one day"""
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=0,  # Day 0 (in seconds)
            stop_time=86400,  # For 1 day duration (in seconds)
            step_size=3600,  # At 1 hour step size (in seconds)
        )
