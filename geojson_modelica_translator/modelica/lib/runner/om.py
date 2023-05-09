# This file is used as a Python-based CLI into OpenModelica.

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


# FIXME: what about model_path? See the confusion in spawn.py
def compile_fmu(model_name) -> str:
    """Compile a modelica model with OpenModelica.

    (Do not rename this function to `compile` as it is reserved in Python.)

    CLI Usage: omc [Options] (Model.mo | Script.mos) [Libraries | .mo-files]
             * Libraries: Fully qualified names of libraries to load before processing Model or Script.
             The libraries should be separated by spaces: Lib1 Lib2 ... LibN.
    """

    # The MBL path can be passed in from docker (om_docker.sh) which joins paths
    # with a colon. Need to split this back out to space separated paths.
    mbl_path = ' '.join([p for p in f"{os.environ['MODELICAPATH']}/Buildings".split(':')])
    logger.info(f"MBL path is {mbl_path}")
    # Call OMC to compile the model, using MSL & MBL libraries
    cmd = f"omc {model_name} Modelica {mbl_path}"
    logger.info(f"Calling OpenModelica compile with '{cmd}'")
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    os.system(cmd)
    return f"{model_name}.fmu"


def run(fmu_name, start: Optional[int], stop: Optional[int], step: Optional[int]) -> str:
    # TODO: what if start, stop, or step is not specified?
    """Run a modelica model with OpenModelica.
    CLI Usage: OMSimulator [Options] [Lua script] [FMU] [SSP file]
    """

    cmd = f"OMSimulator {start} {stop} {step} {fmu_name}"
    logger.info(f"Calling OpenModelica simulator with '{cmd}'")
    os.system(cmd)
    return f'{fmu_name} has been simulated'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model: compile, run, compile_and_run')
    parser.add_argument('model', help='Name(path) of the model to run, if debug, then will use test PID model. Can be an mo file or an FMU')  # noqa
    parser.add_argument('start_time', help='Start time of the simulation.', nargs='?')
    parser.add_argument('end_time', help='End time of the simulation.', nargs='?')
    parser.add_argument('sim_step', help='Time step of the simulation.', nargs='?')

    # Since this command is passed with om.py, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()

    logger.info(f'args: {args}')

    if args.action == 'help':
        print(parser.print_help())  # type: ignore

    fmu_name = None
    if args.action == 'compile' or args.action == 'compile_and_run':
        model = args.model
        if args.model == 'debug':
            model = "Buildings.Controls.OBC.CDL.Continuous.Validation.LimPID"
        else:
            if Path(args.model).is_file():
                model = args.model.replace(os.path.sep, '.')[:-3]
        logger.info(f'Compiling {model}')
        fmu_name = compile_fmu(model)

    if args.action == 'run' or args.action == 'compile_and_run':
        # Run the FMU either that is passed in or from the previous step
        if not fmu_name:
            fmu_name = args.model
        if Path(fmu_name).exists():
            run(fmu_name, args.start_time, args.end_time, args.sim_step)
        else:
            print(f"FMU model does not exist: {fmu_name}")
