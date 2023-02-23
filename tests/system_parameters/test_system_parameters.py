# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
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
        self.weather_dir = self.output_dir / 'weatherfiles'
        self.scenario_dir = self.data_dir / 'sdk_output_skeleton' / 'run' / 'baseline_15min'
        self.microgrid_scenario_dir = self.data_dir / 'sdk_microgrid_output_skeleton' / 'run' / 'reopt_scenario'
        self.microgrid_feature_file = self.data_dir / 'sdk_microgrid_output_skeleton' / 'example_project.json'
        self.microgrid_output_dir = Path(__file__).parent / 'microgrid_output'
        self.feature_file = self.data_dir / 'sdk_output_skeleton' / 'example_project.json'
        self.sys_param_template = Path(__file__).parent.parent.parent / 'geojson_modelica_translator' / \
            'system_parameters' / 'time_series_template.json'
        if self.output_dir.exists():
            rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        if self.weather_dir.exists():
            rmtree(self.weather_dir)
        self.weather_dir.mkdir(parents=True)
        if self.microgrid_output_dir.exists():
            rmtree(self.microgrid_output_dir)
        self.microgrid_output_dir.mkdir(parents=True)

    def test_expanded_paths(self):
        filename = self.data_dir / 'system_params_1.json'
        sdp = SystemParameters(filename)
        for s in sdp.validate():
            print(s)
        value = sdp.get_param_by_building_id("ijk678", "load_model_parameters.spawn.idf_filename")
        self.assertEqual(Path(value), Path(filename).parent / 'example_model.idf')
        value = sdp.get_param("$.weather")
        self.assertEqual(Path(value), Path(filename).parent / '../../data_shared/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos')

        # verify that the second spawn paths resolve too.
        value = sdp.get_param_by_building_id("lmn000", "load_model_parameters.spawn.idf_filename")
        self.assertEqual(Path(value), Path(filename).parent / 'example_model_2.idf')

    def test_load_system_parameters_1(self):
        filename = self.data_dir / 'system_params_1.json'
        sdp = SystemParameters(filename)
        self.assertEqual(
            sdp.data["buildings"][1]["load_model_parameters"]["rc"]["order"], 2
        )

    def test_load_system_parameters_2(self):
        filename = self.data_dir / 'system_params_2.json'
        sdp = SystemParameters(filename)
        self.assertIsNotNone(sdp)

    def test_load_system_parameters_ghe(self):
        filename = self.data_dir / 'system_params_ghe.json'
        sdp = SystemParameters(filename)
        self.assertIsNotNone(sdp)
        self.assertEqual([], sdp.validate())

    def test_load_system_parameters_ghe(self):
        filename = self.data_dir / 'system_params_ghe_2.json'
        sdp = SystemParameters(filename)
        self.assertIsNotNone(sdp)
        self.assertEqual([], sdp.validate())

    def test_missing_file(self):
        fn = "non-existent-path"
        with self.assertRaises(Exception) as exc:
            SystemParameters(fn)
        self.assertEqual(
            f"System design parameters file does not exist: {fn}", str(exc.exception)
        )

    def test_errors(self):
        incomplete_teaser_params = {
            "buildings": [
                {
                    "geojson_id": "asdf",
                    "ets_model": "None",
                    "load_model": "rc",
                    "load_model_parameters": {
                        "rc": {"order": 5}},
                }
            ]
        }

        with self.assertRaises(Exception) as exc:
            SystemParameters.loadd(incomplete_teaser_params)
        self.assertRegex(str(exc.exception), "Invalid system parameter file.*")

        sp = SystemParameters.loadd(incomplete_teaser_params, validate_on_load=False)
        self.assertEqual(len(sp.validate()), 6)
        self.assertIn("'fraction_latent_person' is a required property", sp.validate())
        self.assertIn("'temp_hw_supply' is a required property", sp.validate())
        self.assertIn("'temp_setpoint_cooling' is a required property", sp.validate())
        self.assertIn("'temp_setpoint_heating' is a required property", sp.validate())
        self.assertIn("5 is not one of [1, 2, 3, 4]", sp.validate())

    def test_get_param(self):
        data = {
            "weather": "path/to/weatherfile.mos",
            "buildings": [
                {
                    "geojson_id": "asdf",
                    "ets_model": "None",
                    "load_model": "rc",
                    "load_model_parameters": {
                        "rc": {
                            "order": 4,
                            "fraction_latent_person": 1.25,
                            "temp_hw_supply": 40,
                            "temp_setpoint_heating": 40,
                            "temp_setpoint_cooling": 24
                        }
                    }
                }
            ]
        }
        sp = SystemParameters.loadd(data)
        value = sp.get_param("$.buildings.[*].load_model_parameters.rc.order")
        self.assertEqual(value, 4)

        value = sp.get_param("buildings.[*].load_model")
        self.assertEqual(value, "rc")

        value = sp.get_param("buildings")
        self.assertEqual(
            value,
            [
                {
                    "geojson_id": "asdf",
                    "ets_model": "None",
                    "load_model": "rc",
                    "load_model_parameters": {
                        "rc": {
                            "order": 4,
                            "fraction_latent_person": 1.25,
                            "temp_hw_supply": 40,
                            "temp_setpoint_heating": 40,
                            "temp_setpoint_cooling": 24
                        }
                    }
                }
            ]
        )

        value = sp.get_param("")
        self.assertIsNone(value)

        value = sp.get_param("not.a.real.path")
        self.assertIsNone(value)

    def test_get_param_with_building_id_defaults(self):
        filename = self.data_dir / 'system_params_1.json'
        sdp = SystemParameters(filename)
        self.maxDiff = None
        # ensure the defaults are respected. abcd1234 has NO metamodel defined
        value = sdp.get_param_by_building_id("abcd1234", "ets_model")
        self.assertEqual("None", value)

        # grab the schema default
        value = sdp.get_param_by_building_id("defgh2345", "ets_model")
        self.assertEqual("Indirect Heating and Cooling", value)
        value = sdp.get_param_by_building_id("defgh2345", "ets_indirect_parameters")
        self.assertEqual({
            "heat_flow_nominal": 8000,
            "heat_exchanger_efficiency": 0.8,
            "nominal_mass_flow_district": 0.5,
            "nominal_mass_flow_building": 0.5,
            "valve_pressure_drop": 6000,
            "heat_exchanger_secondary_pressure_drop": 500,
            "heat_exchanger_primary_pressure_drop": 500,
            "cooling_supply_water_temperature_building": 7,
            "heating_supply_water_temperature_building": 50,
            "delta_temp_chw_building": 5,
            "delta_temp_chw_district": 8,
            "delta_temp_hw_building": 15,
            "delta_temp_hw_district": 20,
            "cooling_controller_y_max": 1,
            "cooling_controller_y_min": 0,
            "heating_controller_y_max": 1,
            "heating_controller_y_min": 0
        }, value)

        # respect the passed default value
        # value = sdp.get_param_by_building_id("defgh2345", "ets_model_parameters.NominalFlow_Building", 24815)
        # self.assertEqual(24815, value)
        # FYI! Default sys-param values (in the sys-param file) are being eliminated in this PR

    def test_get_param_with_none_building_id(self):
        filename = self.data_dir / 'system_params_1.json'
        sdp = SystemParameters(filename)
        self.maxDiff = None
        with self.assertRaises(SystemExit) as context:
            sdp.get_param_by_building_id(None, "ets_model")
        self.assertIn("No building_id submitted. Please retry and include the feature_id", str(context.exception))

    def test_missing_files(self):
        with self.assertRaises(SystemExit) as context:
            output_sys_param_file = self.output_dir / 'going_to_fail_first.json'
            missing_scenario_dir = self.scenario_dir / 'foobar'
            sp = SystemParameters()
            sp.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=missing_scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(
            f"Unable to find your scenario. The path you provided was: {missing_scenario_dir}", str(context.exception))
        with self.assertRaises(SystemExit) as context:
            missing_feature_file = self.data_dir / 'sdk_output_skeleton' / 'foobar.json'
            sp = SystemParameters()
            sp.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=missing_feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(
            f"Unable to find your feature file. The path you provided was: {missing_feature_file}", str(context.exception))

    def test_csv_to_sys_param_does_not_overwrite(self):
        with self.assertRaises(SystemExit) as context:
            output_sys_param_file = self.output_dir / 'test_overwriting_sys_param.json'
            sp = SystemParameters()
            sp.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file,
                overwrite=True)
            sp = SystemParameters()
            sp.csv_to_sys_param(
                model_type='time_series',
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file,
                overwrite=False)
        self.assertIn("Output file already exists and overwrite is False:", str(context.exception))

    def test_csv_to_sys_param(self):
        output_sys_param_file = self.output_dir / 'test_sys_param.json'
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type='time_series',
            scenario_dir=self.scenario_dir,
            feature_file=self.feature_file,
            sys_param_filename=output_sys_param_file)

        # debug
        # with open(output_sys_param_file, "r") as f:
        #     sys_param_data = json.load(f)
        #     print(sys_param_data)

        self.assertTrue(output_sys_param_file.is_file())

    def test_csv_to_sys_param_microgrid(self):
        output_sys_param_file = self.microgrid_output_dir / 'test_sys_param_microgrid.json'
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type='time_series',
            scenario_dir=self.microgrid_scenario_dir,
            feature_file=self.microgrid_feature_file,
            sys_param_filename=output_sys_param_file,
            microgrid=True)
        self.assertTrue(output_sys_param_file.exists())

        with open(output_sys_param_file, "r") as f:
            sys_param_data = json.load(f)

        # pv on a building
        self.assertTrue(len(sys_param_data['buildings'][0]['photovoltaic_panels']) > 0)
        # pv for the district
        self.assertTrue(len(sys_param_data['photovoltaic_panels']) > 0)
        self.assertTrue(len(sys_param_data['wind_turbines']) > 0)
        self.assertTrue(sys_param_data['electrical_grid']['frequency'])

        # assert that a building has a 'photovoltaic_panels' section (exists and nonempty)
        self.assertTrue(sys_param_data['buildings'][0]['photovoltaic_panels'])

    def test_validate_sys_param_template(self):
        output_sys_param_file = self.output_dir / 'bogus_sys_param.json'
        with self.assertRaises(Exception) as context:
            sp = SystemParameters()
            sp.csv_to_sys_param(
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn("csv_to_sys_param() missing 1 required positional argument: 'model_type'",
                      str(context.exception))
        with self.assertRaises(SystemExit) as context:
            bogus_template_type = 'openstudio'
            sp = SystemParameters()
            sp.csv_to_sys_param(
                model_type=bogus_template_type,
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file)
        self.assertIn(f"No template found. {bogus_template_type} is not a valid template", str(context.exception))

    def test_download_mos(self):
        sdp = SystemParameters()
        print(f"saving results to f{self.weather_dir}")
        weather_filename = 'USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.epw'
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        self.assertTrue(os.path.exists(os.path.join(self.weather_dir, weather_filename)))

        weather_filename = 'USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos'
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        self.assertTrue(os.path.exists(os.path.join(self.weather_dir, weather_filename)))

    def test_download_invalid_savepath(self):
        sdp = SystemParameters()
        weather_filename = 'irrelevant weather file'
        local_path = os.path.join('not', 'a', 'real', 'path')
        with self.assertRaises(Exception) as context:
            sdp.download_weatherfile(weather_filename, local_path)
        self.assertEqual("Malformed location, needs underscores of location "
                         "(e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)",
                         str(context.exception))

    def test_download_invalid_epw(self):
        sdp = SystemParameters()
        weather_filename = 'invalid-location.epw'
        with self.assertRaises(Exception) as context:
            sdp.download_weatherfile(weather_filename, self.weather_dir)
        self.assertEqual(
            "Malformed location, needs underscores of location (e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)",
            str(context.exception))
