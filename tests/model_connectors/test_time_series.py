# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.scaffold import Scaffold
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class TimeSeriesModelConnectorSingleBuildingTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_no_ets"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)
        # scaffold the project ourselves
        self.scaffold = Scaffold(self.output_dir, project_name)
        self.scaffold.create()

    def test_build_model(self):
        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_no_ets.json"
        sys_params = SystemParameters(filename)

        # now test the connector (independent of the larger geojson translator)
        self.time_series = TimeSeries(sys_params, self.gj.buildings[0])

        assert self.time_series is not None
        assert self.time_series.building is not None
        assert self.time_series.system_parameters.get_param("buildings")[0]["load_model"] == "time_series"

        # currently we must setup the root project before we can run to_modelica
        package = PackageParser.new_from_template(self.scaffold.project_path, self.scaffold.project_name, order=[])
        package.save()
        self.time_series.to_modelica(self.scaffold)

        self.root_path = (Path(self.scaffold.loads_path.files_dir) / "B5a6b99ec37f4de7f94020090").resolve()
        files = [
            Path(self.root_path) / "TimeSeriesBuilding.mo",
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            assert Path(file).exists(), f"File does not exist: {file}"

    @pytest.mark.simulation
    @pytest.mark.skip(
        reason="There is no district in this model so the GMT never instantiates `delTAirHea` and compilation fails."
    )
    def test_build_and_simulate_no_ets(self):
        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_no_ets.json"
        sys_params = SystemParameters(filename)

        # now test the connector (independent of the larger geojson translator)
        self.time_series = TimeSeries(sys_params, self.gj.buildings[0])

        assert self.time_series is not None
        assert self.time_series.building is not None
        assert self.time_series.system_parameters.get_param("buildings")[0]["load_model"] == "time_series"

        # currently we must setup the root project before we can run to_modelica
        package = PackageParser.new_from_template(self.scaffold.project_path, self.scaffold.project_name, order=[])
        package.save()
        self.time_series.to_modelica(self.scaffold)

        self.root_path = (Path(self.scaffold.loads_path.files_dir) / "B5a6b99ec37f4de7f94020090").resolve()
        files = [
            Path(self.root_path) / "TimeSeriesBuilding.mo",
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            assert Path(file).exists(), f"File does not exist: {file}"

        self.run_and_assert_in_docker(
            f"{self.scaffold.project_name}.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding",
            file_to_load=self.scaffold.package_path,
            run_path=self.scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600,  # (in seconds)
        )
