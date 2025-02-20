# # :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# # See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

# from pathlib import Path

# import pytest

# from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
# from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
# from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
# from geojson_modelica_translator.model_connectors.districts.district import District
# from geojson_modelica_translator.model_connectors.networks.network_heated_water_stub import NetworkHeatedWaterStub
# from geojson_modelica_translator.model_connectors.plants import HeatingPlantWithOptionalCHP
# from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
# from tests.base_test_case import TestCaseBase


# class DistrictSystemTest(TestCaseBase):
#     def setUp(self):
#         super().setUp()

#         project_name = "heated_water_plant_stub"
#         self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

#         # load in the example geojson with a single office building
#         filename = Path(self.data_dir) / "time_series_ex1.json"
#         self.gj = UrbanOptGeoJson(filename)

#         # load system parameter data
#         filename = Path(self.data_dir) / "time_series_system_params_ets.json"
#         sys_params = SystemParameters(filename)

#         heating_plant = HeatingPlantWithOptionalCHP(sys_params)
#         heated_water_stub = NetworkHeatedWaterStub(sys_params)
#         hp_hw_coupling = Coupling(heating_plant, heated_water_stub)

#         graph = CouplingGraph(
#             [
#                 hp_hw_coupling,
#             ]
#         )

#         self.district = District(
#             root_dir=self.output_dir, project_name=project_name, system_parameters=sys_params, coupling_graph=graph
#         )
#         self.district.to_modelica()

#     def test_build_district_system(self):
#         root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
#         assert (root_path / "DistrictEnergySystem.mo").exists()

#     @pytest.mark.simulation
#     def test_simulate_district_system(self):
#         self.run_and_assert_in_docker(
#             f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
#             file_to_load=self.district._scaffold.package_path,
#             run_path=self.district._scaffold.project_path,
#         )
