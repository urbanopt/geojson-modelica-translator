from pathlib import Path
from shutil import rmtree
from unittest import TestCase

import pytest
from click.testing import CliRunner
from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from management.uo_des import cli

# Integration tests that the CLI works as expected for an end user


class CLIIntegrationTest(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.output_dir.mkdir(exist_ok=True)
        self.scenario_file_path = self.data_dir / 'sdk_project_scraps' / 'baseline_scenario.csv'
        self.feature_file_path = self.data_dir / 'sdk_project_scraps' / 'example_project.json'

    def test_cli_builds_sys_params(self):
        # In python 3.8 we can drop the if statement and simplify this to "my_file.unlink(missing_ok=True)"
        if (self.output_dir / 'test_sys_param.json').exists():
            (self.output_dir / 'test_sys_param.json').unlink()

        # run subprocess as if we're an end-user
        res = self.runner.invoke(
            cli,
            [
                'build-sys-param',
                str((self.output_dir / 'test_sys_param.json').resolve()),
                str(self.scenario_file_path.resolve()),
                str(self.feature_file_path.resolve())
            ]
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'test_sys_param.json').exists()

    def test_cli_makes_model(self):
        # WARNING: This test assumes test_cli_builds_sys_params has already run
        # successfully! This test should be refactored to avoid this

        # -- Setup
        # first verify the package can be generated without the CLI (ie verify our
        # files are valid)
        project_name = 'modelica_project'
        if (self.output_dir / project_name).exists():
            rmtree(self.output_dir / project_name)

        sys_params_filepath = self.output_dir / 'test_sys_param.json'
        geojson_filepath = self.feature_file_path

        gmt = GeoJsonModelicaTranslator(
            geojson_filepath,
            sys_params_filepath,
            self.output_dir,
            project_name,
        )

        gmt.to_modelica()

        # great! we know our files are good, let's cleanup and test the CLI
        rmtree(self.output_dir / project_name)

        # -- Act
        res = self.runner.invoke(
            cli,
            [
                'create-model',
                str(sys_params_filepath),
                str(geojson_filepath),
                str(self.output_dir / project_name)
            ]
        )

        assert res.exit_code == 0

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project' / 'Districts' / 'DistrictEnergySystem.mo').exists()

    def test_cli_overwrites_properly(self):
        # run subprocess as if we're an end-user, expecting to hit error message
        project_name = 'modelica_project'
        (self.output_dir / project_name).mkdir(exist_ok=True)

        no_overwrite_result = self.runner.invoke(
            cli,
            [
                'create-model',
                str(self.output_dir / 'test_sys_param.json'),
                str(self.feature_file_path),
                str(self.output_dir / project_name)
            ]
        )

        assert no_overwrite_result.exit_code != 0
        self.assertIn("already exists and overwrite flag is not given", str(no_overwrite_result.exception))

        # Run subprocess with overwrite flag, expect it to write new files without errors
        self.runner.invoke(
            cli,
            [
                'create-model',
                str(self.output_dir / 'test_sys_param.json'),
                str(self.feature_file_path),
                str(self.output_dir / project_name),
                '--overwrite'
            ]
        )

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project' / 'Districts' / 'DistrictEnergySystem.mo').exists()

    @pytest.mark.simulation
    def test_cli_runs_model(self):
        if (self.output_dir / 'modelica_project_results').exists():
            rmtree(self.output_dir / 'modelica_project_results')

        # run subprocess as if we're an end-user
        self.runner.invoke(
            cli,
            [
                'run-model',
                str(self.output_dir / 'modelica_project')
            ]
        )

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project_results' / 'modelica_project_Districts_DistrictEnergySystem_result.mat').exists()
