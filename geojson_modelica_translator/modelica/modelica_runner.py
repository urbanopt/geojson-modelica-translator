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

import logging
import os
import shutil
import subprocess
from ast import Str
from glob import glob
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class ModelicaRunner(object):
    """
    Class to run Modelica models. This is a very simple implementation of what needs to be
    a full CLI to run Modelica easily. At the moment, this probably only works on Linux/Mac
    and perhaps in Windows with Docker.
    For Ubuntu, here is the installation instruction: https://docs.docker.com/engine/install/ubuntu/

    # TODO: test in windows
    # Document how to install Docker
    """

    def __init__(self, modelica_lib_path=None):
        """
        Initialize the runner with data needed for simulation

        :param modelica_lib_path: string, Path to the MBL to run against
        """
        # check if the user has defined a MODELICAPATH, is so, then use that.
        if os.environ.get('MODELICAPATH', None):
            print('Using predefined MODELICAPATH')
            self.modelica_lib_path = os.environ['MODELICAPATH']
            logger.debug(f'MODELICAPATH: {self.modelica_lib_path}')
        else:
            self.modelica_lib_path = modelica_lib_path
        local_path = os.path.dirname(os.path.abspath(__file__))
        self.jmodelica_py_path = os.path.join(local_path, 'lib', 'runner', 'jmodelica.py')
        self.jm_ipython_path = os.path.join(local_path, 'lib', 'runner', 'jm_ipython.sh')

        # Verify that docker is up and running
        r = subprocess.call(['docker', 'ps'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.docker_configured = r == 0

    def _verify_docker_run_capability(self, file_to_run):
        if not self.docker_configured:
            raise SystemExit('Docker not configured on host computer, unable to run')

        if not os.path.exists(file_to_run):
            raise SystemExit(f'File not found to run {file_to_run}')

        if not os.path.isfile(file_to_run):
            raise SystemExit(f'Expecting to run a file, not a folder in {file_to_run}')

    def _verify_run_path_for_docker(self, run_path: Str, file_to_run: Str) -> Path:
        """if there is no run_path, then run it in the same directory as the
        file being run. This works fine for simple Modelica projects but typically
        the run_path needs to be a few levels higher in order to include other
        project dependencies (e.g., multiple mo files).
        """
        if not run_path:
            run_path = os.path.dirname(file_to_run)
        run_path = Path(run_path)

        # Modelica can't handle spaces in project name or path
        if (len(str(run_path).split()) > 1) or (len(str(file_to_run).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{run_path}' for run path and {file_to_run} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")
        return run_path

    def _copy_over_docker_resources(self, run_path: Path) -> None:
        """Copy over ipython and jmodelica needed to run the simulation
        """
        new_jm_ipython = os.path.join(run_path, os.path.basename(self.jm_ipython_path))
        shutil.copyfile(self.jm_ipython_path, new_jm_ipython)
        os.chmod(new_jm_ipython, 0o775)
        shutil.copyfile(self.jmodelica_py_path, os.path.join(run_path, os.path.basename(self.jmodelica_py_path)))

    def _subprocess_call_to_docker(self, run_path: Path, file_to_run: Str, action: Str) -> int:
        """Call out to a subprocess to run the command in docker

        :param file_to_run: string, name of the file or directory to simulate
        :param run_path: string, location where the Modelica simulatio or compilation will start
        :param action: string, action to run either compile_and_run, compile, or run
        :returns: int, exit code of the subprocess
        """
        action_log_map = {
            'compile_and_run': 'Compiling mo file and running FMU',
            'compile': 'Compiling mo file',
            'run': 'Running FMU',
        }
        # Verify that the action is in the list of valid actions
        assert action in action_log_map.keys(), \
            f'Invalid action of {action} in _subprocess_call_to_docker, needs to be {[k for k in action_log_map.keys()]}'

        # Set up the run content
        curdir = os.getcwd()
        os.chdir(run_path)
        stdout_log = open('stdout.log', 'w')
        try:
            # get the relative difference between the file to run and the path which everything is running in.
            # make sure to simulate at a directory above the project directory!

            # Use slashes for the location of the model to run. We can make these periods `.replace(os.sep, '.')`
            # but must strip off the .mo extension on the model to run
            run_model = os.path.relpath(file_to_run, run_path)
            logger.info(f"{action_log_map[action]}: {run_model} in {run_path}")
            p = subprocess.Popen(
                ['./jm_ipython.sh', 'jmodelica.py', action, run_model],
                stdout=stdout_log,
                stderr=subprocess.STDOUT,
                cwd=run_path
            )
            logger.debug(f"Subprocess command executed, waiting for completion... \nArgs used: {p.args}")
            exitcode = p.wait()
        finally:
            os.chdir(curdir)
            stdout_log.close()
            logger.debug('Closed stdout.log')

        return exitcode

    def run_in_docker(self, file_to_run: Str, run_path: Str = None, project_name: Str = None) -> Union[bool, str]:
        """
        Run the Modelica project in a docker-based environment. Results are saved into the path of the
        file that was selected to run.

        stdout.log will store both stdout and stderr of the simulations

        :param file_to_run: string, name of the file (could be directory?) to simulate
        :param run_path: string, location where the Modelica simulation will start
        :param project_name: string, name of the project being simulated. Will be used to determine name of results
                                     directory
        :returns: tuple(bool, str), success status and path to the results directory
        """
        self._verify_docker_run_capability(file_to_run)
        run_path = self._verify_run_path_for_docker(run_path, file_to_run)

        if not project_name:
            project_name = os.path.splitext(os.path.basename(file_to_run))[0]

        self._copy_over_docker_resources(run_path)

        exitcode = self._subprocess_call_to_docker(run_path, file_to_run, 'compile_and_run')

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(run_path)

        logger.debug('moving results to results directory')
        # get the location of the results path
        results_path = Path(run_path / f'{project_name}_results')
        self.move_results(run_path, results_path, project_name)
        return (exitcode == 0, results_path)

    def compile_in_docker(self, file_to_run: Str, save_path: Str = None) -> bool:
        """Build/compile the Modelica project in a docker-based environment using JModelica. The resulting
        FMU is saved to the save_path.

        stdout.log will store both stdout and stderr of the simulations

        :param file_to_run: string, name of the file (could be directory?) to simulate
        :param run_psave_pathath: string, location where the Modelica FMU will be saved
        :returns: bool, success status
        """
        self._verify_docker_run_capability(file_to_run)
        save_path = self._verify_run_path_for_docker(save_path, file_to_run)

        self._copy_over_docker_resources(save_path)

        exitcode = self._subprocess_call_to_docker(save_path, file_to_run, 'compile')

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(save_path)

        logger.debug('moving results to results directory')
        return exitcode == 0

    def run_fmu_in_docker(self, file_to_run: Str, run_path: Str = None):
        """Run the FMU in a docker-based environment. Results are saved into the path of the
        file that was selected to run.

        stdout.log will store both stdout and stderr of the simulations

        :param file_to_run: string, name of the file (could be directory?) to simulate
        :param run_path: string, location where the Modelica simulation will start
        :param project_name: string, name of the project being simulated. Will be used to determine name of results
                                     directory
        :return: tuple(bool, str), success status and path to the results directory
        """
        self._verify_docker_run_capability(file_to_run)
        run_path = self._verify_run_path_for_docker(run_path, file_to_run)
        project_name = os.path.splitext(os.path.basename(file_to_run))[0]

        self._copy_over_docker_resources(run_path)

        exitcode = self._subprocess_call_to_docker(run_path, file_to_run, 'run')

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(run_path)

        logger.debug('moving results to results directory')
        # get the location of the results path
        results_path = Path(run_path / f'{project_name}_results')
        self.move_results(run_path, results_path, project_name)
        return (exitcode == 0, results_path)

    def move_results(self, from_path: Path, to_path: Path, project_name: Str = None) -> None:
        """This method moves the results of the simulation that are known for now.
        This method moves only specific files (stdout.log for now), plus all files and folders beginning
        with the "{project_name}_" name.

        :param from_path: pathlib.Path, where the files will move from
        :param to_path: pathlib.Path, where the files will be saved. Will be created if does not exist.
        :param project_name: string, name of the project ran in run_in_docker method
        :return: None
        """
        # if there are results, they will simply be overwritten (for now).
        to_path.mkdir(parents=True, exist_ok=True)

        files_to_move = [
            'stdout.log',
        ]

        for to_move in from_path.iterdir():
            if not to_move == to_path:
                if (to_move.name in files_to_move) or to_move.name.startswith(f'{project_name}_'):
                    # typecast back to strings for the shutil method.
                    shutil.move(str(to_move), str(to_path / to_move.name))

    def _cleanup_path(self, path: Path) -> None:
        """Clean up the files in the path that was presumably used to run the simulation
        """
        remove_files = [
            'jm_ipython.sh',
            'jmodelica.py',
        ]

        for f in remove_files:
            if os.path.exists(os.path.join(path, f)):
                os.remove(os.path.join(path, f))

        for g in glob(os.path.join(path, 'tmp-simulation-*')):
            logger.debug(f"Removing tmp-simulation files {g}")
            # This is a complete hack but the name of the other folder that gets created is the
            # globbed directory without the tmp-simulation
            eplus_path = os.path.join(path, os.path.basename(g).replace('tmp-simulation-', ''))
            if os.path.exists(eplus_path):
                shutil.rmtree(eplus_path)
            shutil.rmtree(g)
