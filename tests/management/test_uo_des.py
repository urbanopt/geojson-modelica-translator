from pathlib import Path
from shutil import rmtree
from subprocess import run
from unittest import TestCase

# Integration tests that the CLI works as expected for an end user


class CLIIntegrationTest(TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.scenario_file_path = self.data_dir / 'sdk_project_scraps' / 'baseline_scenario.csv'
        self.feature_file_path = self.data_dir / 'sdk_project_scraps' / 'example_project.json'

    def test_cli_builds_sys_params(self):
        # In python 3.8 we can drop the if statement and simplify this to "my_file.unlink(missing_ok=True)"
        if (self.output_dir / 'test_sys_param.json').exists():
            (self.output_dir / 'test_sys_param.json').unlink()

        # run subprocess as if we're an end-user
        run(['uo_des', 'build-sys-param', self.output_dir / 'test_sys_param.json',
             self.scenario_file_path, self.feature_file_path])

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'test_sys_param.json').exists()

    def test_cli_makes_model(self):
        if (self.output_dir / 'modelica_project' / 'Districts' / 'DistrictEnergySystem.mo').exists():
            rmtree(self.output_dir / 'modelica_project')

        # run subprocess as if we're an end-user
        run(['uo_des', 'create-model', self.output_dir / 'test_sys_param.json',
             self.feature_file_path, self.output_dir / 'modelica_project'])

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project' / 'Districts' / 'DistrictEnergySystem.mo').exists()

    def test_cli_overwrites_properly(self):
        # run subprocess as if we're an end-user, expecting to hit error message
        project_name = 'modelica_project'
        no_overwrite_result = run(['uo_des', 'create-model', self.output_dir / 'test_sys_param.json',
                                   self.feature_file_path, self.output_dir / project_name], capture_output=True)
        assert no_overwrite_result.returncode != 0
        self.assertIn("already exists and overwrite flag is not given", no_overwrite_result.stderr.decode())

        # Run subprocess with overwrite flag, expect it to write new files without errors
        run(['uo_des', 'create-model', self.output_dir / 'test_sys_param.json',
             self.feature_file_path, self.output_dir / project_name, '--overwrite'])

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project' / 'Districts' / 'DistrictEnergySystem.mo').exists()

    def test_cli_runs_model(self):
        if (self.output_dir / 'modelica_project_results').exists():
            rmtree(self.output_dir / 'modelica_project_results')

        # run subprocess as if we're an end-user
        run(['uo_des', 'run-model', self.output_dir / 'modelica_project'])

        # If this file exists, the cli command ran successfully
        assert (self.output_dir / 'modelica_project_results' / 'modelica_project_Districts_DistrictEnergySystem_result.mat').exists()
