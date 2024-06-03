# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district_5g import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


# WARNING: this requires ThermalNetwork to have been run appropriately first!
class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_multiple_ghe"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)
        # path to a sample UO project run with ghe features and TN sizing already run
        # We'll need to set up a test environment for this eventually
        example_dir = Path.home() / "github" / "aaa"

        # load in the example geojson with multiple buildings
        gj_filename = example_dir / "exportGeo.json"
        self.gj = UrbanOptGeoJson(gj_filename)

        # ThermalNetwork package will place a loop_order file next to the sys-param file.
        # This file can be deleted after the model is created
        loop_order_filepath: Path = example_dir / "loop_order.json"
        bldg_groups_by_num: dict = json.loads(loop_order_filepath.read_text())

        # ThermalNetwork package will place a ghe_order file next to the sys-param file.
        # This file can be deleted after the model is created
        ghe_order_filepath: Path = example_dir / "ghe_order.json"
        ghe_groups_by_num: dict = json.loads(ghe_order_filepath.read_text())

        # the json files have integer keys stored as strings, so convert to int
        bldg_groups_by_num = {int(k): v for k, v in bldg_groups_by_num.items()}
        ghe_groups_by_num = {int(k): v for k, v in ghe_groups_by_num.items()}

        # load system parameter data
        sys_param_filename = example_dir / "zzz.json"
        sys_params = SystemParameters(sys_param_filename)

        # create borefield
        borefield = Borefield(sys_params)

        # create ambient water stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create the couplings and graph
        # create the couplings and graph for the "time series of the buildings" separately
        # only needed to create time series loads:
        # modelica://district_multiple_ghe/Loads/Resources/Data/[building_geojson_id]/*.mos
        # TODO: check if *.mos files can be created another way
        all_couplings = []
        all_couplings_time_series = []
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            all_couplings_time_series.append(Coupling(time_series_load, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(borefield, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="5G"))

        graph = CouplingGraph(all_couplings)
        graph_time_series = CouplingGraph(all_couplings_time_series)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph,
            coupling_graph_time_series=graph_time_series,
            num_of_bldg_groups=len(bldg_groups_by_num),
            bldg_groups_by_num=bldg_groups_by_num,
            num_of_ghe_groups=len(ghe_groups_by_num),
            ghe_groups_by_num=ghe_groups_by_num,
            borefield_borehole_configuration_type=borefield.borehole_configuration_type,
        )

        self.district.to_modelica()

        # Remove temporary files that were created by ThermalNetwork to aid in building the Modelica model
        if ghe_order_filepath.exists():
            ghe_order_filepath.unlink()
        if loop_order_filepath.exists():
            loop_order_filepath.unlink()

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
