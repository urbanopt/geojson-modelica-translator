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
from pathlib import Path
from shutil import rmtree
import unittest

from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class SystemParametersTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.scenario_dir = self.data_dir / 'sdk_output_skeleton' / 'run' / 'baseline_15min'
        self.feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
        if self.output_dir.exists():
            rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        self.output_sys_param_file = self.output_dir / 'test_sys_param.json'

    def test_expanded_paths(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)
        value = sdp.get_param_by_building_id("ijk678", "load_model_parameters.spawn.idf_filename")
        self.assertEqual(value, os.path.join(os.path.dirname(filename), 'example_model.idf'))
        value = sdp.get_param_by_building_id("ijk678", "load_model_parameters.spawn.mos_weather_filename")
        self.assertEqual(value, os.path.join(os.path.dirname(filename), 'example_weather.mos'))
        value = sdp.get_param_by_building_id("ijk678", "load_model_parameters.spawn.epw_filename")
        self.assertEqual(value, os.path.join(os.path.dirname(filename), 'example_weather.epw'))

        # verify that the second spawn paths resolve too.
        value = sdp.get_param_by_building_id("lmn000", "load_model_parameters.spawn.idf_filename")
        self.assertEqual(value, os.path.join(os.path.dirname(filename), 'example_model_2.idf'))

    def test_load_system_parameters_1(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)
        self.assertEqual(
            sdp.data["buildings"]["default"]["load_model_parameters"]["rc"]["order"], 2
        )

    def test_load_system_parameters_2(self):
        filename = os.path.join(self.data_dir, 'system_params_2.json')
        sdp = SystemParameters(filename)
        self.assertIsNotNone(sdp)

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            SystemParameters(fn)
        self.assertEqual(
            f"System design parameters file does not exist: {fn}", str(exc.exception)
        )

    def test_errors(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "rc",
                    "load_model_parameters": {"rc": {"order": 6}},
                }
            }
        }

        with self.assertRaises(Exception) as exc:
            SystemParameters.loadd(data)
        self.assertRegex(str(exc.exception), "Invalid system parameter file.*")

        sp = SystemParameters.loadd(data, validate_on_load=False)
        self.assertEqual(sp.validate()[0], "'mos_weather_filename' is a required property")
        self.assertEqual(sp.validate()[1], "6 is not one of [1, 2, 3, 4]")

    def test_get_param(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "rc",
                    "load_model_parameters": {"rc": {"order": 4, "mos_weather_filename": "path-to-file"}},
                }
            }
        }
        sp = SystemParameters.loadd(data)
        # $.buildings.*[?load_model=spawn].load_model_parameters.spawn.idf_filename
        value = sp.get_param("$.buildings.default.load_model_parameters.rc.order")
        self.assertEqual(value, 4)

        value = sp.get_param("buildings.default.load_model")
        self.assertEqual(value, "rc")

        value = sp.get_param("buildings.default")
        self.assertDictEqual(
            value,
            {
                "load_model": "rc",
                "load_model_parameters": {
                    "rc": {"order": 4, "mos_weather_filename": "path-to-file"}}
            }
        )

        value = sp.get_param("")
        self.assertIsNone(value)

        value = sp.get_param("not.a.real.path")
        self.assertIsNone(value)

    def test_get_param_with_default(self):
        data = {"buildings": {"default": {"load_model": "spawn"}}}
        sp = SystemParameters.loadd(data)
        # this path doesn't exist, but there is a default
        value = sp.get_param(
            "buildings.default.load_model_parameters.rc.order", default=2
        )
        self.assertEqual(2, value)

        value = sp.get_param("not.a.real.path", default=2)
        self.assertEqual(2, value)

    def test_get_param_with_building_id_defaults(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)

        # ensure the defaults are respected. abcd1234 has NO metamodel defined
        value = sdp.get_param_by_building_id("abcd1234", "ets_model", "Not None")
        self.assertEqual("None", value)

        # grab the schema default
        value = sdp.get_param_by_building_id("defgh2345", "ets_model", "Not None")
        self.assertEqual("Indirect Heating and Cooling", value)
        value = sdp.get_param_by_building_id("defgh2345", "ets_model_parameters", "Not None")
        self.assertEqual({"indirect": {
            "q_flow_nominal": 8000,
            "eta_efficiency": 0.666,
            "nominal_flow_district": 0.666,
            "nominal_flow_building": 0.666,
            "pressure_drop_valve": 888,
            "pressure_drop_hx_secondary": 999,
            "pressure_drop_hx_primary": 999,
            "cooling_supply_water_temperature_district": 5,
            "cooling_supply_water_temperature_building": 7,
            "heating_supply_water_temperature_district": 55,
            "heating_supply_water_temperature_building": 50
        }}, value)

        # respect the passed default value
        value = sdp.get_param_by_building_id("defgh2345", "ets_model_parameters.NominalFlow_Building", 24815)
        self.assertEqual(24815, value)

    def test_get_param_with_none_building_id(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)
        self.maxDiff = None
        value = sdp.get_param_by_building_id(None, "ets_model", "Not None")
        self.assertEqual("Indirect Heating and Cooling", value)
        value = sdp.get_param_by_building_id(None, "ets_model_parameters", "Not None")
        self.assertEqual({'indirect': {
            "q_flow_nominal": 10000,
            "eta_efficiency": 0.9,
            "nominal_flow_district": 5000,
            "nominal_flow_building": 200,
            "pressure_drop_valve": 3,
            "pressure_drop_hx_secondary": 3,
            "pressure_drop_hx_primary": 3,
            "cooling_supply_water_temperature_district": 5,
            "cooling_supply_water_temperature_building": 7,
            "heating_supply_water_temperature_district": 55,
            "heating_supply_water_temperature_building": 50,
            "booster_heater": False,
            "ets_generation": "Fifth Generation",
            "ets_connection_type": "Indirect",
            "primary_design_delta_t": 3,
            "secondary_design_delta_t": 3
        }}, value)

    def test_scenario_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            scenario_dir = self.scenario_dir / 'foobar'
            dne = SystemParameters()
            dne.csv_to_sys_param(scenario_dir=scenario_dir, feature_file=self.feature_file, sys_param_filename=self.output_sys_param_file)
        self.assertIn("Unable to find your scenario. The path you provided was:", str(context.exception))

    def test_csv_to_sys_param_does_not_overwrite(self):
        with self.assertRaises(Exception) as context:
            first_run = SystemParameters()
            first_run.csv_to_sys_param(scenario_dir=self.scenario_dir, feature_file=self.feature_file, sys_param_filename=self.output_sys_param_file, overwrite=True)
            raise_an_error = SystemParameters()
            raise_an_error.csv_to_sys_param(scenario_dir=self.scenario_dir, feature_file=self.feature_file, sys_param_filename=self.output_sys_param_file, overwrite=False)
        self.assertIn("Output file already exists and overwrite is False:", str(context.exception))

    def test_csv_to_sys_param(self):
        csv_to_sys_param = SystemParameters()
        csv_to_sys_param.csv_to_sys_param(scenario_dir=self.scenario_dir, feature_file=self.feature_file, sys_param_filename=self.output_sys_param_file)
        self.assertTrue(self.output_sys_param_file.exists())
