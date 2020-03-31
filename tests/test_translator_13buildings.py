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

# import itertools
import os
import shutil
import unittest

# from geojson_modelica_translator.modelica.modelica_runner import (
#     ModelicaRunner
# )
from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class GeoJSONTranslatorTest(unittest.TestCase):
    def test_init(self):
        gj = GeoJSONTranslatorTest()
        self.assertIsNotNone(gj)

    def test_from_geojson(self):
        # filename = os.path.abspath("tests/geojson/data/geojson_1.json")
        filename = os.path.abspath(os.path.join(os.getcwd()+"/geojson/data/example_geojson_13buildings.json"))

        gj = GeoJsonModelicaTranslator.from_geojson(filename)

        self.assertEqual(len(gj.buildings), 13)

    def test_missing_geojson(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            GeoJsonModelicaTranslator.from_geojson(fn)
        self.assertEqual(f"GeoJSON file does not exist: {fn}", str(exc.exception))

    def test_to_modelica_defaults(self):
        self.results_path = os.path.abspath("tests_13buildings_modelica/output/geojson_13buildings")
        if os.path.exists(self.results_path):
            shutil.rmtree(self.results_path)

        # filename = os.path.abspath("tests/geojson/data/geojson_1.json")
        filename = os.path.abspath(os.path.join(os.getcwd()+"/geojson/data/example_geojson_13buildings.json"))

        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        sys_params = SystemParameters()
        gj.set_system_parameters(sys_params)
        gj.to_modelica("geojson_13buildings", "tests_13buildings_modelica/output")

        # setup what we are going to check
        """
        model_names = [
            "Floor",
            "ICT",
            "Meeting",
            "Office",
            "package",
            "Restroom",
            "Storage",
        ]
        """
        """
        for b in gj.buildings:
            print ("Jing3: ", vars(gj))

        building_paths = [
            os.path.join(gj.loads_path.files_dir, b.dirname) for b in gj.buildings
        ]
        """

        """
        building_paths =  os.listdir( os.path.join(os.getcwd()+"/tests_13buildings/output/geojson_13buildings/Loads/") )


        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]
        print("Jing3: ", path_checks )
        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found {p}")
        """
        # go through the generated buildings and ensure that the resources are created
        resource_names = [
            "InternalGains_Floor",
            "InternalGains_ICT",
            "InternalGains_Meeting",
            "InternalGains_Office",
            "InternalGains_Restroom",
            "InternalGains_Storage",
        ]
        for b in gj.buildings:
            for resource_name in resource_names:
                # TEASER 0.7.2 used .txt for schedule files
                path = os.path.join(
                    os.path.join(os.getcwd()+"/tests_13buildings_modelica/output/geojson_13buildings/Loads/"),
                    "Resources",
                    "Data",
                    b.dirname,
                    f"{resource_name}.txt",
                )
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")

    def test_to_modelica_rc_order_4(self):
        self.results_path = os.path.abspath("tests_13buildings_rc4/output/geojson_13buildings")
        if os.path.exists(self.results_path):
            shutil.rmtree(self.results_path)

        # filename = os.path.abspath("tests/geojson/data/geojson_1.json")
        filename = os.path.abspath(os.path.join(os.getcwd()+"/geojson/data/example_geojson_13buildings.json"))

        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        sys_params = SystemParameters.loadd(
            {"buildings": {"default": {"load_model_parameters": {"rc": {"order": 4}}}}}
        )
        self.assertEqual(len(sys_params.validate()), 0)
        gj.set_system_parameters(sys_params)

        gj.to_modelica("geojson_13buildings", "tests_13buildings_rc4/output")
        # setup what we are going to check
        """
        model_names = [
            "Floor",
            "ICT",
            "Meeting",
            "Office",
            "package",
            "Restroom",
            "Storage",
        ]
        """
        """
        building_paths = [
            os.path.join(gj.loads_path.files_dir, b.dirname) for b in gj.buildings
        ]
        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found: {p}")
        """
        resource_names = [
            "InternalGains_Floor",
            "InternalGains_ICT",
            "InternalGains_Meeting",
            "InternalGains_Office",
            "InternalGains_Restroom",
            "InternalGains_Storage",
        ]
        for b in gj.buildings:
            for resource_name in resource_names:
                # TEASER 0.7.2 used .txt for schedule files
                path = os.path.join(
                    os.path.join(os.getcwd()+"/tests_13buildings_rc4/output/geojson_13buildings/Loads/"),
                    "Resources",
                    "Data",
                    b.dirname,
                    f"{resource_name}.txt",
                )
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")

        # # make sure the model can run using the ModelicaRunner class
        # mr = ModelicaRunner()
        # file_to_run = os.path.abspath(
        #     f'{self.results_path}/Loads/B5a6b99ec37f4de7f94020090/Office.mo'
        # )
        # exitcode = mr.run_in_docker(file_to_run)
        # self.assertEqual(0, exitcode)


if __name__ == "__main__":
    unittest.main()
