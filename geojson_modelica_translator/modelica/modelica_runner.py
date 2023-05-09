# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
import subprocess
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
    Class to run Modelica models.
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
        local_path = Path(__file__).parent.resolve()
        self.om_docker_path = local_path / 'lib' / 'runner' / 'om_docker.sh'

        # Verify that docker is up and running
        r = subprocess.call(['docker', 'ps'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.docker_configured = r == 0

    def _verify_docker_run_capability(self, file_to_run: Union[str, Path]):
        if not self.docker_configured:
            raise SystemExit('Docker not configured on host computer, unable to run')

        if not os.path.exists(file_to_run):
            raise SystemExit(f'File not found to run {file_to_run}')

        if not os.path.isfile(file_to_run):
            raise SystemExit(f'Expecting to run a file, not a folder in {file_to_run}')

    def _verify_run_path_for_docker(self, run_path: Union[str, Path, None], file_to_run: Union[str, Path]) -> Path:
        """If there is no run_path, then run it in the same directory as the
        file being run. This works fine for simple Modelica projects but typically
        the run_path needs to be a few levels higher in order to include other
        project dependencies (e.g., multiple mo files).

        Args:
            run_path (str): directory of where to run the simulation
            file_to_run (str): the name of the file to run. This should be the fully
                               qualified path to the file.

        Raises:
            SystemExit: Throw an exception if the run_path or file_to_run has spaces in it

        Returns:
            Path: Return the run_path as a Path object
        """
        if not run_path:
            run_path = os.path.dirname(file_to_run)
        new_run_path = Path(run_path)

        # Modelica can't handle spaces in project name or path
        if (len(str(new_run_path).split()) > 1) or (len(str(file_to_run).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{new_run_path}' for run path and {file_to_run} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")
        return new_run_path

    def _copy_over_docker_resources(self, run_path: Path) -> None:
        """Copy over files needed to run the simulation
        """
        new_om_docker = os.path.join(run_path, os.path.basename(self.om_docker_path))
        shutil.copyfile(self.om_docker_path, new_om_docker)
        os.chmod(new_om_docker, 0o775)

    def _subprocess_call_to_docker(self, run_path: Union[str, Path], file_to_run: Union[str, Path], action: str) -> int:
        """Call out to a subprocess to run the command in docker

        Args:
            run_path (Path): name of the file or directory to simulate
            file_to_run (str): location where the Modelica simulatio or compilation will start
            action (str):  action to run either compile_and_run, compile, or run

        Raises:
            SystemExit: Invalid action, should be of type compile_and_run, compile, or run

        Returns:
            int: exit code of the subprocess
        """
        action_log_map = {
            'compile_and_run': 'Compiling mo file and running FMU',
            'compile': 'Compiling mo file',
            'run': 'Running FMU',
        }
        # Verify that the action is in the list of valid actions
        if action not in action_log_map:
            raise SystemExit(f'Invalid action {action}, must be one of {list(action_log_map.keys())}')

        # Set up the run content
        curdir = os.getcwd()
        os.chdir(run_path)
        stdout_log = open('stdout.log', 'w')
        try:
            # get the relative difference between the file to run and the path which everything is running in.
            # make sure to simulate at a directory above the project directory!

            # Use slashes for the location of the model to run. We can make these periods `.replace(os.sep, '.')`
            # but must strip off the .mo extension on the model to run
            run_model = Path(file_to_run).relative_to(run_path)
            logger.info(f"{action_log_map[action]}: {run_model} in {run_path}")
            exec_call = [self.om_docker_path, action, run_model, run_path]
            logger.debug(f"Calling {exec_call}")
            p = subprocess.Popen(
                exec_call,  # type: ignore
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

    def run_in_docker(self, file_to_run: Union[str, Path], run_path: Union[str, Path, None]
                      = None, project_name: Union[str, None] = None) -> tuple[bool, Union[str, Path]]:
        """ Run the Modelica project in a docker-based environment. Results are saved into the path of the
        file that was selected to run.

        stdout.log will store both stdout and stderr of the simulations

        Args:
            file_to_run (str, Path): name of the file (could be directory?) to simulate
            run_path (str, optional): location where the Modelica simulation will start. Defaults to None.
            project_name (str, optional): name of the project being simulated. Will be used to determine name
                                          of results directory. Defaults to None.

        Returns:
            tuple[bool, str]: success status and path to the results directory
        """
        self._verify_docker_run_capability(file_to_run)
        verified_run_path = self._verify_run_path_for_docker(run_path, file_to_run)

        if not project_name:
            project_name = os.path.splitext(os.path.basename(file_to_run))[0]

        # self._copy_over_docker_resources(verified_run_path)

        exitcode = self._subprocess_call_to_docker(verified_run_path, file_to_run, 'compile_and_run')

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(verified_run_path)

        logger.debug('moving results to results directory')
        # get the location of the results path
        results_path = Path(verified_run_path / f'{project_name}_results')
        self.move_results(verified_run_path, results_path, project_name)
        return (exitcode == 0, results_path)

    def compile_in_docker(self, file_to_run: str, save_path: Union[str, Path, None] = None) -> bool:
        """Build/compile the Modelica project in a docker-based environment using JModelica. The resulting
        FMU is saved to the save_path.

        stdout.log will store both stdout and stderr of the simulations

        Args:
            file_to_run (str):  name of the file (could be directory?) to simulate
            save_path (str, optional): location where the Modelica FMU will be saved. Defaults to None.

        Returns:
            bool: success status
        """
        self._verify_docker_run_capability(file_to_run)
        verified_save_path = self._verify_run_path_for_docker(save_path, file_to_run)

        # self._copy_over_docker_resources(verified_save_path)

        exitcode = self._subprocess_call_to_docker(verified_save_path, file_to_run, 'compile')

        # Cleanup all of the temporary files that get created
        logger.debug('removing temporary files')
        self._cleanup_path(verified_save_path)

        logger.debug('moving results to results directory')
        return exitcode == 0

    def run_fmu_in_docker(self, file_to_run: str, run_path: Union[str, None] = None) -> tuple[bool, Union[str, Path]]:
        """Run the FMU in a docker-based environment. Results are saved into the path of the
        file that was selected to run.

        stdout.log will store both stdout and stderr of the simulations

        Args:
            file_to_run (str): name of the file (could be directory?) to simulate
            run_path (str, optional): location where the Modelica simulation will start. Defaults to None.

        Returns:
            tuple[bool, str]: success status and path to the results directory
        """
        self._verify_docker_run_capability(file_to_run)
        verified_run_path = self._verify_run_path_for_docker(run_path, file_to_run)
        project_name = os.path.splitext(os.path.basename(file_to_run))[0]

        # self._copy_over_docker_resources(verified_run_path)

        exitcode = self._subprocess_call_to_docker(verified_run_path, file_to_run, 'run')

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(verified_run_path)

        logger.debug('moving results to results directory')
        # get the location of the results path
        results_path = Path(verified_run_path / f'{project_name}_results')
        self.move_results(verified_run_path, results_path, project_name)
        return (exitcode == 0, results_path)

    def move_results(self, from_path: Path, to_path: Path, project_name: str = None) -> None:
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
            'om_docker.sh',
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
