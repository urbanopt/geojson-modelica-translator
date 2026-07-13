# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
#
# Test suite for 1st-generation (steam) district energy systems.
#
# The 1st-generation district model instantiates the native MBL steam stack explicitly and
# wires it with steam connections: a single-boiler steam plant (Plants.SteamBoiler) ->
# steam distribution network (Buildings.DHC.Networks.Steam.DistributionCondensatePipe) ->
# buildings with integrated steam energy transfer stations
# (Buildings.DHC.Loads.Steam.BuildingTimeSeriesAtETS). The number of buildings comes from
# the system parameters, and the central plant parameters drive the plant/network sizing.
#
# - SteamPlantMultipleTest: Tests a steam district with 2 buildings (time_series_ex1.json)
#   and number_of_boilers=3 via time_series_sys_params_steam_3_boilers.json.
#
# - FullSteamDistrictTest: Tests a complete district with 3 buildings (time_series_ex2.json).
#   Plant: 1-boiler SteamBoiler (default).

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
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

        # The 1st-generation district model instantiates the decomposed steam stack
        # (plant -> distribution -> buildings) directly, so only the plant coupling is
        # needed to build a valid coupling graph.
        all_couplings = [Coupling(network, heating_plant)]

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
            geojson_file=self.gj,
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

        # The 1st-generation district model instantiates the decomposed steam stack
        # (plant -> distribution -> buildings) directly, so only the plant coupling is
        # needed to build a valid coupling graph.
        all_couplings = [Coupling(network, heating_plant)]

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
            geojson_file=self.gj,
        )
        self.district.to_modelica()

    def test_build_large_steam_district(self):
        """Verify that a 3-building district can be generated with connected steam components"""
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        district_file = root_path / "DistrictEnergySystem.mo"
        assert district_file.exists()

        district_mo = district_file.read_text()

        # The decomposed steam components must be instantiated: per-building wrapped loads,
        # the steam distribution network, and the steam plant.
        assert "Buildings.DHC.Networks.Steam.DistributionCondensatePipe dis" in district_mo
        assert "Plants.SteamBoiler pla" in district_mo
        # One GMT-wrapped steam building (with integrated ETS) per geojson building (ex2 has 2)
        assert district_mo.count(".building bld") == 2
        assert "bld1(" in district_mo and "bld2(" in district_mo

        # ...and wired together: plant -> distribution -> buildings (with steam), per connection index
        assert "connect(dis.ports_bCon[1], bld1.port_a);" in district_mo
        assert "connect(bld1.port_b, dis.ports_aCon[1]);" in district_mo
        assert "connect(dis.ports_bCon[2], bld2.port_a);" in district_mo
        assert "connect(pla.port_bSerHea, dis.port_aDisSup);" in district_mo
        assert "connect(dis.port_bDisRet, pla.port_aSerHea);" in district_mo

    def test_large_district_has_correct_building_count(self):
        """Verify that the district model reflects the geojson buildings"""
        district_file = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        district_mo = district_file.read_text()

        # Verify N=2 (ex2 geojson has 2 buildings)
        assert "parameter Integer N=2" in district_mo
        # Each building's steam load instance should be connected to the network
        assert district_mo.count("connect(dis.ports_bCon[") == 2

    def test_full_district_has_all_components(self):
        """Verify that the district includes the Loads, Plants and Districts packages"""
        districts_path = Path(self.district._scaffold.districts_path.files_dir)
        plants_path = Path(self.district._scaffold.plants_path.files_dir)
        loads_path = Path(self.district._scaffold.loads_path.files_dir)

        # Verify component packages exist
        assert (districts_path / "package.mo").exists(), "Districts package should exist"
        assert (plants_path / "package.mo").exists(), "Plants package should exist"
        assert (loads_path / "package.mo").exists(), "Loads package should exist"

        # The steam plant wrapper model should be generated in the Plants package
        assert (plants_path / "SteamBoiler.mo").exists(), "SteamBoiler plant model should exist"

        # Each geojson building should have a generated GMT-wrapped steam building model
        building_models = list(loads_path.glob("*/building.mo"))
        assert len(building_models) == 2, "Each building should have a generated building.mo model"

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
