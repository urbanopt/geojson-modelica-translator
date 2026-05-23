# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import re
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
from geojson_modelica_translator.model_connectors.plants.chp import HeatingPlantWithOptionalCHP
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictHeatingSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_heating_system"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_ets.json"
        sys_params = SystemParameters(filename)

        # create network and plant
        network = Network2Pipe(sys_params)
        heating_plant = HeatingPlantWithOptionalCHP(sys_params)

        # create our our load/ets/stubs
        all_couplings = [Coupling(network, heating_plant)]
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            heating_indirect_system = HeatingIndirect(sys_params, geojson_load_id)
            cold_water_stub = EtsColdWaterStub(sys_params)
            all_couplings.append(Coupling(time_series_load, heating_indirect_system))
            all_couplings.append(Coupling(time_series_load, cold_water_stub))
            all_couplings.append(Coupling(heating_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
        )
        self.district.to_modelica()

    def test_build_district_heating_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    def test_heating_plant_sys_params_are_propagated(self):
        """Verify central heating plant parameters from sys_params are rendered in Modelica."""
        district_mo_file = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        mo_content = district_mo_file.read_text()

        # The fixture sets heat_flow_nominal=8001, mass_hhw_flow_nominal=1,
        # boiler_water_flow_minimum=0.1, and pressure_drop_hhw_nominal=55001.
        q_match = re.search(r"Q_flow_nominal_(\w+)\s*=\s*8001\b", mo_content)
        assert q_match is not None, "Q_flow_nominal should propagate heat_flow_nominal from sys_params"
        plant_id = q_match.group(1)

        assert re.search(r"mHW_flow_nominal_\w+\s*=\s*1\b", mo_content), (
            "mHW_flow_nominal should propagate mass_hhw_flow_nominal from sys_params"
        )
        assert re.search(r"dpBoi_nominal_\w+\s*=\s*55001\b", mo_content), (
            "dpBoi_nominal should propagate pressure_drop_hhw_nominal from sys_params"
        )

        compact = "".join(mo_content.split())
        assert f"mMin_flow_{plant_id}=0.1/{plant_id}.numBoi" in compact, (
            "mMin_flow should be boiler_water_flow_minimum divided by numBoi"
        )

    @pytest.mark.simulation
    def test_simulate_district_heating_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=86400 * 5,  # Day 5 (in seconds)
            stop_time=86400 * 6,  # For 1 day duration (in seconds)
            step_size=300,  # At 5-minute step size (in seconds)
        )
