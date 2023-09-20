# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.load_connectors.time_series import (
    TimeSeries
)
from geojson_modelica_translator.modelica.package_parser import PackageParser
from geojson_modelica_translator.scaffold import Scaffold
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TimeSeriesModelConnectorSingleBuildingTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "time_series_no_ets"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = UrbanOptGeoJson(filename)
        # scaffold the project ourselves
        self.scaffold = Scaffold(self.output_dir, project_name)
        self.scaffold.create()

    def test_build_model(self):
        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_no_ets.json")
        sys_params = SystemParameters(filename)

        # now test the connector (independent of the larger geojson translator)
        self.time_series = TimeSeries(sys_params, self.gj.buildings[0])

        self.assertIsNotNone(self.time_series)
        self.assertIsNotNone(self.time_series.building)
        self.assertEqual("time_series",
                         self.time_series.system_parameters.get_param("buildings")[0]["load_model"])

        # currently we must setup the root project before we can run to_modelica
        package = PackageParser.new_from_template(
            self.scaffold.project_path, self.scaffold.project_name, order=[])
        package.save()
        self.time_series.to_modelica(self.scaffold)

        self.root_path = os.path.abspath(os.path.join(self.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090'))
        files = [
            os.path.join(self.root_path, 'TimeSeriesBuilding.mo'),
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            self.assertTrue(os.path.exists(file), f"File does not exist: {file}")

    @pytest.mark.simulation
    @pytest.mark.skip(reason="Because there is no district in this model, the GMT never instantiates `delTAirHea` and compilation fails.")
    # [/var/lib/jenkins2/ws/LINUX_BUILDS/tmp.build/openmodelica-1.21.0/OMCompiler/Compiler/NFFrontEnd/NFConnectEquations.mo:1038:5-1039:59:writable] Error: Internal error NFConnectEquations.lookupVarAttr could not find the variable ports_aHeaWat[1].m_flow
    def test_build_and_simulate_no_ets(self):
        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_no_ets.json")
        sys_params = SystemParameters(filename)

        # now test the connector (independent of the larger geojson translator)
        self.time_series = TimeSeries(sys_params, self.gj.buildings[0])

        self.assertIsNotNone(self.time_series)
        self.assertIsNotNone(self.time_series.building)
        self.assertEqual("time_series",
                         self.time_series.system_parameters.get_param("buildings")[0]["load_model"])

        # currently we must setup the root project before we can run to_modelica
        package = PackageParser.new_from_template(
            self.scaffold.project_path, self.scaffold.project_name, order=[])
        package.save()
        self.time_series.to_modelica(self.scaffold)

        self.root_path = os.path.abspath(os.path.join(self.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090'))
        files = [
            os.path.join(self.root_path, 'TimeSeriesBuilding.mo'),
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            self.assertTrue(os.path.exists(file), f"File does not exist: {file}")

        self.run_and_assert_in_docker(
            f'{self.scaffold.project_name}.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding',
            file_to_load=self.scaffold.package_path,
            run_path=self.scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600  # (in seconds)
        )
