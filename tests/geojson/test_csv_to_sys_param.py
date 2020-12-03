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

from pathlib import Path
import unittest

from geojson_modelica_translator.geojson.csv_to_sys_param import CSVToSysParam


class CSVToSysParamTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def test_csv_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            input_mfrt_file = Path(self.data_dir) / 'DNE.csv'
            input_loads_file = Path(self.data_dir) / 'building_loads_snippet.csv'
            CSVToSysParam(input_mfrt_file=input_mfrt_file, input_loads_file=input_loads_file)
        self.assertIn("Unable to convert CSV file because one of these paths does not exist:", str(context.exception))

    def test_csv_to_sys_param_does_not_overwrite(self):
        with self.assertRaises(Exception) as context:
            input_mfrt_file = Path(self.data_dir) / 'building_mfrt_snippet.csv'
            input_loads_file = Path(self.data_dir) / 'building_loads_snippet.csv'
            output_sys_param_file = self.output_dir / 'test_sys_param.json'
            csv_to_sys_param = CSVToSysParam(input_mfrt_file=input_mfrt_file, input_loads_file=input_loads_file)
            csv_to_sys_param.csv_to_sys_param(output_sys_param_file, overwrite=False)
        self.assertIn("Output file already exists and overwrite is False:", str(context.exception))

    def test_csv_to_sys_param(self):
        input_mfrt_file = Path(self.data_dir) / 'building_mfrt_snippet.csv'
        input_loads_file = Path(self.data_dir) / 'building_loads_snippet.csv'
        output_sys_param_file = self.output_dir / 'test_sys_param.json'
        csv_to_sys_param = CSVToSysParam(input_mfrt_file=input_mfrt_file, input_loads_file=input_loads_file)
        csv_to_sys_param.csv_to_sys_param(output_sys_param_file)
        self.assertTrue(output_sys_param_file.exists())
