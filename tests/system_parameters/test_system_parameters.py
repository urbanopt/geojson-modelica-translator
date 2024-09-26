# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
import os
import unittest
from pathlib import Path
from shutil import rmtree

import pytest

from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters


class SystemParametersTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        self.weather_dir = self.output_dir / "weatherfiles"
        self.scenario_dir = self.data_dir / "sdk_output_skeleton" / "run" / "baseline_15min"
        self.microgrid_scenario_dir = self.data_dir / "sdk_microgrid_output_skeleton" / "run" / "reopt_scenario"
        self.microgrid_feature_file = self.data_dir / "sdk_microgrid_output_skeleton" / "example_project.json"
        self.microgrid_output_dir = Path(__file__).parent / "microgrid_output"
        self.feature_file = self.data_dir / "sdk_output_skeleton" / "example_project.json"
        self.sys_param_template = (
            Path(__file__).parent.parent.parent
            / "geojson_modelica_translator"
            / "system_parameters"
            / "time_series_template.json"
        )
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
        filename = self.data_dir / "system_params_1.json"
        sdp = SystemParameters(filename)
        for s in sdp.validate():
            print(s)
        value = sdp.get_param_by_id("ijk678", "load_model_parameters.spawn.idf_filename")
        assert Path(value) == Path(filename).parent / "example_model.idf"
        value = sdp.get_param("$.weather")
        assert Path(value) == Path(filename).parent / "../../data_shared/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos"

        # verify that the second spawn paths resolve too.
        value = sdp.get_param_by_id("lmn000", "load_model_parameters.spawn.idf_filename")
        assert Path(value) == Path(filename).parent / "example_model_2.idf"

    def test_load_system_parameters_1(self):
        filename = self.data_dir / "system_params_1.json"
        sdp = SystemParameters(filename)
        assert sdp.param_template["buildings"][1]["load_model_parameters"]["rc"]["order"] == 2

    def test_load_system_parameters_2(self):
        filename = self.data_dir / "system_params_2.json"
        sdp = SystemParameters(filename)
        assert sdp is not None

    def test_valid_system_parameters_ghe(self):
        filename = self.data_dir / "system_params_ghe.json"
        sdp = SystemParameters(filename)
        assert sdp is not None
        assert len(sdp.validate()) == 0
        assert sdp.validate() == []

    def test_error_system_parameters_ghe(self):
        filename = self.data_dir / "system_params_ghe_invalid.json"
        with pytest.raises(ValueError, match="Invalid"):
            SystemParameters(filename)

    def test_missing_file(self):
        fn = "non-existent-path"
        with pytest.raises(FileNotFoundError, match=f"System design parameters file does not exist: {fn}"):
            SystemParameters(fn)

    def test_errors(self):
        incomplete_teaser_params = {
            "buildings": [
                {
                    "geojson_id": "asdf",
                    "ets_model": "None",
                    "load_model": "rc",
                    "load_model_parameters": {"rc": {"order": 5}},
                }
            ]
        }

        with pytest.raises(ValueError, match="Invalid system parameter"):
            SystemParameters.loadd(incomplete_teaser_params)

        sp = SystemParameters.loadd(incomplete_teaser_params, validate_on_load=False)
        assert len(sp.validate()) == 6
        assert "'fraction_latent_person' is a required property" in sp.validate()
        assert "'temp_hw_supply' is a required property" in sp.validate()
        assert "'temp_setpoint_cooling' is a required property" in sp.validate()
        assert "'temp_setpoint_heating' is a required property" in sp.validate()
        assert "5 is not one of [1, 2, 3, 4]" in sp.validate()

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
                            "temp_setpoint_cooling": 24,
                        }
                    },
                }
            ],
        }
        sp = SystemParameters.loadd(data)
        value = sp.get_param("$.buildings.[*].load_model_parameters.rc.order")
        assert value == 4

        value = sp.get_param("buildings.[*].load_model")
        assert value == "rc"

        value = sp.get_param("buildings")
        assert value == [
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
                        "temp_setpoint_cooling": 24,
                    }
                },
            }
        ]

        value = sp.get_param("")
        assert value is None

        value = sp.get_param("not.a.real.path")
        assert value is None

    def test_get_param_with_building_id(self):
        filename = self.data_dir / "system_params_1.json"
        sdp = SystemParameters(filename)
        self.maxDiff = None
        value = sdp.get_param_by_id("abcd1234", "ets_model")
        assert value == "Indirect Heating and Cooling"

        # grab the schema default
        value = sdp.get_param_by_id("defgh2345", "ets_model")
        assert value == "Indirect Heating and Cooling"
        value = sdp.get_param_by_id("defgh2345", "ets_indirect_parameters")
        assert value == {
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
            "heating_controller_y_min": 0,
        }

    def test_get_param_with_ghe_id(self):
        # Setup
        filename = self.data_dir / "system_params_ghe.json"
        sdp = SystemParameters(filename)
        self.maxDiff = None

        # Act
        value = sdp.get_param_by_id("c432cb11-4813-40df-8dd4-e88f5de40033", "borehole")

        # Assert
        assert value == {"buried_depth": 2.0, "diameter": 0.15}

        # Act
        second_ghe_borehole = sdp.get_param_by_id("c432cb11-4813-40df-8dd4-e88f5de40034", "borehole")
        # Assert
        assert second_ghe_borehole["buried_depth"] == 10.0

    def test_get_param_with_none_building_id(self):
        # Setup
        filename = self.data_dir / "system_params_1.json"
        sdp = SystemParameters(filename)
        self.maxDiff = None

        # Act
        with pytest.raises(SystemExit) as context:
            sdp.get_param_by_id(None, "ets_model")

        # Assert
        assert "No id submitted. Please retry and include the appropriate id" in str(context.value)

    def test_missing_files(self):
        output_sys_param_file = self.output_dir / "going_to_fail_first.json"
        missing_scenario_dir = self.scenario_dir / "foobar"
        sp = SystemParameters()
        with pytest.raises(SystemExit) as context:
            sp.csv_to_sys_param(
                model_type="time_series",
                scenario_dir=missing_scenario_dir,
                feature_file=self.feature_file,
                district_type="4G",
                sys_param_filename=output_sys_param_file,
            )
        assert f"Unable to find your scenario. The path you provided was: {missing_scenario_dir}" in str(context.value)
        missing_feature_file = self.data_dir / "sdk_output_skeleton" / "foobar.json"
        sp = SystemParameters()
        with pytest.raises(SystemExit) as context:
            sp.csv_to_sys_param(
                model_type="time_series",
                scenario_dir=self.scenario_dir,
                feature_file=missing_feature_file,
                district_type="4G",
                sys_param_filename=output_sys_param_file,
            )
        assert f"Unable to find your feature file. The path you provided was: {missing_feature_file}" in str(
            context.value
        )

    def test_csv_to_sys_param_does_not_overwrite(self):
        output_sys_param_file = self.output_dir / "test_overwriting_sys_param.json"
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type="time_series",
            scenario_dir=self.scenario_dir,
            feature_file=self.feature_file,
            district_type="4G",
            sys_param_filename=output_sys_param_file,
            overwrite=True,
        )
        with pytest.raises(SystemExit) as context:
            sp.csv_to_sys_param(
                model_type="time_series",
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                sys_param_filename=output_sys_param_file,
                overwrite=False,
            )
        assert "Output file already exists and overwrite is False:" in str(context.value)

    def test_csv_to_sys_param(self):
        output_sys_param_file = self.output_dir / "test_sys_param.json"
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type="time_series",
            scenario_dir=self.scenario_dir,
            feature_file=self.feature_file,
            sys_param_filename=output_sys_param_file,
        )

        # debug
        # with open(output_sys_param_file, "r") as f:
        #     sys_param_data = json.load(f)
        #     print(sys_param_data)

        assert output_sys_param_file.is_file()

    def test_csv_to_sys_param_ghe(self):
        output_sys_param_file = self.output_dir / "test_sys_param.json"
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type="time_series",
            scenario_dir=self.scenario_dir,
            feature_file=self.feature_file,
            district_type="5G_ghe",
            sys_param_filename=output_sys_param_file,
        )

        assert output_sys_param_file.is_file()
        with open(output_sys_param_file) as f:
            sys_param_data = json.load(f)

        # ghe
        assert sys_param_data["district_system"]["fifth_generation"]["ghe_parameters"] is not False

    def test_csv_to_sys_param_microgrid(self):
        output_sys_param_file = self.microgrid_output_dir / "test_sys_param_microgrid.json"
        sp = SystemParameters()
        sp.csv_to_sys_param(
            model_type="time_series",
            scenario_dir=self.microgrid_scenario_dir,
            feature_file=self.microgrid_feature_file,
            district_type="4G",
            sys_param_filename=output_sys_param_file,
            microgrid=True,
        )
        assert output_sys_param_file.exists()

        with open(output_sys_param_file) as f:
            sys_param_data = json.load(f)

        # pv on a building
        assert len(sys_param_data["buildings"][0]["photovoltaic_panels"]) > 0
        # pv for the district
        assert len(sys_param_data["photovoltaic_panels"]) > 0
        assert len(sys_param_data["wind_turbines"]) > 0
        assert sys_param_data["electrical_grid"]["frequency"] is not False

        # assert that a building has a 'photovoltaic_panels' section (exists and nonempty)
        assert sys_param_data["buildings"][0]["photovoltaic_panels"] is not False

        # assert that building_id 7 (number 1 in the list) has an electrical load
        # Building 1 (number 0 in the list) does not have an electrical load as of 2023-03-07
        assert sys_param_data["buildings"][1]["load_model_parameters"]["time_series"]["max_electrical_load"] > 0

    def test_validate_sys_param_template(self):
        output_sys_param_file = self.output_dir / "bogus_sys_param.json"
        sp = SystemParameters()
        with pytest.raises(TypeError) as context:
            sp.csv_to_sys_param(
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                district_type="4G",
                sys_param_filename=output_sys_param_file,
            )
        assert "missing 1 required positional argument: 'model_type'" in str(context.value)
        bogus_template_type = "openstudio"
        sp = SystemParameters()
        with pytest.raises(SystemExit) as context:
            sp.csv_to_sys_param(
                model_type=bogus_template_type,
                scenario_dir=self.scenario_dir,
                feature_file=self.feature_file,
                district_type="4G",
                sys_param_filename=output_sys_param_file,
            )
        assert f"No template found. {bogus_template_type} is not a valid template" in str(context.value)

    def test_download_usa_mos(self):
        sdp = SystemParameters()
        print(f"saving results to f{self.weather_dir}")

        weather_filename = "USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos"
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        assert (Path(self.weather_dir) / weather_filename).exists()

    def test_download_usa_epw(self):
        sdp = SystemParameters()
        print(f"saving results to f{self.weather_dir}")
        weather_filename = "USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.epw"
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        assert (Path(self.weather_dir) / weather_filename).exists()

    def test_download_german_epw(self):
        sdp = SystemParameters()
        print(f"saving results to f{self.weather_dir}")
        weather_filename = "DEU_Stuttgart.107380_IWEC.epw"
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        assert (Path(self.weather_dir) / weather_filename).exists()

    def test_download_german_mos(self):
        sdp = SystemParameters()
        print(f"saving results to f{self.weather_dir}")
        weather_filename = "DEU_Stuttgart.107380_IWEC.mos"
        sdp.download_weatherfile(weather_filename, self.weather_dir)
        assert (Path(self.weather_dir) / weather_filename).exists()

    def test_download_invalid_savepath(self):
        sdp = SystemParameters()
        weather_filename = "irrelevant weather file"
        local_path = os.path.join("not", "a", "real", "path")
        with pytest.raises(IndexError) as context:
            sdp.download_weatherfile(weather_filename, local_path)
        assert (
            str(context.value) == "Malformed location, needs underscores of location "
            "(e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)"
        )

    def test_download_invalid_epw(self):
        sdp = SystemParameters()
        weather_filename = "invalid-location.epw"
        with pytest.raises(IndexError) as context:
            sdp.download_weatherfile(weather_filename, self.weather_dir)
        assert (
            str(context.value) == "Malformed location, needs underscores of location "
            "(e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)"
        )
