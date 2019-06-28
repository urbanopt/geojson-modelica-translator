"""
****************************************************************************************************
:copyright (c) 2019 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

from .context import geojson_modelica_translator  # Do not remove this line

import os
import unittest

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator


class GeoJSONTranslatorTest(unittest.TestCase):
    def test_init(self):
        gj = GeoJSONTranslatorTest()
        self.assertIsNotNone(gj)

    def test_from_geojson(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        gj = GeoJsonModelicaTranslator.from_geojson(filename)

        self.assertEqual(len(gj.buildings), 3)

    def test_scaffold(self):
        gj = GeoJsonModelicaTranslator()
        p = os.path.abspath(os.path.join('tests', 'output', 'test_01'))
        gj.scaffold_directory(p)

        # check the existence of all the member variables
        self.assertEqual(gj.loads_dir, os.path.join(p, 'Loads'))
        self.assertEqual(gj.substations_dir, os.path.join(p, 'Substations'))
        self.assertEqual(gj.plants_dir, os.path.join(p, 'Plants'))
        self.assertEqual(gj.districts_dir, os.path.join(p, 'Districts'))
        self.assertEqual(gj.resources_dir, os.path.join(p, 'Resources'))
        self.assertEqual(gj.resources_data_root_dir, os.path.join(p, 'Resources', 'Data'))
        self.assertEqual(gj.resources_data_loads_dir, os.path.join(p, 'Resources', 'Data', 'Loads'))
        self.assertEqual(gj.resources_data_districts_dir, os.path.join(p, 'Resources', 'Data', 'Districts'))
        self.assertEqual(gj.resources_data_weather_dir, os.path.join(p, 'Resources', 'Data', 'Weather'))

    def test_to_modelica(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        gj.to_modelica('tests/output/geojson_1')
        self.assertTrue(os.path.exists(gj.loads_dir))


if __name__ == '__main__':
    unittest.main()
