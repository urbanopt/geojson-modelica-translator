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
import unittest

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)


class GeoJSONTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_load_geojson(self):
        filename = os.path.join(self.data_dir, "geojson_1.json")
        json = UrbanOptGeoJson(filename)
        self.assertIsNotNone(json.data)
        self.assertEqual(len(json.data.features), 4)

        valid, results = json.validate()
        self.assertTrue(valid)
        self.assertEqual(len(results["building"]), 0)

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            UrbanOptGeoJson(fn)
        self.assertEqual(
            f"URBANopt GeoJSON file does not exist: {fn}", str(exc.exception)
        )

    def test_valid_instance(self):
        filename = os.path.join(self.data_dir, "geojson_1.json")
        json = UrbanOptGeoJson(filename)
        valid, results = json.validate()
        self.assertTrue(valid)
        self.assertEqual(len(results["building"]), 0)

    def test_validate(self):
        filename = os.path.join(self.data_dir, "geojson_1_invalid.json")
        json = UrbanOptGeoJson(filename)
        valid, results = json.validate()
        self.assertFalse(valid)
        self.assertEqual(len(results["building"]), 1)
        err = ["'footprint_area' is a required property", "'name' is a required property"]
        self.assertEqual(results["building"][0]["errors"], err)
