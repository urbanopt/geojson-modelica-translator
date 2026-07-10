# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.design_data_series import DesignDataSeries
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants.no_plant_boundary import NoPlantBoundary
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictSystemNoPlantBoundaryTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_5g_no_plant"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)
        self.no_plant_data_dir = Path(__file__).parent / "data_no_plant"

        # load in the example geojson with time series office buildings
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data without a 5G plant/GHE definition
        filename = Path(self.no_plant_data_dir) / "time_series_5g_sys_params.json"
        sys_params = SystemParameters(filename)

        # create 5G district network, pump, design data, and no-plant boundary
        ambient_water_stub = NetworkDistributionPump(sys_params)
        design_data = DesignDataSeries(sys_params)
        distribution = UnidirectionalSeries(sys_params)
        no_plant_boundary = NoPlantBoundary(sys_params)

        # create load-to-network, load-to-pump, load-to-design-data, and no-plant couplings
        all_couplings = []
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            all_couplings.append(Coupling(time_series_load, distribution, district_type="fifth_generation"))
            all_couplings.append(Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation"))
            all_couplings.append(Coupling(time_series_load, design_data, district_type="fifth_generation"))
        all_couplings.append(Coupling(distribution, no_plant_boundary, district_type="fifth_generation"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="fifth_generation"))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph,
            geojson_file=self.gj,
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    def test_generated_district_system_uses_no_plant_boundary(self):
        district_model = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        district_text = district_model.read_text()

        assert "/5G_templates/UnidirectionalSeries_NoPlantBoundary/ComponentDefinitions.mopt" in district_text
        assert "bound_heatPort_" in district_text
        assert "heaNoPlant_" in district_text
        assert "cooNoPlant_" in district_text
        assert "TSouIn_fallback_" in district_text
        assert "TSouOut_fallback_" in district_text
        assert (
            "FanCoil2PipeCoolingDry"
            in (
                Path(self.district._scaffold.loads_path.files_dir)
                / "B5a6b99ec37f4de7f94020090"
                / "TimeSeriesBuilding.mo"
            ).read_text()
        )
        assert "Borefield" not in district_text

    def simulation_result_path(self):
        model_name = f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem"
        return self.district._scaffold.project_path / f"{model_name}_results" / f"{model_name}_res.mat"

    @pytest.mark.simulation
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            # run for 1 week to make sure this works well for longer time windows.
            start_time="0",
            stop_time="604800",
        )

        # rename results to winter_results.mat
        self.simulation_result_path().rename(self.district._scaffold.project_path / "winter_results.mat")

        # run for summer as well to make sure the no-plant boundary works for both heating and cooling
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time="5184000",
            stop_time="6048000",
        )
        # rename results to summer_results.mat
        self.simulation_result_path().rename(self.district._scaffold.project_path / "summer_results.mat")
