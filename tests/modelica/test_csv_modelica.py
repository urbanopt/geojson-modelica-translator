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

import os
import shutil
import unittest

from geojson_modelica_translator.modelica.csv_modelica import CSVModelica


class CsvModelicaTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def test_csv_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            input_file = os.path.join(self.data_dir, 'DNE.csv')
            CSVModelica(input_file)
        self.assertIn("Unable to convert CSV file because this path does not exist:", str(context.exception))

    def test_csv_modelica(self):
        input_file = os.path.join(self.data_dir, 'Mass_Flow_Rates_Temperatures.csv')
        energyplus_timestep = 60 * 15
        output_modelica_file_name = os.path.join(self.output_dir, 'modelica')

        csv_converter = CSVModelica(input_file)
        # save the updated time series to the output directory of the test folder
        csv_converter.timeseries_to_modelica_data(output_modelica_file_name, energyplus_timestep, 'double')
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'modelica.csv')))

        # check if a string is in there
        with open(os.path.join(self.output_dir, 'modelica.csv'), 'r') as f:
            data = f.read()
            self.assertTrue('12600,42.25,55.0,15.73,6.67,8.58,0.19' in data)
            self.assertTrue('29700000,39.32,55.0,15.75,6.67,2.08,0.29' in data)
