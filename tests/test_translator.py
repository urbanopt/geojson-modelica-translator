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

import itertools
import os
import shutil
import unittest

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
# from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class GeoJSONTranslatorTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "geojson", "data")
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_init(self):
        gj = GeoJSONTranslatorTest()
        self.assertIsNotNone(gj)

    def test_from_geojson(self):
        filename = os.path.join(self.data_dir, "geojson_1.json")
        gj = GeoJsonModelicaTranslator.from_geojson(filename)

        self.assertEqual(len(gj.buildings), 3)

    def test_missing_geojson(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            GeoJsonModelicaTranslator.from_geojson(fn)
        self.assertEqual(f"GeoJSON file does not exist: {fn}", str(exc.exception))

    def test_to_modelica_defaults(self):
        results_path = os.path.join(self.output_dir, "geojson_1")
        if os.path.exists(results_path):
            shutil.rmtree(results_path)

        filename = os.path.join(self.data_dir, "geojson_1.json")
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        sys_params = SystemParameters()
        gj.set_system_parameters(sys_params)
        gj.to_modelica("geojson_1", self.output_dir)

        # setup what we are going to check
        model_names = [
            "Floor",
            "ICT",
            "Meeting",
            "Office",
            "package",
            "Restroom",
            "Storage",
        ]
        building_paths = [
            os.path.join(gj.scaffold.loads_path.files_dir, b.dirname) for b in gj.buildings
        ]
        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found {p}")

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
                path = os.path.join(gj.scaffold.loads_path.files_dir, "Resources", "Data",
                                    b.dirname, f"{resource_name}.txt")
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")

        # verify that the models run in JModelica -- this is broken!
        # mr = ModelicaRunner()
        # file_to_run = os.path.abspath(
        #     os.path.join(gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090', 'Office.mo')
        # )
        # run_path = Path(os.path.abspath(gj.scaffold.project_path)).parent
        # exitcode = mr.run_in_docker(file_to_run, run_path=run_path)
        # self.assertEqual(0, exitcode)

    def test_to_modelica_rc_order_4(self):
        results_path = os.path.join(self.output_dir, "rc_order_4")
        if os.path.exists(results_path):
            shutil.rmtree(results_path)

        filename = os.path.join(self.data_dir, "geojson_1.json")
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        sys_params = SystemParameters.loadd(
            {"buildings": {"default": {"load_model_parameters": {"rc": {"order": 4}}}}}
        )
        self.assertEqual(len(sys_params.validate()), 0)
        gj.set_system_parameters(sys_params)

        gj.to_modelica("rc_order_4", self.output_dir)

        # setup what we are going to check
        model_names = [
            "Floor",
            "ICT",
            "Meeting",
            "Office",
            "package",
            "Restroom",
            "Storage",
        ]
        building_paths = [
            os.path.join(gj.scaffold.loads_path.files_dir, b.dirname) for b in gj.buildings
        ]
        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found: {p}")

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
                path = os.path.join(gj.scaffold.loads_path.files_dir, "Resources", "Data",
                                    b.dirname, f"{resource_name}.txt")
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")

        # # make sure the model can run using the ModelicaRunner class
        # mr = ModelicaRunner()
        # file_to_run = os.path.abspath(
        #     f'{self.results_path}/Loads/B5a6b99ec37f4de7f94020090/Office.mo'
        # )
        # exitcode = mr.run_in_docker(file_to_run)
        # self.assertEqual(0, exitcode)


class GeoJSONUrbanOptExampleFileTranslatorTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "geojson", "data")
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_from_geojson(self):
        filename = os.path.join(self.data_dir, "example_geojson_13buildings.json")
        gj = GeoJsonModelicaTranslator.from_geojson(filename)

        self.assertEqual(len(gj.buildings), 13)

    def test_to_modelica_defaults(self):
        results_path = os.path.join(self.output_dir, "example_geojson_13buildings")
        if os.path.exists(results_path):
            shutil.rmtree(results_path)

        filename = os.path.join(self.data_dir, "example_geojson_13buildings.json")
        gj = GeoJsonModelicaTranslator.from_geojson(filename)
        sys_params = SystemParameters()
        gj.set_system_parameters(sys_params)
        gj.to_modelica("example_geojson_13buildings", self.output_dir)

        # setup what we are going to check
        model_names = [
            "Floor",
            "ICT",
            "Meeting",
            "Office",
            "package",
            "Restroom",
            "Storage",
        ]
        building_paths = [
            os.path.join(gj.scaffold.loads_path.files_dir, b.dirname) for b in gj.buildings
        ]
        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found: {p}")

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
                path = os.path.join(gj.scaffold.loads_path.files_dir, "Resources", "Data",
                                    b.dirname, f"{resource_name}.txt")
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")


class GeoJSONTranslatorETSTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output/ets/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_ets_templating(self):
        ets = GeoJsonModelicaTranslator().ets_templating()
        self.assertIsNotNone(ets)
