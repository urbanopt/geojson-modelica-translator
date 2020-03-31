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
import unittest

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)


class GeoJSONTest(unittest.TestCase):
    def test_load_geojson(self):
        # filename = os.path.abspath( "tests/geojson/data/example_geojson_13buildings.json")
        filename = os.path.abspath(os.path.join(os.getcwd() + "/data/example_geojson_13buildings.json"))
        json = UrbanOptGeoJson(filename)
        self.assertIsNotNone(json.data)
        # there are 13 buildings, plus 1 site, thus totally it is 14 features.
        self.assertEqual(len(json.data.features), 14)

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            UrbanOptGeoJson(fn)
        self.assertEqual(f"URBANopt GeoJSON file does not exist: {fn}", str(exc.exception))

    def test_validate(self):
        # filename = os.path.abspath("tests/geojson/data/example_geojson_13_buildings.json")
        filename = os.path.abspath(os.path.join(os.getcwd()+"/data/example_geojson_13buildings.json"))
        json = UrbanOptGeoJson(filename)
        valid, results = json.validate()
        self.assertFalse(valid)
        self.assertEqual(len(results["building"]), 13)
        # The id of buildings is numbered by 1-13, instead of uuid.
        self.assertEqual(results["building"][0]["id"], "1")


if __name__ == "__main__":
    unittest.main()
