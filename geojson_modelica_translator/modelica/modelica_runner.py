# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS

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
    ACTION_LOG_MAP = {
        'compile': 'Compiling mo file',  # creates an FMU
        'compile_and_run': 'Compile and run the mo file',
        'run': 'Running FMU',
    }

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

    def _verify_docker_run_capability(self, file_to_load: Union[str, Path, None]):
        """Verify that docker is configured on the host computer correctly before running

        Args:
            file_to_load (Union[str, Path]): Can be a file path or a modelica path

        Raises:
            SystemExit: _description_
            SystemExit: _description_
        """
        if not self.docker_configured:
            raise SystemExit('Docker not configured on host computer, unable to run')

        # If there is a file to load (meaning that we aren't loading from the library),
        # then check that it exists
        if file_to_load and not os.path.exists(file_to_load):
            raise SystemExit(f'File not found to run {file_to_load}')

    def _verify_run_path_for_docker(self, run_path: Union[str, Path, None], file_to_run: Union[str, Path, None]) -> Path:
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
            run_path = os.path.dirname(file_to_run)  # type: ignore
        new_run_path = Path(run_path)

        # Modelica can't handle spaces in project name or path
        if (len(str(new_run_path).split()) > 1) or (len(str(file_to_run).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{new_run_path}' for run path and {file_to_run} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")
        return new_run_path

    def _copy_over_docker_resources(self, run_path: Path, filename: Union[str, Path, None], model_name: str, **kwargs) -> None:
        """Copy over files needed to run the simulation, this includes
        the generation of the OpenModelica scripts to load and compile/run
        the simulation.

        If passing the start, stop, and step times, then at least start and stop must be supplied to
        update the simuation to use these values instead of the defaults.

        Args:
            run_path (Path): Path where the model will be run, this is where the files will be copied.
            filename (str): name of the file that will be loaded (e.g., BouncingBall.mo, package.mo)
            model_name (str): name of the model to run (e.g., BouncingBall, Districts.DistrictModel)
        """
        # read in the start, stop, and step times
        project_in_library = kwargs.get('project_in_library', False)
        start_time = kwargs.get('start_time', None)
        stop_time = kwargs.get('stop_time', None)
        step_size = kwargs.get('step_size', None)

        # initialize the templating framework (Jinja2)
        template_env = Environment(
            loader=FileSystemLoader(searchpath=Path(__file__).parent.resolve() / 'lib' / 'runner'),
            undefined=StrictUndefined
        )
        template_env.filters.update(ALL_CUSTOM_FILTERS)
        template = template_env.get_template('simulate.most')
        model_data = {
            "project_in_library": project_in_library,
            "file_to_load": Path(filename).name if filename else None,
            "model_name": model_name,
            "use_default_time_params": False if start_time is not None and stop_time is not None else True,
            "start_time": start_time,
            "stop_time": stop_time,
            "step_size": step_size,
        }
        with open(run_path / 'simulate.mos', 'w') as f:
            f.write(template.render(**model_data))
        template = template_env.get_template('compile_fmu.most')
        with open(run_path / 'compile_fmu.mos', 'w') as f:
            f.write(template.render(**model_data))

        # new om_docker.sh file name
        new_om_docker = run_path / self.om_docker_path.name
        shutil.copyfile(self.om_docker_path, new_om_docker)
        os.chmod(new_om_docker, 0o775)

    def _subprocess_call_to_docker(self, run_path: Union[str, Path], action: str) -> int:
        """Call out to a subprocess to run the command in docker

        Args:
            run_path (Path): local path where the Modelica simulation or compilation will start
            action (str):  action to run either compile_and_run, compile, or run

        Returns:
            int: exit code of the subprocess
        """
        # Set up the run content
        curdir = os.getcwd()
        os.chdir(run_path)
        stdout_log = open('stdout.log', 'w')
        try:
            # get the relative difference between the file to run and the path which everything is running in.
            # make sure to simulate at a directory above the project directory!

            # Use slashes for the location of the model to run. We can make these periods `.replace(os.sep, '.')`
            # but must strip off the .mo extension on the model to run
            # run_model = Path(file_to_run).relative_to(run_path)
            exec_call = ['./om_docker.sh', action]
            logger.debug(f"Calling {exec_call}")
            p = subprocess.Popen(
                exec_call,  # type: ignore
                stdout=stdout_log,
                stderr=subprocess.STDOUT,
                cwd=run_path
            )
            # Uncomment this section and rebuild the container in order to pause the container
            # to inpsect the container and test commands.
            # import time
            # time.sleep(10000)  # wait for the subprocess to start
            logger.debug(f"Subprocess command executed, waiting for completion... \nArgs used: {p.args}")
            exitcode = p.wait()
        finally:
            os.chdir(curdir)
            stdout_log.close()
            logger.debug('Closed stdout.log')

        return exitcode

    def run_in_docker(self, action: str, model_name: str, file_to_load: Union[str, Path, None] = None,
                      run_path: Union[str, Path, None] = None, **kwargs) -> tuple[bool, Union[str, Path]]:
        """Run the Modelica project in a docker-based environment. The action will determine
        what type of run will be conducted. This method supports either a file path pointing to the package to load, or a modelica path which is a period separated path. Results are saved into run_path.

        stdout.log will store both stdout and stderr of the simulations

        Args:
            action (str): The action to run, must be one of compile_and_run, compile, or run
            model_name (str): The name of the model to be simulated (this is the name within Modelica)
            file_to_load (str, Path): The file path or a modelica path to be simulated
            run_path (str, optional): location where the Modelica simulation will start. Defaults to None.
            kwargs: additional arugments to pass to the runner which can include
                project_in_library (bool): whether the project is in a library or not
                start_time (float): start time of the simulation
                stop_time (float): stop time of the simulation
                step_size (float): step size of the simulation

        Returns:
            tuple[bool, str]: success status and path to the results directory
        """
        # Verify that the action is in the list of valid actions
        if action not in ModelicaRunner.ACTION_LOG_MAP:
            raise SystemExit(f'Invalid action {action}, must be one of {list(ModelicaRunner.ACTION_LOG_MAP.keys())}')

        self._verify_docker_run_capability(file_to_load)
        verified_run_path = self._verify_run_path_for_docker(run_path, file_to_load)

        self._copy_over_docker_resources(
            verified_run_path, file_to_load, model_name, **kwargs
        )

        exitcode = self._subprocess_call_to_docker(verified_run_path, action)

        logger.debug('checking stdout.log for errors')
        # Check the stdout.log file for errors
        with open(verified_run_path / 'stdout.log', 'r') as f:
            stdout_log = f.read()
            if 'Failed to build model' in stdout_log:
                logger.error('Model failed to build')
                exitcode = 1
            elif 'The simulation finished successfully' in stdout_log:
                logger.info('Model ran successfully')
                exitcode = 0
            elif action == 'compile':
                logger.info('Model compiled successfully -- no errors')
                exitcode = 0
            else:
                logger.error('Model failed to run -- unknown error')
                exitcode = 1

        logger.debug('removing temporary files')
        # Cleanup all of the temporary files that get created
        self._cleanup_path(verified_run_path, model_name)

        logger.debug('moving results to results directory')
        # get the location of the results path
        results_path = Path(verified_run_path / f'{model_name}_results')
        self.move_results(verified_run_path, results_path, model_name)
        return (exitcode == 0, results_path)

    def move_results(self, from_path: Path, to_path: Path, model_name: Union[str, None] = None) -> None:
        """This method moves the results of the simulation that are known for now.
        This method moves only specific files (stdout.log for now), plus all files and folders beginning
        with the "{project_name}_" name.

        :param from_path: pathlib.Path, where the files will move from
        :param to_path: pathlib.Path, where the files will be saved. Will be created if does not exist.
        :param model_name: string, name of the project ran in run_in_docker method
        :return: None
        """
        # if there are results, they will simply be overwritten (for now).
        to_path.mkdir(parents=True, exist_ok=True)

        files_to_move = [
            'stdout.log',
        ]
        if model_name is not None:
            files_to_move.append(f'{model_name}.log',)
            files_to_move.append(f'{model_name}.fmu',)
            files_to_move.append(f"{model_name.replace('.', '_')}.log",)
            files_to_move.append(f"{model_name.replace('.', '_')}_FMU.log",)

        for to_move in from_path.iterdir():
            if not to_move == to_path:
                if (to_move.name in files_to_move) or to_move.name.startswith(f'{model_name}_'):
                    # typecast back to strings for the shutil method.
                    shutil.move(str(to_move), str(to_path / to_move.name))

    def _cleanup_path(self, path: Path, model_name: str) -> None:
        """Clean up the files in the path that was presumably used to run the simulation
        """
        remove_files = [
            'om_docker.sh',
            'compile_fmu.mos',
            'simulate.mos',
            f'{model_name}',
            f'{model_name}.makefile',
            f"{model_name.replace('.', '_')}_info.json",
            f"{model_name.replace('.', '_')}_FMU.makefile",
            f"{model_name.replace('.', '_')}_FMU.libs",
        ]

        for f in remove_files:
            if os.path.exists(os.path.join(path, f)):
                os.remove(os.path.join(path, f))

        # glob for the .c, .h, .o, .bin files to remove
        remove_files_glob = [
            f'{model_name}*.c',
            f'{model_name}*.h',
            f'{model_name}*.o',
            f'{model_name}*.bin',
        ]
        for pattern in remove_files_glob:
            for f in glob(os.path.join(path, pattern)):
                os.remove(f)

        # The below was a result from jmodelica and can *most likely* be removed
        for g in glob(os.path.join(path, 'tmp-simulation-*')):
            logger.debug(f"Removing tmp-simulation files {g}")
            # This is a complete hack but the name of the other folder that gets created is the
            # globbed directory without the tmp-simulation
            eplus_path = os.path.join(path, os.path.basename(g).replace('tmp-simulation-', ''))
            if os.path.exists(eplus_path):
                shutil.rmtree(eplus_path)
            shutil.rmtree(g)
