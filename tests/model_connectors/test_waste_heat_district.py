# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

# from geojson_modelica_translator.external_package_utils import load_loop_order
from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.design_data_series import DesignDataSeries

# from geojson_modelica_translator.model_connectors.networks.ground_coupling import GroundCoupling
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants.waste_heat import WasteHeat
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictWasteHeat(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_waste_heat"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with multiple buildings
        geojson_filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(geojson_filename)

        # load system parameter data
        sys_param_filename = Path(self.data_dir) / "time_series_5g_sys_params.json"
        sys_params = SystemParameters(sys_param_filename)

        # read the loop order and create building groups
        # loop_order = load_loop_order(sys_param_filename)

        # create waste heat source
        waste_heat = WasteHeat(sys_params)

        distribution = UnidirectionalSeries(sys_params)

        # create ambient water stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create ground coupling
        # ground_coupling = GroundCoupling(sys_params)

        # create district data
        design_data = DesignDataSeries(sys_params)

        # create our our load/ets/stubs
        all_couplings = []
        all_couplings.append(Coupling(distribution, waste_heat, district_type="fifth_generation"))
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            all_couplings.append(Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation"))
            all_couplings.append(Coupling(time_series_load, design_data, district_type="fifth_generation"))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
        )

        self.district.to_modelica()

    def test_build_waste_heat_district(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()
