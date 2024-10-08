# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems.ets_cold_water_stub import EtsColdWaterStub
from geojson_modelica_translator.model_connectors.energy_transfer_systems.heating_indirect import HeatingIndirect
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_heated_water_stub import NetworkHeatedWaterStub
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_heating_indirect"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)
        single_building = self.gj.buildings[0]

        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_ets.json"
        sys_params = SystemParameters(filename)

        # Create the time series load, ets and their coupling
        time_series_load = TimeSeries(sys_params, single_building)
        geojson_load_id = single_building.feature.properties["id"]
        heating_indirect_system = HeatingIndirect(sys_params, geojson_load_id)
        ts_hi_coupling = Coupling(time_series_load, heating_indirect_system)

        assert time_series_load is not None
        assert time_series_load.building is not None
        assert time_series_load.system_parameters.get_param("buildings")[0]["load_model"] == "time_series"

        # create heated water stub for the ets
        heated_water_stub = NetworkHeatedWaterStub(sys_params)
        hi_hw_coupling = Coupling(heating_indirect_system, heated_water_stub)

        #  create cold water stub for the load
        cold_water_stub = EtsColdWaterStub(sys_params)
        ts_cw_coupling = Coupling(time_series_load, cold_water_stub)

        graph = CouplingGraph(
            [
                ts_hi_coupling,
                hi_hw_coupling,
                ts_cw_coupling,
            ]
        )

        self.district = District(
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
        )
