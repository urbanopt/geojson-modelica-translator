"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import unittest
from pathlib import Path
from shutil import rmtree

from geojson_modelica_translator.geojson.csv_to_sys_param import CSVToSysParam


class CSVToSysParamTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.scenario_dir = self.data_dir / "sdk_output_skeleton" / "run" / "baseline_15min"
        if self.output_dir.exists():
            rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

    def test_csv_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            scenario_dir = self.scenario_dir / 'foobar'
            sys_param_template = self.data_dir / 'time_series_template.json'
            feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
            CSVToSysParam(scenario_dir=scenario_dir, sys_param_template=sys_param_template, feature_file=feature_file)
        self.assertIn("Unable to find your scenario. The path you provided was:", str(context.exception))

    def test_csv_to_sys_param_does_not_overwrite(self):
        with self.assertRaises(Exception) as context:
            sys_param_template = self.data_dir / 'time_series_template.json'
            output_sys_param_file = self.output_dir / 'test_sys_param.json'
            feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
            first_run = CSVToSysParam(scenario_dir=self.scenario_dir, sys_param_template=sys_param_template, feature_file=feature_file)
            first_run.csv_to_sys_param(output_sys_param_file, overwrite=True)
            raise_an_error = CSVToSysParam(scenario_dir=self.scenario_dir, sys_param_template=sys_param_template, feature_file=feature_file)
            raise_an_error.csv_to_sys_param(output_sys_param_file, overwrite=False)
        self.assertIn("Output file already exists and overwrite is False:", str(context.exception))

    def test_csv_to_sys_param(self):
        sys_param_template = self.data_dir / 'time_series_template.json'
        output_sys_param_file = self.output_dir / 'test_sys_param.json'
        feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
        csv_to_sys_param = CSVToSysParam(scenario_dir=self.scenario_dir, sys_param_template=sys_param_template, feature_file=feature_file)
        csv_to_sys_param.csv_to_sys_param(output_sys_param_file)
        self.assertTrue(output_sys_param_file.exists())
