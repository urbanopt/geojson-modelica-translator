# This file is used as a Python-based CLI into Spawn.

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from fmu_runner import FmuRunner

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


def compile_fmu(model_name, modelica_path, compiler):
    """Compile a modelica model.

    (Do not rename this function to `compile` as it is reserved in Python.)

    This function shamelessly stolen from https://github.com/NREL/MegaBOP/blob/main/main/pymodelica/compiler.py#L11
    and only lightly modified.
    """

    # FYI Spawn's implementation doesn't currently handle *.mo files in the modelica_path.
    # It is expecting only directories.
    logger.info(f"Modelica path is {modelica_path}")
    # The MBL path can be passed in from docker (spawn_docker.sh) which joins paths
    # with a colon. Need to split this back out to space separated paths.
    # FIXME: I don't know how env vars work in Docker. The container version of both the modelica_path and the mbl_path
    # are inside the mbl_path variable. We need both, but somehow they're both in the mbl_path variable.
    mbl_path = ' '.join([p for p in f"{os.environ['MODELICAPATH']}/Buildings".split(':')])
    logger.info(f"MBL path is {mbl_path}")
    cmd = f"spawn modelica --create-fmu {model_name} --modelica-path {mbl_path} --fmu-type ME --{compiler}"
    logger.info(f"Calling spawn compile with '{cmd}'")
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    os.system(cmd)
    return f"{model_name}.fmu"


# TODO: Pass the start, stop, and step as arguments.
def run(fmu_name, start: Optional[int], stop: Optional[int], step: Optional[int]):
    """Run a modelica model with Spawn."""

    # TODO: Decide if start, stop, or step should be exposed to the user.
    run_class = FmuRunner(fmu_name, start=start, stop=stop, step=step)
    result = run_class.run()
    logger.info(f"Spawn result: {result}")

    # TODO: eventually use spawn's FMU runner, but it is not ready for prime time.
    # cmd = f"spawn fmu --simulate {fmu_name} --start 0.0 --stop 86400 --step 300"
    # os.system(cmd)
    # logger.warning("Spawn modelica is not ready for prime time yet.")

    return f'{fmu_name} has been simulated'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model: compile, run, compile_and_run')
    parser.add_argument('model', help='Name of the model to run, if debug, then will use test PID model. Can be an mo file or an FMU')
    parser.add_argument('modelica_path', help='Path to the project folder.')
    parser.add_argument('compiler', help='Compiler to use.', default='optimica')
    parser.add_argument('start_time', help='Start time of the simulation.', nargs='?')
    parser.add_argument('end_time', help='End time of the simulation.', nargs='?')
    parser.add_argument('sim_step', help='Time step of the simulation.', nargs='?')

    # Since this command is passed with spawn.py, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()

    logger.info(f'args: {args}')

    if args.action == 'help':
        print(parser.print_help())

    fmu_name = None
    if args.action == 'compile' or args.action == 'compile_and_run':
        model = args.model
        if args.model == 'debug':
            model = "Buildings.Controls.OBC.CDL.Continuous.Validation.LimPID"
        else:
            if Path(args.model).is_file():
                model = args.model.replace(os.path.sep, '.')[:-3]
        logger.info(f'Compiling {model}')
        fmu_name = compile_fmu(model, args.modelica_path, args.compiler)

    if args.action == 'run' or args.action == 'compile_and_run':
        # Run the FMU either that is passed in or from the previous step
        if not fmu_name:
            fmu_name = args.model
        if Path(fmu_name).exists():
            run(fmu_name, args.start_time, args.end_time, args.sim_step)
        else:
            print(f"FMU model does not exist: {fmu_name}")
