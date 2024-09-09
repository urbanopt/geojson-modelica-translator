# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from shutil import rmtree
from unittest import TestCase

import pytest
from click.testing import CliRunner

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator
from management.uo_des import cli

# Integration tests that the CLI works as expected for an end user


class CLIIntegrationTest(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.scenario_file_path = self.data_dir / "sdk_project_scraps" / "baseline_scenario.csv"
        self.feature_file_path = self.data_dir / "sdk_project_scraps" / "example_project.json"
        self.feature_file_path_ghe = self.data_dir / "sdk_project_scraps" / "example_project_combine_GHE.json"
        self.feature_file_path_germany = self.data_dir / "sdk_project_scraps" / "example_project_germany_ghe.json"
        self.sys_param_path = (
            self.data_dir / "sdk_project_scraps" / "run" / "baseline_scenario" / "system_parameter.json"
        )
        self.day_200_in_seconds = 17280000  # in seconds
        self.day_201_in_seconds = 17366400  # in seconds
        self.step_size_90_seconds = 90  # in seconds

    def test_cli_builds_sys_params(self):
        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path.resolve()),
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert self.sys_param_path.exists()

    def test_cli_builds_sys_params_with_ghe(self):
        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path_ghe.resolve()),
                "5G_ghe",
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert self.sys_param_path.exists()

    def test_cli_builds_sys_params_with_german_weatherfile(self):
        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path_germany.resolve()),
                "5G_ghe",
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert self.sys_param_path.exists()

    def test_cli_makes_model(self):
        # -- Setup
        # Gnerate a sys-params file using the CLI
        project_name = "modelica_project_4g"
        if (self.output_dir / project_name).exists():
            rmtree(self.output_dir / project_name)

        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path.resolve()),
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli successfully built the system parameter file
        assert self.sys_param_path.exists()

        # Next, verify the package can be generated without the CLI (verify our files are valid)

        gmt = GeoJsonModelicaTranslator(
            self.feature_file_path,
            self.sys_param_path,
            self.output_dir,
            project_name,
        )

        gmt.to_modelica()

        # If this file exists, the cli successfully built the model
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()
        # Great! We know our files are good, let's cleanup and test the CLI
        rmtree(self.output_dir / project_name)

        # -- Act
        res = self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path),
                str(self.output_dir / project_name),
            ],
        )

        # -- Assert
        assert res.exit_code == 0
        # If this file exists, the cli successfully built the model
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()

    def test_cli_makes_model_with_ghe(self):
        # -- Setup
        # first verify the package can be generated without the CLI (ie verify our
        # files are valid)
        project_name = "modelica_project_5g"
        if (self.output_dir / project_name).exists():
            rmtree(self.output_dir / project_name)

        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path_ghe.resolve()),
                "5G_ghe",
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert self.sys_param_path.exists()

        # FIXME : we need error handling when system parameter is created for fifth gen GHE system.
        #  Currently this method raises an error : 'dict object' has no attribute 'temp_setpoint_chw'
        gmt = GeoJsonModelicaTranslator(
            self.feature_file_path_ghe,
            self.sys_param_path,
            self.output_dir,
            project_name,
        )

        gmt.to_modelica()

        # If this file exists, the cli successfully built the model
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()
        # Great! We know our files are good, let's cleanup and test the CLI
        rmtree(self.output_dir / project_name)

        # -- Act
        res = self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path_ghe),
                str(self.output_dir / project_name),
            ],
        )

        # -- Assert
        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()

    def test_cli_makes_model_with_german_weather(self):
        # -- Setup
        # first verify the package can be generated without the CLI (ie verify our
        # files are valid)
        project_name = "modelica_project_germany"
        if (self.output_dir / project_name).exists():
            rmtree(self.output_dir / project_name)

        self.sys_param_path.unlink(missing_ok=True)

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                "build-sys-param",
                str(self.sys_param_path),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path_germany.resolve()),
                "5G_ghe",
            ],
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert self.sys_param_path.exists()

        gmt = GeoJsonModelicaTranslator(
            self.feature_file_path_germany,
            self.sys_param_path,
            self.output_dir,
            project_name,
        )

        gmt.to_modelica()

        # If this file exists, the cli successfully built the model
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()
        # Great! We know our files are good, let's cleanup and test the CLI
        rmtree(self.output_dir / project_name)

        # -- Act
        res = self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path_germany),
                str(self.output_dir / project_name),
            ],
        )

        # -- Assert
        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()

    def test_cli_overwrites_properly(self):
        # run subprocess as if we're an end-user, expecting to hit error message
        project_name = "modelica_project"
        (self.output_dir / project_name).mkdir(exist_ok=True)

        no_overwrite_result = self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path_ghe),
                str(self.output_dir / project_name),
            ],
        )

        assert no_overwrite_result.exit_code != 0
        assert "already exists and overwrite flag is not given" in str(no_overwrite_result.exception)

        # Run subprocess with overwrite flag, expect it to write new files without errors
        self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path_ghe),
                str(self.output_dir / project_name),
                "--overwrite",
            ],
        )

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / project_name / "Districts" / "DistrictEnergySystem.mo").exists()

    def test_cli_returns_graceful_error_on_space(self):
        bad_project_name = "modelica project"
        # (self.output_dir / bad_project_name).mkdir(exist_ok=True)

        expected_failure = self.runner.invoke(
            cli,
            [
                "create-model",
                str(self.sys_param_path),
                str(self.feature_file_path),
                str(self.output_dir / bad_project_name),
            ],
        )

        assert expected_failure.exit_code != 0
        assert "Modelica does not support spaces in project names or paths." in str(expected_failure.exception)

    @pytest.mark.simulation()
    def test_cli_runs_existing_4g_model(self):
        project_name = "modelica_project_4g"
        results_dir = f"{project_name}.Districts.DistrictEnergySystem_results"
        if (self.output_dir / project_name / results_dir).exists():
            rmtree(self.output_dir / project_name / results_dir)

        # run subprocess as if we're an end-user
        self.runner.invoke(
            cli,
            [
                "run-model",
                str(self.output_dir / project_name),
                "-a",
                str(self.day_200_in_seconds),
                "-z",
                str(self.day_201_in_seconds),
                "-x",
                str(self.step_size_90_seconds),
            ],
        )

        # If this file exists, the cli command ran successfully
        assert (
            self.output_dir / project_name / results_dir / f"{project_name}.Districts.DistrictEnergySystem_res.mat"
        ).exists()

    @pytest.mark.simulation()
    def test_cli_runs_existing_5g_model(self):
        project_name = "modelica_project_5g"
        results_dir = f"{project_name}.Districts.DistrictEnergySystem_results"
        if (self.output_dir / project_name / results_dir).exists():
            rmtree(self.output_dir / project_name / results_dir)

        # run subprocess as if we're an end-user
        self.runner.invoke(
            cli,
            [
                "run-model",
                str(self.output_dir / project_name),
                "-a",
                str(self.day_200_in_seconds),
                "-z",
                str(self.day_201_in_seconds),
                "-x",
                str(self.step_size_90_seconds),
            ],
        )

        # If this file exists, the cli command ran successfully
        assert (
            self.output_dir / project_name / results_dir / f"{project_name}.Districts.DistrictEnergySystem_res.mat"
        ).exists()
