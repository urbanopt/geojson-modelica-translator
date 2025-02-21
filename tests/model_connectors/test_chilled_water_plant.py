# # :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# # See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

# from pathlib import Path

# import pytest

# from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
# from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
# from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
# from geojson_modelica_translator.model_connectors.districts.district import District
# from geojson_modelica_translator.model_connectors.networks.network_chilled_water_stub import NetworkChilledWaterStub
# from geojson_modelica_translator.model_connectors.plants import CoolingPlant
# from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
# from tests.base_test_case import TestCaseBase


# class DistrictSystemTest(TestCaseBase):
#     def setUp(self):
#         super().setUp()

#         project_name = "chilled_water_plant_stub"
#         self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

#         # load in the example geojson with a single office building
#         filename = Path(self.data_dir) / "time_series_ex1.json"
#         self.gj = UrbanOptGeoJson(filename)

#         # load system parameter data
#         filename = Path(self.data_dir) / "time_series_system_params_ets.json"
#         sys_params = SystemParameters(filename)

#         cooling_plant = CoolingPlant(sys_params)
#         # create chilled water stub for the ets
#         chilled_water_stub = NetworkChilledWaterStub(sys_params)
#         cp_cw_coupling = Coupling(cooling_plant, chilled_water_stub)

#         graph = CouplingGraph(
#             [
#                 cp_cw_coupling,
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
