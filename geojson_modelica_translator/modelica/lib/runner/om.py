# This file is used as a Python-based CLI into OpenModelica.

# OpenModelica doesn't support the MODELICAPATH env var, so the modelica
# building library must be symlinked into the .openmodelica folder.
# https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/faq.html

import argparse
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


def configure_mbl_path() -> None:
    """Configure the Modelica Building Library (MBL) path.  The mbl is always mounted into the
    same folder within the Docker container. If the user has checked out MBL, then the folder
    will already be at the level of Buildings folder, otherwise, the user most likely is
    developing from a git checkout and we need to go down one level to get to the Buildings.
    """
    if Path('/mnt/lib/mbl/package.mo').exists():
        mbl_path = Path('/mnt/lib/mbl')
        mbl_package_file = mbl_path / 'package.mo'
    elif Path('/mnt/lib/mbl/Buildings/package.mo').exists():
        mbl_path = Path('/mnt/lib/mbl/Buildings')
        mbl_package_file = mbl_path / 'package.mo'
    else:
        error_str = 'Could not find Modelica Buildings Library in /mnt/lib/mbl or /mnt/lib/mbl/Buildings.'
        raise Exception(error_str)

    # Read the version of the MBL which will be needed for OpenModelica to be
    # configured correctly
    mbl_version = Path(mbl_package_file).read_text().split('version="')[1].split('"')[0]

    # create the symlink to the MBL
    mbl_link = f'/root/.openmodelica/libraries/Buildings {mbl_version}'
    if not os.path.exists(mbl_link):
        os.symlink(mbl_path, mbl_link)


def compile_fmu(model_name) -> str:
    """Compile a modelica model with OpenModelica.

    (Do not rename this function to `compile` as it is reserved in Python.)

    CLI Usage: omc [Options] (Model.mo | Script.mos) [Libraries | .mo-files]
             * Libraries: Fully qualified names of libraries to load before processing Model or Script.
             The libraries should be separated by spaces: Lib1 Lib2 ... LibN.
    """
    # Call OMC to compile the model, using MSL & MBL libraries
    cmd = "omc compile_fmu.mos"
    logger.info(f"Calling OpenModelica compile with '{cmd}'")
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    os.system(cmd)
    return f"{model_name}.fmu"


def run_as_fmu(fmu_name, start: Optional[float], stop: Optional[float], step: Optional[float]) -> str:
    # TODO: what if start, stop, or step is not specified?
    """Run a modelica model with OpenModelica.
    CLI Usage: OMSimulator [Options] [Lua script] [FMU] [SSP file]
    """
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    cmd = f"OMSimulator --startTime={start} --stopTime={stop} --stepSize={step} {fmu_name}"
    logger.info(f"Calling OpenModelica simulator with '{cmd}'")
    os.system(cmd)
    return f'{fmu_name} has been simulated'


def run_with_omc() -> bool:
    """Compile and run the model with OpenModelica. This method does not generate the FMU.
    A model_name is not passed since the simulate.mos script was generated during the
    setup.

    Returns:
        bool: Always true for now
    """
    # Call OMC to compile the model, using MSL & MBL libraries
    cmd = "omc simulate.mos"
    logger.info(f"Calling OpenModelica simulate with '{cmd}'")
    # Uncomment this section and rebuild the container in order to pause the container
    # to inpsect the container and test commands.
    # import time
    # time.sleep(10000)
    os.system(cmd)

    # remove the 'tmp' folder that was created, because it will
    # have different permissions than the user running the container
    path = Path(__file__).parent.absolute()
    if (path / 'tmp' / 'temperatureResponseMatrix').exists():
        shutil.rmtree(path / 'tmp' / 'temperatureResponseMatrix')
        # check if the tmp folder is empty now, and if so remove
        if not any((path / 'tmp').iterdir()):
            (path / 'tmp').rmdir()

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model: compile, run, compile_and_run')
    parser.add_argument('model', help='Name(path) of the model to run, if debug, then will use test PID model. Can be an mo file or an FMU')  # noqa
    parser.add_argument('run_path', help='Path to the model you want to run')
    parser.add_argument('start_time', help='Start time of the simulation.', nargs='?')
    parser.add_argument('end_time', help='End time of the simulation.', nargs='?')
    parser.add_argument('sim_step', help='Time step of the simulation.', nargs='?')

    # Since this command is passed with om.py, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()
    args.run_path = Path(args.run_path)

    logger.info(f'args: {args}')

    if args.action == 'help':
        print(parser.print_help())  # type: ignore

    logger.info('Configuring MBL path')
    configure_mbl_path()

    fmu_name = None
    if args.action == 'compile':
        model = args.model

        if Path(model).is_file():
            model = str((args.run_path / model)).replace(os.path.sep, '.')[:-3]
            if model[0] == '.':
                model = model[1:]

        logger.info(f'Compiling {model}')
        compile_fmu(model)

    if args.action == 'compile_and_run':
        model = args.model

        if Path(model).is_file():
            model = str((args.run_path / model)).replace(os.path.sep, '.')[:-3]
            if model[0] == '.':
                model = model[1:]

        logger.info(f'Running model {model} with OMC')
        fmu_name = run_with_omc()

    if args.action == 'run':
        model = args.model

        if Path(model).exists():  # type: ignore
            # TODO: This still needs to be implemented since the FMU runner isn't
            # loading correctly.
            # run_as_fmu(fmu_name, args.start_time, args.end_time, args.sim_step)
            run_as_fmu(model, 0, 1, 0.05)
        else:
            print(f"FMU model does not exist: {model}")
