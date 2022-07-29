"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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
        if os.path.exists(self.run_path):
            shutil.rmtree(self.run_path)
        if os.path.exists(self.fmu_run_path):
            shutil.rmtree(self.fmu_run_path)
        os.makedirs(self.run_path)
        os.makedirs(self.fmu_run_path)

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
        self.assertTrue(os.path.exists(mr.spawn_docker_path))

    def test_docker_enabled(self):
        mr = ModelicaRunner()
        self.assertTrue(mr.docker_configured, 'Docker is not running, unable to run all tests')

    def test_invalid_action(self):
        mr = ModelicaRunner()
        with self.assertRaises(AssertionError) as excinfo:
            mr._subprocess_call_to_docker(None, None, 'unreal')
        self.assertIn('unreal', str(excinfo.exception))
        self.assertIn('needs to be [\'compile_and_run\'', str(excinfo.exception))

    @pytest.mark.simulation
    def test_run_in_docker_errors(self):
        mr = ModelicaRunner()
        file_to_run = os.path.join(self.run_path, 'no_file.mo')
        with self.assertRaises(SystemExit) as exc:
            mr.run_in_docker(file_to_run)
        self.assertEqual(f'File not found to run {file_to_run}', str(exc.exception))

        file_to_run = os.path.join(self.run_path)
        with self.assertRaises(SystemExit) as exc:
            mr.run_in_docker(file_to_run)
        self.assertEqual(f'Expecting to run a file, not a folder in {file_to_run}', str(exc.exception))

    @pytest.mark.simulation
    def test_run_in_docker(self):
        mr = ModelicaRunner()
        mr.run_in_docker(os.path.join(self.run_path, 'BouncingBall.mo'))

        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_result.mat')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'spawn_docker.sh')))
        
    @pytest.mark.compilation
    def test_compile_in_docker(self):
        # cleanup output path
        results_path = os.path.join(self.run_path, 'BouncingBall_results')
        shutil.rmtree(results_path, ignore_errors=True)
        # remove old FMU
        fmu_path = os.path.join(self.run_path, 'BouncingBall.fmu')
        if os.path.exists(fmu_path):
            os.remove(fmu_path)
        if os.path.exists(os.path.join(self.run_path, 'stdout.log')):
            os.remove(os.path.join(self.run_path, 'stdout.log'))

        # compile the project
        mr = ModelicaRunner()
        mr.compile_in_docker(os.path.join(self.run_path, 'BouncingBall.mo'))
        
        
        self.assertTrue(os.path.exists(os.path.join(self.run_path, 'stdout.log')))
        # Write out the log to the logger for debugging
        with open(os.path.join(self.run_path, 'stdout.log')) as f:
            logger.info(f.read())
        self.assertFalse(os.path.exists(os.path.join(results_path, 'spawn_docker.sh')))
        self.assertTrue(os.path.exists(fmu_path))
        
        
        
    @pytest.mark.simulation
    def test_run_only_in_docker(self):
        # cleanup output path
        results_path = os.path.join(self.fmu_run_path, 'BouncingBall_results')
        shutil.rmtree(results_path, ignore_errors=True)

        # run the project
        mr = ModelicaRunner()
        mr.run_fmu_in_docker(os.path.join(self.fmu_run_path, 'BouncingBall.fmu'))

        self.assertTrue(os.path.exists(os.path.join(results_path, 'stdout.log')))
        self.assertTrue(os.path.exists(os.path.join(results_path, 'BouncingBall_result.mat')))
        self.assertFalse(os.path.exists(os.path.join(results_path, 'spawn_docker.sh')))
