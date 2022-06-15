import argparse
import os
import re
from pathlib import Path


def compile_fmu(model_name, modelica_path, compiler):
    """
    Compile a modelica model.
    This function shamelessly stolen from https://github.com/NREL/MegaBOP/blob/main/main/pymodelica/compiler.py#L11
    and only lightly modified.
    """

    # Spawn's implementation doesn't currently handle *.mo files in the modelica_path.
    # It is expecting only directories.
    # This is a workaround to eliminate .mo items from modelica_path
    # FIXME: GMT is passing a dir, correct? So this modelica_path line isn't necessary?
    modelica_path = ' '.join([p for p in modelica_path if not re.match(r'.*\.mo$', p)])
    mbl_path = f"{os.environ['MODELICAPATH']}/Buildings"

    cmd = f'spawn modelica --create-fmu {model_name} --modelica-path {modelica_path} {mbl_path} --fmu-type ME --{compiler}'
    os.system(cmd)
    return f'{model_name}.fmu'


def run(fmu_name):
    """
    Run a modelica model with Spawn.
    """

    # TODO: Decide if start, stop, or step should be exposed to the user.
    cmd = f"spawn fmu --simulate {fmu_name} --start 0.0 --stop 86400 --step 300"
    os.system(cmd)
    return f'{fmu_name} has been simulated'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model: compile, run, compile_and_run')
    parser.add_argument('model', help='Name of the model to run, if debug, then will use test PID model.')
    parser.add_argument('fmu_name', help='Optional, name of pre-built FMU to simulate.')
    parser.add_argument('modelica_path', help='Path to the project folder.')
    parser.add_argument('compiler', help='Compiler to use.', default='optimica')
    # Since this command is passed with jm_ipython, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()

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
        fmu_name = compile(model, args.modelica_path, args.compiler)

    if args.action == 'run' or args.action == 'compile_and_run':
        # Run the FMU either that is passed in or from the previous step
        if not fmu_name:
            fmu_name = args.model
        if Path(fmu_name).exists():
            run(fmu_name)
        else:
            print(f"FMU model does not exist: {fmu_name}")
