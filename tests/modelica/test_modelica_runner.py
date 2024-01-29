# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import shutil
import unittest
import logging
import inspect
import pytest

from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from pathlib import Path

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

    @pytest.mark.docker
    def test_docker_enabled(self):
        mr = ModelicaRunner()
        self.assertTrue(mr.docker_configured, 'Docker is not running, unable to run all tests')

    @pytest.mark.docker
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

    @pytest.mark.compilation
    def test_compile_bouncing_ball_in_docker(self):
        # cleanup output path
        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        shutil.rmtree(results_path, ignore_errors=True)

        # compile the project
        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile', 'BouncingBall',
                         file_to_load = os.path.join(self.run_path, 'BouncingBall.mo'),
                         run_path=self.run_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall.fmu')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        # Write out the log to the logger for debugging
        # with open(os.path.join(self.run_path, 'stdout.log')) as f:
            # logger.info(f.read())
        self.assertFalse(os.path.exists(os.path.join(results_path, 'compile_fmu.mos')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'simulate.mos')))

    @pytest.mark.simulation
    def test_simulate_bouncing_ball_in_docker(self):
        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile_and_run', 'BouncingBall',
                         file_to_load = os.path.join(self.run_path, 'BouncingBall.mo'),
                         run_path=self.run_path)

        self.assertTrue(success)

        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_res.mat')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'om_docker.sh')))

    @pytest.mark.simulation
    @pytest.mark.skip(reason='Need to install libfortran.so.4 in docker image')
    def test_simulate_fmu_in_docker(self):
        # TODO: this breaks at the moment due to the libfortran.so.4 error.
        # cleanup output path
        results_path = os.path.join(self.fmu_run_path, 'BouncingBall_results')
        shutil.rmtree(results_path, ignore_errors=True)

        # run the project
        mr = ModelicaRunner()
        mr.run_in_docker('run', 'BouncingBall',
                         file_to_load = os.path.join(self.fmu_run_path, 'BouncingBall.fmu'),
                         run_path = self.fmu_run_path)

        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_result.mat')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'om_docker.sh')))

    @pytest.mark.compilation
    def test_compile_msl_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile', model_name, run_path=self.msl_run_path, project_in_library=True)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}.fmu')))

    @pytest.mark.simulation
    def test_simulate_msl_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile_and_run', model_name, run_path=self.msl_run_path, project_in_library=True)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}_res.mat')))

    @pytest.mark.simulation
    def test_simulate_msl_with_start_times_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = os.path.join(self.msl_run_path, f"{model_name}_results")
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile_and_run', model_name,
                         run_path=self.msl_run_path, project_in_library=True,
                         start_time=0, stop_time=60, step_size=0.1)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}_res.mat')))

    @pytest.mark.simulation
    def test_simulate_msl_with_intervals_in_docker(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = Path(self.msl_run_path) / f"{model_name}_results"
        shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        success, _ = mr.run_in_docker('compile_and_run', model_name,
                         run_path=self.msl_run_path, project_in_library=True,
                         start_time=0, stop_time=60, number_of_intervals=6)

        self.assertTrue(success)
        self.assertTrue((results_path / 'stdout.log').exists())
        self.assertTrue((results_path / f'{model_name}_res.mat').exists())

    @pytest.mark.simulation
    def test_simulate_mbl_pid_in_docker(self):
        model_name = 'Buildings.Controls.OBC.CDL.Reals.Validation.PID'

        mr = ModelicaRunner()
        success, _ = mr.run_in_docker(
            'compile_and_run', model_name, run_path=self.mbl_run_path, project_in_library=True
        )
        self.assertTrue(success)

    @pytest.mark.dymola
    def test_simulate_msl_in_dymola(self):
        model_name = 'Modelica.Blocks.Examples.PID_Controller'
        results_path = Path(self.msl_run_path) / f"{inspect.currentframe().f_code.co_name}_results"
        if results_path.exists():
            shutil.rmtree(results_path, ignore_errors=True)
        results_path.mkdir(parents=True)

        # shutil.rmtree(results_path, ignore_errors=True)

        mr = ModelicaRunner()
        success, _ = mr.run_in_dymola(
            'simulate', model_name, run_path=results_path, file_to_load=None
        )

        self.assertTrue(success)
        # self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        # self.assertTrue(os.path.exists(os.path.join(results_path, f'{model_name}.fmu')))

    @pytest.mark.dymola
    def test_simulate_mbl_pid_in_dymola(self):
        results_path = Path(self.mbl_run_path) / f"{inspect.currentframe().f_code.co_name}_results"
        if results_path.exists():
            shutil.rmtree(results_path, ignore_errors=True)
        results_path.mkdir(parents=True)

        model_name = 'Buildings.Controls.OBC.CDL.Reals.Validation.PID'

        mr = ModelicaRunner()
        success, _ = mr.run_in_dymola(
            'simulate', model_name, run_path=results_path, file_to_load=None  # , debug=True
        )
        self.assertTrue(success)

    @pytest.mark.dymola
    def test_compile_mbl_pid_in_dymola(self):
        results_path = Path(self.mbl_run_path) / f"{inspect.currentframe().f_code.co_name}_results"
        if results_path.exists():
            shutil.rmtree(results_path, ignore_errors=True)
        results_path.mkdir(parents=True)

        model_name = 'Buildings.Controls.OBC.CDL.Reals.Validation.PID'

        mr = ModelicaRunner()
        success, _ = mr.run_in_dymola(
            'compile', model_name, run_path=results_path, file_to_load=None, debug=True
        )
        self.assertTrue(success)
