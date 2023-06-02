# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import shutil
import unittest
import logging

import pytest

from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class ModelicaRunnerTest(unittest.TestCase):
    def setUp(self):
        # create a run directory and copy in a project to test run
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.run_path = os.path.join(os.path.dirname(__file__), 'output', 'simdir')
        self.fmu_run_path = os.path.join(os.path.dirname(__file__), 'output', 'fmudir')
        self.mbl_run_path = os.path.join(os.path.dirname(__file__), 'output', 'mbldir')
        self.msl_run_path = os.path.join(os.path.dirname(__file__), 'output', 'msldir')

        # remove the run directory if it exists and recreate
        for p in [self.run_path, self.fmu_run_path, self.mbl_run_path, self.msl_run_path]:
            if os.path.exists(p):
                shutil.rmtree(p)
            os.makedirs(p)

        # copy in the test modelica file
        shutil.copyfile(
            os.path.join(self.data_dir, 'BouncingBall.mo'),
            os.path.join(self.run_path, 'BouncingBall.mo')
        )
        shutil.copyfile(
            os.path.join(self.data_dir, 'BouncingBall.fmu'),
            os.path.join(self.fmu_run_path, 'BouncingBall.fmu')
        )

    def test_run_setup(self):
        prev_mod_path = os.environ.get('MODELICAPATH', None)
        try:
            os.environ['MODELICAPATH'] = 'A_PATH/to_something'
            mr = ModelicaRunner()
            self.assertEqual(mr.modelica_lib_path, 'A_PATH/to_something')
        finally:
            if prev_mod_path:
                os.environ['MODELICAPATH'] = prev_mod_path
        self.assertTrue(os.path.exists(mr.om_docker_path))

    def test_docker_enabled(self):
        mr = ModelicaRunner()
        self.assertTrue(mr.docker_configured, 'Docker is not running, unable to run all tests')

    def test_invalid_action(self):
        mr = ModelicaRunner()
        with self.assertRaises(SystemExit) as excinfo:
            mr.run_in_docker('unreal', None)
        self.assertIn('unreal', str(excinfo.exception))
        self.assertIn("must be one of ['compile'", str(excinfo.exception))

    @pytest.mark.simulation
    def test_run_in_docker_errors(self):
        mr = ModelicaRunner()
        file_to_run = os.path.join(self.run_path, 'no_file.mo')
        with self.assertRaises(SystemExit) as exc:
            mr.run_in_docker('compile', 'no_file', file_to_load=file_to_run)
        self.assertEqual(f'File not found to run {file_to_run}', str(exc.exception))

    @pytest.mark.simulation
    def test_simulate_in_docker(self):
        mr = ModelicaRunner()
        mr.run_in_docker('compile_and_run', 'BouncingBall', 
                         file_to_load = os.path.join(self.run_path, 'BouncingBall.mo'), 
                         run_path=self.run_path)

        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_res.mat')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'om_docker.sh')))

    @pytest.mark.compilation
    def test_compile_in_docker(self):
        # cleanup output path
        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        shutil.rmtree(results_path, ignore_errors=True)
        
        # compile the project
        mr = ModelicaRunner()
        mr.run_in_docker('compile', 'BouncingBall', 
                         file_to_load = os.path.join(self.run_path, 'BouncingBall.mo'),
                         run_path=self.run_path)

        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall.fmu')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        # Write out the log to the logger for debugging
        # with open(os.path.join(self.run_path, 'stdout.log')) as f:
            # logger.info(f.read())
        self.assertFalse(os.path.exists(os.path.join(results_path, 'om_docker.sh')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'compile_fmu.mos')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'simulate.mos')))

    # @pytest.mark.simulation
    # def test_simulate_fmu_in_docker(self):
    #     # TODO: this breaks at the moment due to the libfortran.so.4 error.
    #     # cleanup output path
    #     results_path = os.path.join(self.fmu_run_path, 'BouncingBall_results')
    #     shutil.rmtree(results_path, ignore_errors=True)

    #     # run the project
    #     mr = ModelicaRunner()
    #     mr.run_in_docker('run', 'BouncingBall', 
    #                      file_to_load = os.path.join(self.fmu_run_path, 'BouncingBall.fmu'),
    #                      run_path = self.fmu_run_path)

    #     self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
    #     self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_result.mat')))
    #     self.assertFalse(os.path.exists(os.path.join(results_path, 'om_docker.sh')))

    @pytest.mark.simulation
    def test_simulate_mbl_in_docker(self):
        model_name = 'Buildings.Controls.OBC.CDL.Continuous.Validation.PID'
        
        mr = ModelicaRunner()
        mr.run_in_docker('compile_and_run', model_name, run_path=self.mbl_run_path, project_in_library=True)


    @pytest.mark.compilation
    def test_compile_msl_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        mr.run_in_docker('compile', model_name, run_path=self.msl_run_path, project_in_library=True)

        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}.fmu')))

    @pytest.mark.simulation
    def test_simulate_msl_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        mr.run_in_docker('compile_and_run', model_name, run_path=self.msl_run_path, project_in_library=True)

        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}_res.mat')))

    @pytest.mark.simulation
    def test_simulate_msl_with_starttimes_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        mr.run_in_docker('compile_and_run', model_name, 
                         run_path=self.msl_run_path, project_in_library=True,
                         start_time=0, stop_time=60, step_size=0.1)

        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}_res.mat')))

        