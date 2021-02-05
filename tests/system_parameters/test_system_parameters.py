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
from pathlib import Path
from shutil import rmtree

from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class SystemParametersTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.scenario_dir = self.data_dir / 'sdk_output_skeleton' / 'run' / 'baseline_15min'
        self.feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
        self.sys_param_template = Path(__file__).parent.parent.parent / 'geojson_modelica_translator' / \
            'system_parameters' / 'time_series_template.json'
        if self.output_dir.exists():
            rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

    def test_expanded_paths(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)
        for s in sdp.validate():
            print(s)
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
                    "load_model_parameters": {
                        "rc": {"order": 6}},
                }
            }
        }

        with self.assertRaises(Exception) as exc:
            SystemParameters.loadd(data)
        self.assertRegex(str(exc.exception), "Invalid system parameter file.*")

        sp = SystemParameters.loadd(data, validate_on_load=False)
        self.assertEqual(len(sp.validate()), 6)
        self.assertIn("'fraction_latent_person' is a required property", sp.validate())
        self.assertIn("'mos_weather_filename' is a required property", sp.validate())
        self.assertIn("'temp_hw_supply' is a required property", sp.validate())
        self.assertIn("'temp_setpoint_cooling' is a required property", sp.validate())
        self.assertIn("'temp_setpoint_heating' is a required property", sp.validate())
        self.assertIn("6 is not one of [1, 2, 3, 4]", sp.validate())

    def test_get_param(self):
        data = {
            "buildings": {
                "default": {
                    "load_model": "rc",
                    "load_model_parameters": {
                        "rc": {
                            "order": 4,
                            "mos_weather_filename": "path-to-file",
                            "fraction_latent_person": 1.25,
                            "temp_hw_supply": 40,
                            "temp_setpoint_heating": 40,
                            "temp_setpoint_cooling": 24
                        }
                    },
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
                    "rc": {
                        "order": 4,
                        "mos_weather_filename": "path-to-file",
                        "fraction_latent_person": 1.25,
                        "temp_hw_supply": 40,
                        "temp_setpoint_heating": 40,
                        "temp_setpoint_cooling": 24
                    }
                }
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
        self.maxDiff = None
        # ensure the defaults are respected. abcd1234 has NO metamodel defined
        value = sdp.get_param_by_building_id("abcd1234", "ets_model", "Not None")
        self.assertEqual("None", value)

        # grab the schema default
        value = sdp.get_param_by_building_id("defgh2345", "ets_model", "Not None")
        self.assertEqual("Indirect Heating and Cooling", value)
        value = sdp.get_param_by_building_id("defgh2345", "ets_model_parameters", "Not None")
        self.assertEqual({"indirect": {
            "heat_flow_nominal": 8000,
            "heat_exchanger_efficiency": 0.8,
            "nominal_mass_flow_district": 0.5,
            "nominal_mass_flow_building": 0.5,
            "valve_pressure_drop": 6000,
            "heat_exchanger_secondary_pressure_drop": 500,
            "heat_exchanger_primary_pressure_drop": 500,
            "cooling_supply_water_temperature_district": 5,
            "cooling_supply_water_temperature_building": 7,
            "heating_supply_water_temperature_district": 55,
            "heating_supply_water_temperature_building": 50,
            "delta_temp_chw_building": 5,
            "delta_temp_chw_district": 8,
            "delta_temp_hw_building": 15,
            "delta_temp_hw_district": 20,
            "cooling_controller_y_max": 1,
            "cooling_controller_y_min": 0,
            "heating_controller_y_max": 1,
            "heating_controller_y_min": 0
        }}, value)

        # respect the passed default value
        value = sdp.get_param_by_building_id("defgh2345", "ets_model_parameters.NominalFlow_Building", 24815)
        self.assertEqual(24815, value)

    def test_get_param_with_none_building_id(self):
        filename = os.path.join(self.data_dir, 'system_params_1.json')
        sdp = SystemParameters(filename)
        self.maxDiff = None
        with self.assertRaises(SystemExit) as context:
            sdp.get_param_by_building_id(None, "ets_model", "Not None")
        self.assertIn("No building_id submitted. Please retry and include the feature_id", str(context.exception))

    def test_missing_files(self):
        with self.assertRaises(Exception) as context:
            output_sys_param_file = self.output_dir / 'going_to_fail_first.json'
            missing_scenario_dir = self.scenario_dir / 'foobar'
            SystemParameters.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=missing_scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(f"Unable to find your scenario. The path you provided was: {missing_scenario_dir}", str(context.exception))
        with self.assertRaises(Exception) as context:
            missing_feature_file = self.data_dir / 'sdk_output_skeleton' / 'foobar.json'
            SystemParameters.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=missing_feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(f"Unable to find your feature file. The path you provided was: {missing_feature_file}", str(context.exception))

    def test_csv_to_sys_param_does_not_overwrite(self):
        with self.assertRaises(Exception) as context:
            output_sys_param_file = self.output_dir / 'test_overwriting_sys_param.json'
            SystemParameters.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file,
                overwrite=True)
            SystemParameters.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file,
                overwrite=False)
        self.assertIn("Output file already exists and overwrite is False:", str(context.exception))

    def test_csv_to_sys_param(self):
        output_sys_param_file = self.output_dir / 'test_sys_param.json'
        SystemParameters.csv_to_sys_param(
            model_type='time_series',
            scenario_dir=self.scenario_dir,
            feature_file=self.feature_file,
            sys_param_filename=output_sys_param_file)
        self.assertTrue(output_sys_param_file.exists())

    def test_validate_sys_param_template(self):
        output_sys_param_file = self.output_dir / 'bogus_sys_param.json'
        with self.assertRaises(Exception) as context:
            SystemParameters.csv_to_sys_param(
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn("csv_to_sys_param() missing 1 required positional argument: 'model_type'",
                      str(context.exception))
        with self.assertRaises(Exception) as context:
            bogus_template_type = 'openstudio'
            SystemParameters.csv_to_sys_param(
                model_type=bogus_template_type,
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(f"No template found. {bogus_template_type} is not a valid template", str(context.exception))
