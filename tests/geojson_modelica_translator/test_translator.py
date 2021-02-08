"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.load_connectors import (
    Spawn,
    Teaser,
    TimeSeries
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class GeoJSONTranslatorTest(TestCaseBase):
    def setUp(self):
        self.project_name = 'geojson_1'
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), self.project_name)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_init(self):
        gj = GeoJSONTranslatorTest()
        self.assertIsNotNone(gj)

    def test_missing_geojson(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            GeoJsonModelicaTranslator.from_geojson(fn)
        self.assertEqual(f"GeoJSON file does not exist: {fn}", str(exc.exception))

    def test_translate_to_modelica(self):
        filename = os.path.join(self.data_dir, "geojson_1.json")

        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        filename = os.path.join(self.data_dir, "system_parameters_mix_models.json")
        gj.set_system_parameters(SystemParameters(filename))

        gj.process_loads()
        self.assertEqual(len(gj.loads), 3)
        gj.to_modelica(self.project_name, self.output_dir)

        # verify that there are 3 buildings, one of each type
        self.assertIsInstance(gj.loads[0], Spawn)
        self.assertIsInstance(gj.loads[1], TimeSeries)
        self.assertIsInstance(gj.loads[2], Teaser)

        building_paths = [
            os.path.join(gj.scaffold.loads_path.files_dir, b.dirname) for b in gj.json_loads
        ]

        for b in building_paths:
            p_check = os.path.join(b, 'building.mo')
            self.assertTrue(os.path.exists(p_check), f"Path not found {p_check}")
