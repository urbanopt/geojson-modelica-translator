# This file is used as a Python-based CLI into Spawn.

import argparse
import logging
import os
import re
from pathlib import Path

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

    # Spawn's implementation doesn't currently handle *.mo files in the modelica_path.
    # It is expecting only directories.
    # This is a workaround to eliminate .mo items from modelica_path
    # FIXME: GMT is passing a dir, correct? So this modelica_path line isn't necessary?
    modelica_path = ' '.join([p for p in modelica_path if not re.match(r'.*\.mo$', p)])
    logger.info(f"Modelica path is {modelica_path}")
    # The MBL path can be passed in from docker (spawn_docker.sh) which joins paths
    # with a colon. Need to split this back out to space separated paths.
    mbl_path = ' '.join([p for p in f"{os.environ['MODELICAPATH']}/Buildings".split(':')])
    logger.info(f"MBL path is {mbl_path}")

    cmd = f"spawn modelica --create-fmu {model_name} --modelica-path {modelica_path} {mbl_path} --fmu-type ME --{compiler}"
    logger.info(f"Calling spawn compile with '{cmd}'")
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    # os.system(cmd)
    return f"{model_name}.fmu"


def run(fmu_name):
    """Run a modelica model with Spawn."""

    # TODO: Decide if start, stop, or step should be exposed to the user.
    cmd = f"spawn fmu --simulate {fmu_name} --start 0.0 --stop 86400 --step 300"
    os.system(cmd)
    return f'{fmu_name} has been simulated'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model: compile, run, compile_and_run')
    parser.add_argument('model', help='Name of the model to run, if debug, then will use test PID model. Can be an mo file or an FMU')
    parser.add_argument('modelica_path', help='Path to the project folder.')
    parser.add_argument('compiler', help='Compiler to use.', default='optimica')
    # Since this command is passed with spawn.py, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()

    logger.info(f'args: {args}')

    if args.action == 'help':
        print(parser.print_help())

    # fmu_name = None
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
            run(fmu_name)
        else:
            print(f"FMU model does not exist: {fmu_name}")
