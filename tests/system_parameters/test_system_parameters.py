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

import os
import unittest

from ..context import geojson_modelica_translator  # noqa - Do not remove this line
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters


class GeoJSONTest(unittest.TestCase):

    def test_load_system_parameters(self):
        filename = os.path.abspath('tests/system_parameters/data/system_params_1.json')
        sdp = SystemParameters(filename)
        self.assertEqual(sdp.data['buildings']['default']['rc_order'], 2)

    def test_missing_file(self):
        fn = 'non-existent-path'
        with self.assertRaises(Exception) as exc:
            SystemParameters(fn)
        self.assertEqual(f'System design parameters file does not exist: {fn}', str(exc.exception))

    def test_errors(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "Spawn",
                    "rc_order": 6
                }
            }
        }
        sp = SystemParameters.loadd(data)
        self.assertEqual(sp.validate()[0], '6 is not one of [1, 2, 4]')

    def test_get_param(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "Spawn",
                    "rc_order": 6
                }
            }
        }
        sp = SystemParameters.loadd(data)
        value = sp.get_param('buildings.default.rc_order')
        self.assertEqual(value, 6)

        value = sp.get_param('buildings.default.load_model')
        self.assertEqual(value, 'Spawn')

        value = sp.get_param('buildings.default')
        self.assertDictEqual(value, {'load_model': 'Spawn', 'rc_order': 6})

        value = sp.get_param('')
        self.assertIsNone(value)

        value = sp.get_param('not.a.real.path')
        self.assertIsNone(value)

    def test_get_param_with_default(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "Spawn"
                }
            }
        }
        sp = SystemParameters.loadd(data)
        value = sp.get_param('buildings.default.rc_order', default=2)
        self.assertEqual(value, 2)

        value = sp.get_param('not.a.real.path', default=2)
        self.assertEqual(value, 2)


if __name__ == '__main__':
    unittest.main()
