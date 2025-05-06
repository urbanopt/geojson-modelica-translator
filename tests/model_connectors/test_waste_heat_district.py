# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.external_package_utils import load_loop_order
from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.design_data_series import DesignDataSeries
from geojson_modelica_translator.model_connectors.networks.ground_coupling import GroundCoupling
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.model_connectors.plants.waste_heat import WasteHeat
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictWasteHeat(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_waste_heat"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with multiple buildings
        geojson_filename = Path(self.data_dir) / "time_series_ex2.json"
        self.gj = UrbanOptGeoJson(geojson_filename)

        # load system parameter data
        sys_param_filename = Path(self.data_dir) / "time_series_waste_heat_sys_params.json"
        sys_params = SystemParameters(sys_param_filename)

        # read the loop order and create building groups
        loop_order = load_loop_order(sys_param_filename)

        # create ambient water loop stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create ground coupling
        ground_coupling = GroundCoupling(sys_params)

        # create waste heat source and controller
        waste_heat = WasteHeat(sys_params)

        # create district data
        design_data = DesignDataSeries(sys_params)

        # create the couplings and graph
        all_couplings = []
        for loop in loop_order:
            ghe_id = loop["list_ghe_ids_in_group"][0]
            for ghe in sys_params.get_param("$.district_system.fifth_generation.ghe_parameters.ghe_specific_params"):
                if ghe_id == ghe["ghe_id"]:
                    borefield = Borefield(sys_params, ghe)
            distribution = UnidirectionalSeries(sys_params)
            for bldg_id in loop["list_bldg_ids_in_group"]:
                for geojson_load in self.gj.buildings:
                    if bldg_id == geojson_load.id:
                        # create the building time series load
                        time_series_load = TimeSeries(sys_params, geojson_load)
                        # couple each time series load to distribution
                        all_couplings.append(Coupling(time_series_load, distribution, district_type="fifth_generation"))
                        all_couplings.append(
                            Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation")
                        )
                        all_couplings.append(Coupling(time_series_load, design_data, district_type="fifth_generation"))
            # couple each borefield and distribution
            all_couplings.append(Coupling(distribution, borefield, district_type="fifth_generation"))
            # couple distribution and ground coupling
            all_couplings.append(Coupling(distribution, ground_coupling, district_type="fifth_generation"))
            # empty couple between borefield and ground
            all_couplings.append(Coupling(ground_coupling, borefield, district_type="fifth_generation"))
        # couple distribution and waste heat
        all_couplings.append(Coupling(distribution, waste_heat, district_type="fifth_generation"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="fifth_generation"))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            geojson_file=self.gj,
            coupling_graph=graph,
        )

        self.district.to_modelica()

    def test_build_waste_heat_district(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation
    @pytest.mark.dymola
    @pytest.mark.skip(reason="Controller has too many event simulations for OM. Simulates as expected using Dymola")
    def test_simulate_district_waste_heat_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            # simulation_flags="-mei=50000"
        )
