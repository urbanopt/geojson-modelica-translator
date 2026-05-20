# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
import re

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems.cooling_indirect import CoolingIndirect
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_hot_water_stub import EtsHotWaterStub
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import Network2Pipe
from geojson_modelica_translator.model_connectors.plants.cooling_plant import CoolingPlant
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictCoolingSystemTest(TestCaseBase):
    def setUp(self):
        # TODO: remove all the unittest stuff since we use pytest
        super().setUp()

        project_name = "district_cooling_system"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        params_filename = Path(self.data_dir) / "time_series_system_params_ets.json"
        sys_params = SystemParameters(params_filename)

        # create network and plant
        network = Network2Pipe(sys_params)
        cooling_plant = CoolingPlant(sys_params)

        # create our our load/ets/stubs
        all_couplings = [Coupling(network, cooling_plant)]
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            geojson_load_id = geojson_load.feature.properties["id"]
            cooling_indirect_system = CoolingIndirect(sys_params, geojson_load_id)
            hot_water_stub = EtsHotWaterStub(sys_params)
            all_couplings.append(Coupling(time_series_load, cooling_indirect_system))
            all_couplings.append(Coupling(time_series_load, hot_water_stub))
            all_couplings.append(Coupling(cooling_indirect_system, network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
        )
        self.district.to_modelica()

    def test_build_district_cooling_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    def test_cooling_plant_sys_params_are_propagated(self):
        """Verify central cooling plant parameters from sys_params are rendered in Modelica."""
        district_mo_file = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        mo_content = district_mo_file.read_text()

        # The fixture sets these to 9.9, 9.9, 7999, and 6 respectively.
        mchw_match = re.search(r"mCHW_flow_nominal_(\w+)\s*=\s*9\.9\b", mo_content)
        assert mchw_match is not None, "mCHW_flow_nominal should propagate from sys_params"
        plant_id = mchw_match.group(1)

        assert re.search(r"mCW_flow_nominal_\w+\s*=\s*9\.9\b", mo_content), (
            "mCW_flow_nominal should propagate from sys_params"
        )
        assert re.search(r"QEva_nominal_\w+\s*=\s*-7999\b", mo_content), (
            "QEva_nominal should be the negated heat_flow_nominal from sys_params"
        )
        assert re.search(r"TSetChiWatDis_\w+\(\s*y\s*=\s*6\+273\.15\)", mo_content), (
            "temp_setpoint_chw should propagate from sys_params"
        )

        compact = "".join(mo_content.split())
        assert f"mMin_flow_{plant_id}=9.9/{plant_id}.numChi" in compact, (
            "mMin_flow should be based on chiller_water_flow_minimum divided by numChi"
        )

    @pytest.mark.simulation
    def test_simulate_district_cooling_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
        )
