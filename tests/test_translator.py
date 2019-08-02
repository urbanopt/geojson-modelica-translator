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

from .context import geojson_modelica_translator  # noqa - Do not remove this line

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

    def test_to_modelica(self):
        filename = os.path.abspath('tests/geojson/data/geojson_1.json')
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        gj.to_modelica('geojson_1', 'tests/output')
        self.assertTrue(os.path.exists(gj.loads_path.files_dir))


if __name__ == '__main__':
    unittest.main()
