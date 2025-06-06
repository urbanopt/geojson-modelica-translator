# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

# from __future__ import annotations
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Union

from buildingspy.simulate.Dymola import Simulator
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS

logger = logging.getLogger(__name__)


class ModelicaRunner:
    """Class to run Modelica models."""

    ACTION_LOG_MAP = {  # noqa: RUF012
        "compile": "Compiling mo file",  # creates an FMU
        "compile_and_run": "Compile and run the mo file",
        "run": "Running FMU",
    }

    def __init__(self):
        """Initialize the runner with data needed for simulation"""

        # Verify that docker is up and running, if needed.
        r = subprocess.call(["docker", "ps"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            raise SystemExit("Docker not configured on host computer, unable to run")

        # If there is a file to load (meaning that we aren't loading from the library),
        # then check that it exists
        if file_to_load and not Path(file_to_load).exists():
            raise SystemExit(f"File not found to run {file_to_load}")

    def _verify_run_path_for_docker(
        self, run_path: Union[str, Path, None], file_to_run: Union[str, Path, None]
    ) -> Path:
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
            run_path = Path(file_to_run).parent  # type: ignore[arg-type]
        new_run_path = Path(run_path)

        # Modelica can't handle spaces in project name or path
        if (len(str(new_run_path).split()) > 1) or (len(str(file_to_run).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{new_run_path}' for run path and {file_to_run} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere."
            )
        return new_run_path

    def _copy_over_docker_resources(
        self, run_path: Path, filename: Union[str, Path, None], model_name: str, **kwargs
    ) -> None:
        """Copy over files needed to run the simulation, this includes
        the generation of the OpenModelica scripts to load and compile/run
        the simulation.

        Must pass start_time, stop_time, and either step_size or number_of_intervals.

        Args:
            run_path (Path): Path where the model will be run, this is where the files will be copied.
            filename (str): name of the file that will be loaded (e.g., BouncingBall.mo, package.mo)
            model_name (str): name of the model to run (e.g., BouncingBall, Districts.DistrictModel)
            **kwargs: Arbitrary keyword arguments.
                project_in_library (bool): If True, then the file_to_load is in the library, otherwise it is a file
                                             on the local file system.
                start_time (int): start time of the simulation, in seconds
                stop_time (int): stop time of the simulation, in seconds
                step_size (int): step size of the simulation, in seconds
                number_of_intervals (int): number of intervals to run the simulation
                output_variables (list[str]): limit Modelica .
        """
        # read in the start, stop, and step times
        project_in_library = kwargs.get("project_in_library", False)
        start_time = kwargs.get("start_time")
        stop_time = kwargs.get("stop_time")
        step_size = kwargs.get("step_size")
        number_of_intervals = kwargs.get("number_of_intervals")
        output_variables = kwargs.get("output_variables")
        simulation_flags = kwargs.get("simulation_flags")

        if step_size and number_of_intervals:
            logger.error("step_size and number_of_intervals are mutually exclusive. Pass one or the other, not both.")
            raise ValueError()
            # ValueError is raised in order to prevent the simulation from running.
            # Text in the ValueError does not get out of our test, therefore log the message for user visibility.

        simulation_args = f"{model_name}"
        if start_time:
            simulation_args += f", startTime={start_time}"
        if stop_time:
            simulation_args += f", stopTime={stop_time}"
        if step_size:
            simulation_args += f", stepSize={step_size}"
        if number_of_intervals:
            simulation_args += f", numberOfIntervals={number_of_intervals}"
        if output_variables:
            simulation_args += f', variableFilter="{output_variables.replace(",", "|")}"'
        if simulation_flags:
            simulation_args += f', simflags="{simulation_flags.replace(",", " ")}"'
        logger.debug(f"Arguments passed to OMC: {simulation_args}")

        # initialize the templating framework (Jinja2)
        template_env = Environment(
            loader=FileSystemLoader(searchpath=Path(__file__).parent.resolve() / "lib" / "runner"),
            undefined=StrictUndefined,
        )
        template_env.filters.update(ALL_CUSTOM_FILTERS)
        template = template_env.get_template("simulate.most")
        model_data = {
            "project_in_library": project_in_library,
            "file_to_load": Path(filename).name if filename else None,
            "simulation_args": simulation_args,
            "model_name": model_name,
        }
        with open(run_path / "simulate.mos", "w") as f:
            f.write(template.render(**model_data))
        template = template_env.get_template("compile_fmu.most")
        with open(run_path / "compile_fmu.mos", "w") as f:
            f.write(template.render(**model_data))

    def _subprocess_call_to_docker(self, run_path: Path, action: str, compiler_flags: str | None = None) -> int:
        """Call out to a subprocess to run the command in docker

        Args:
            run_path (Path): local path where the Modelica simulation or compilation will start
            action (str):  action to run either compile_and_run, compile, or run

        Returns:
            int: exit code of the subprocess
        """
        # Set up the run content
        curdir = Path.cwd()
        os.chdir(run_path)
        stdout_log = open("stdout.log", "w")  # noqa: SIM115
        model_name = run_path.parts[-1]
        image_name = "nrel/gmt-om-runner:3.0.0"
        mo_script = "compile_fmu" if action == "compile" else "simulate"
        if compiler_flags is not None:
            # Format compiler flags for OpenModelica
            compiler_flags_for_modelica = compiler_flags.replace(",", " ")
        else:
            compiler_flags_for_modelica = ""

        try:
            # create the command to call the open modelica compiler inside the docker image
            exec_call = [
                "docker",
                "run",
                "-v",
                f"{run_path}:/mnt/shared/{model_name}",
                f"{image_name}",
                "/bin/bash",
                "-c",
                f"cd mnt/shared/{model_name} && omc {mo_script}.mos {compiler_flags_for_modelica}",
            ]
            # execute the command that calls docker
            logger.debug(f"Calling {exec_call}")
            completed_process = subprocess.run(
                exec_call,
                stdout=stdout_log,
                stderr=subprocess.STDOUT,
                cwd=run_path,
                check=False,
            )
            # Uncomment this section and rebuild the container in order to pause the container
            # to inspect the container and test commands.
            # import time
            # time.sleep(10000)  # wait for the subprocess to start
            logger.debug(
                f"Subprocess command executed, waiting for completion... \nArgs used: {completed_process.args}"
            )
        except KeyboardInterrupt:
            # List all containers and their images
            docker_containers_cmd = ["docker", "ps", "--format", "{{.ID}} {{.Image}}"]
            containers_list = subprocess.check_output(docker_containers_cmd, text=True).rstrip().split("\n")

            # Find containers from our image
            for container_line in containers_list:
                container_id, container_image = container_line.split()
                if container_image == image_name:
                    logger.debug(f"Killing container: {container_id} (Image: {container_image})")
                    # Kill the container
                    kill_command = f"docker kill {container_id}"
                    subprocess.run(kill_command.split(), check=True, text=True)
            # Remind user why the simulation didn't complete
            raise SystemExit("Simulation stopped by user KeyboardInterrupt")
        finally:
            os.chdir(curdir)
            stdout_log.close()
            logger.debug("Closed stdout.log")

        return completed_process.returncode

    def run_in_docker(
        self,
        action: str,
        model_name: str,
        file_to_load: Union[str, Path, None] = None,
        run_path: Union[str, Path, None] = None,
        **kwargs,
    ) -> tuple[bool, Union[str, Path]]:
        """Run the Modelica project in a docker-based environment.
        The action will determine what type of run will be conducted.
        This method supports either a file path pointing to the package to load, or a modelica path which is a
        period separated path. Results are saved into run_path.

        stdout.log will store both stdout and stderr of the simulations

        Args:
            action (str): The action to run, must be one of compile_and_run, compile, or run
            model_name (str): The name of the model to be simulated (this is the name within Modelica)
            file_to_load (str, Path): The file path or a modelica path to be simulated
            run_path (str, optional): location where the Modelica simulation will start. Defaults to None.
            kwargs: additional arguments to pass to the runner which can include
                project_in_library (bool): whether the project is in a library or not
                start_time (float): start time of the simulation
                stop_time (float): stop time of the simulation
                step_size (float): step size of the simulation
                number_of_intervals (int): number of intervals to run the simulation
                output_variables (str): Comma separated list of Modelica output variables to produce
                compiler_flags (str): Comma separated list of OpenModelica simulation flags. For advanced users only
                simulation_flags (str): Comma-separated list of OpenModelica simulation flags. For advanced users only
                debug (bool): whether to run in debug mode or not, prevents files from being deleted

        Returns:
            tuple[bool, str]: success status and path to the results directory
        """
        # Verify that the action is in the list of valid actions
        if action not in ModelicaRunner.ACTION_LOG_MAP:
            raise SystemExit(f"Invalid action {action}, must be one of {list(ModelicaRunner.ACTION_LOG_MAP.keys())}")

        self._verify_docker_run_capability(file_to_load)
        verified_run_path = self._verify_run_path_for_docker(run_path, file_to_load)

        self._copy_over_docker_resources(verified_run_path, file_to_load, model_name, **kwargs)

        exitcode = self._subprocess_call_to_docker(verified_run_path, action, kwargs.get("compiler_flags"))

        logger.debug("Checking stdout.log for errors")
        with open(verified_run_path / "stdout.log") as f:
            stdout_log = f.read()
            if "Failed to build model" in stdout_log:
                logger.error("Model failed to build")
                exitcode = 1
            elif "Killed" in stdout_log:
                logger.error(
                    "Model is too large for the Docker resources available."
                    " Increase Docker resources, decrease number of buildings simulated, or both"
                )
            elif "division by zero at time" in stdout_log and "Simulation execution failed for model:" in stdout_log:
                logger.error(
                    "Model failed to run due to division by zero. Perhaps head pressure or flow rate are insufficient?"
                )
                exitcode = 1
            elif "The simulation finished successfully" in stdout_log:
                logger.info("Model ran successfully")
                exitcode = 0
            elif action == "compile":
                logger.info("Model compiled successfully -- no errors")
                exitcode = 0
            else:
                logger.error("Model failed to run -- unknown error")
                exitcode = 1

        # Cleanup all of the temporary files that get created
        self.cleanup_path(verified_run_path, model_name, debug=kwargs.get("debug", False))

        logger.debug("Moving results to results directory")
        # get the location of the results path
        results_path = Path(verified_run_path / f"{model_name}_results")
        self.move_results(verified_run_path, results_path, model_name)
        return (exitcode == 0, results_path)

    def run_in_dymola(
        self, action: str, model_name: str, file_to_load: Union[str, Path], run_path: Union[str, Path], **kwargs
    ) -> tuple[bool, Union[str, Path]]:
        """If running on Windows or Linux, you can run Dymola (assuming you have a license),
        using the BuildingsPy library. This is not supported on Mac.

        For using Dymola with the GMT, you need to ensure that MSL v4.0 are loaded correctly and that the
        Buildings library is in the MODELICAPATH. I added the MSL openModel via appending it to the Dymola's
        /opt/<install>/insert/dymola.mos file on Linux. The additions to the dymola.mos will look like the following:

            ```modelica
            // If using Dymola 2024, then the MSL v4.0.0 is already loaded
            // If needed, install the patch of the Modelica Standard Library v4.0.0 (Services)
            openModel("/home/username/Dymola/MSL_v4_ServicesPatch/ModelicaServices/package.mo", changeDirectory=false);
            // If needed, install MSL v4
            openModel("/home/username/Dymola/config/Modelica 4.0.0/package.mo", changeDirectory=false);

            // Open MBL
            openModel("/home/username/working/modelica-buildings/Buildings/package.mo", changeDirectory=false);

            // Set the home directory
            cd("/home/username/working")
            ```

        Args:
            action (str): compile (translate) or simulate
            model_name (str): Name of the model to translate or simulate
            package_path (Union[str, Path]): Name of the package to also load
            kwargs: additional arguments to pass to the runner which can include
                start_time (float): start time of the simulation
                stop_time (float): stop time of the simulation, in seconds
                step_size (float): step size of the simulation, in seconds
                debug (bool): whether to run in debug mode or not, prevents files from being deleted.

        Returns:
            tuple[bool, Union[str, Path]]:  success status and path to the results directory
        """
        run_path = str(run_path)
        current_dir = Path.cwd()
        try:
            os.chdir(run_path)
            print(run_path)
            if file_to_load is None:
                # This occurs when the model is already in a library that is loaded (e.g., MSL, Buildings)
                # Dymola does check the MODELICAPATH for any libraries that need to be loaded automatically.
                dymola_simulator = Simulator(
                    modelName=model_name,
                    outputDirectory=run_path,
                )
            else:
                file_to_load = str(file_to_load)
                dymola_simulator = Simulator(
                    modelName=model_name,
                    outputDirectory=run_path,
                    packagePath=file_to_load,
                )

            # TODO: add in passing of parameters
            # dymola_simulator.addParameters({'PI.k': 10.0, 'PI.Ti': 0.1})
            dymola_simulator.setSolver("dassl")

            start_time = kwargs.get("start_time", 0)
            stop_time = kwargs.get("stop_time", 300)
            step_size = kwargs.get("step_size", 5)

            # calculate the number of intervals based on the step size
            number_of_intervals = int((stop_time - start_time) / step_size)

            dymola_simulator.setStartTime(start_time)
            dymola_simulator.setStopTime(stop_time)
            dymola_simulator.setNumberOfIntervals(number_of_intervals)

            # Do not show progressbar! -- It will cause an "elapsed time used before assigned" error.
            # dymola_simulator.showProgressBar(show=True)

            if kwargs.get("debug", False):
                dymola_simulator.showGUI(show=True)
                dymola_simulator.exitSimulator(False)

            # BuildingPy throws an exception if the model errs
            try:
                if action == "compile":
                    dymola_simulator.translate()
                    # the results of this does not create an FMU, just
                    # the status of the translation/compilation.
                elif action == "simulate":
                    dymola_simulator.simulate()
            except Exception as e:  # noqa: BLE001
                logger.error(f"Exception running Dymola: {e}")
                return False, run_path

            # remove some of the unneeded results
            self.cleanup_path(Path(run_path), model_name, debug=kwargs.get("debug", False))
        finally:
            os.chdir(current_dir)

        return True, run_path

    def move_results(self, from_path: Path, to_path: Path, model_name: Union[str, None] = None) -> None:
        """This method moves the results of the simulation that are known for now.
        This method moves only specific files (stdout.log for now), plus all files and folders beginning
        with the "{project_name}_" name.

        If there are results, they will simply be overwritten (for now).

        Args:
            from_path (Path): where the files will move from
            to_path (Path): where the files will be saved. Will be created if does not exist.
            model_name (Union[str, None], optional): name of the project ran in run_in_docker method. Defaults to None.
        """
        to_path.mkdir(parents=True, exist_ok=True)

        files_to_move = [
            "stdout.log",
        ]
        if model_name is not None:
            files_to_move.append(
                f"{model_name}.log",
            )
            files_to_move.append(
                f"{model_name}.fmu",
            )
            files_to_move.append(
                f"{model_name.replace('.', '_')}.log",
            )
            files_to_move.append(
                f"{model_name.replace('.', '_')}_FMU.log",
            )

        for to_move in from_path.iterdir():
            if to_move != to_path and ((to_move.name in files_to_move) or to_move.name.startswith(f"{model_name}_")):
                # typecast back to strings for the shutil method.
                shutil.move(str(to_move), str(to_path / to_move.name))

    def cleanup_path(self, path: Path, model_name: str, **kwargs: dict) -> None:
        """Clean up the files in the path that was presumably used to run the simulation.
        If debug is passed, then simulation running files will not be removed, but the
        intermediate simulation files will be removed (e.g., .c, .h, .o, .bin)

        Args:
            path (Path): Path of the folder to clean
            model_name (str): Name of the model, used to remove model-specific intermediate files
            kwargs: additional arguments to pass to the runner which can include
                debug (bool): whether to remove all files or not
        """
        # list of files to always remove
        files_to_remove = [
            "dsin.txt",
            "dsmodel.c",
            "dymosim",
            "request.",
            f"{model_name}",
            f"{model_name}.makefile",
            f"{model_name}.libs",
            f"{model_name.replace('.', '_')}_info.json",
            f"{model_name.replace('.', '_')}_FMU.makefile",
            f"{model_name.replace('.', '_')}_FMU.libs",
        ]

        # keep these files if debug is passed
        conditional_remove_files = [
            "compile_fmu.mos",
            "simulate.mos",
            "run.mos",
            "run_translate.mos",
        ]

        logger.debug("Removing temporary files")

        if not kwargs.get("debug", False):
            logger.debug("...and removing scripts to run the simulation")
            files_to_remove.extend(conditional_remove_files)

        for f in files_to_remove:
            logger.debug(f"Removing {f}")
            if (path / f).is_dir():
                continue
            (path / f).unlink(missing_ok=True)

        # The other files below will always be removed, debug or not

        # glob for the .c, .h, .o, .bin files to remove
        remove_files_glob = [
            f"{model_name}*.c",
            f"{model_name}*.h",
            f"{model_name}*.o",
            f"{model_name}*.bin",
        ]
        for pattern in remove_files_glob:
            for f in path.glob(pattern):  # type: ignore[assignment]
                Path(f).unlink(missing_ok=True)

        # Remove the 'tmp' folder that was created by 5G simulations
        # Dir won't exist for 4G simulations, so ignoring errors
        shutil.rmtree(path / "tmp", ignore_errors=True)
