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

import shutil
import unittest
from pathlib import Path

from geojson_modelica_translator.modelica.csv_modelica import CSVModelica


class CsvModelicaTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def test_csv_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            input_file = Path(self.data_dir) / 'DNE.csv'
            CSVModelica(input_file)
        self.assertIn("Unable to convert CSV file because this path does not exist:", str(context.exception))

    def test_misshapen_csv_fails_gracefully(self):
        with self.assertRaises(SystemExit) as context:
            input_file = Path(self.data_dir) / 'misshapen_building_loads.csv'
            # This input file has a typo in a column name and a missing column. Each will cause the ValueError.
            CSVModelica(input_file)
            self.assertIn(
                "Usecols do not match columns, columns expected but not found:", str(
                    context.exception))

    def test_csv_modelica(self):
        input_file = Path(self.data_dir) / 'building_loads.csv'
        output_modelica_file_name = Path(self.output_dir) / 'modelica.csv'

        csv_converter = CSVModelica(input_file)
        # save the updated time series to the output directory of the test folder
        csv_converter.timeseries_to_modelica_data(output_modelica_file_name)
        self.assertTrue(output_modelica_file_name.exists())

        # check if a string is in there
        with open(output_modelica_file_name, 'r') as f:
            data = f.read()
            self.assertTrue('14400,52.74,82.22,4.06,15.41,6.68,10.35' in data)
            self.assertTrue('31532400,58.72,82.22,2.47,15.19,6.68,5.62' in data)
