# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.ground_coupling import GroundCoupling
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_single_ghe"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with multiple buildings
        filename = Path(self.data_dir) / "time_series_ex2.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = Path(self.data_dir) / "system_params_ghe_3.json"
        sys_params = SystemParameters(filename)

        # create borefield
        borefield = Borefield(sys_params)

        # create ambient water stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create ground coupling
        ground_coupling = GroundCoupling(sys_params)

        # create the couplings and graph
        all_couplings = []
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            all_couplings.append(Coupling(time_series_load, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(borefield, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="5G"))

        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, geojson_file=self.gj, coupling_graph=graph
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation()
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            run_path=self.district._scaffold.project_path,
            file_to_load=self.district._scaffold.package_path,
        )
