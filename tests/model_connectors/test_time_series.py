"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import os

import pytest
from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.load_connectors.time_series import (
    TimeSeries
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
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
            os.path.join(self.root_path, 'building.mo'),
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            self.assertTrue(os.path.exists(file), f"File does not exist: {file}")

    @pytest.mark.simulation
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
            os.path.join(self.root_path, 'building.mo'),
        ]

        # verify that there are only 2 files that matter (coupling and building)
        for file in files:
            self.assertTrue(os.path.exists(file), f"File does not exist: {file}")

        self.run_and_assert_in_docker(os.path.join(self.root_path, 'building.mo'),
                                      project_path=self.scaffold.project_path,
                                      project_name=self.scaffold.project_name)
