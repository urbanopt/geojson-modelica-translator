import argparse
import os
import re


def compile_fmu(model_name, modelica_path):
    """
    Compile a modelica model.
    This function shamelessly stolen from https://github.com/NREL/MegaBOP/blob/main/pymodelica/compiler.py#L11
    """
    # Spawn's implementation doesn't currently handle *.mo files in the modelica_path,
    # it is expecting only directories,
    # however BOPTEST's parser will include wrapped.mo in the modelica_path.
    # This is a workaround to elliminate .mo items from modelica_path
    modelica_path = ' '.join([p for p in modelica_path if not re.match(r'.*\.mo$', p)])

    cmd = f'spawn modelica --modelica-path {modelica_path} --fmu-type ME --create-fmu {model_name}'
    os.system(cmd)
    return f'{model_name}.fmu'


def run(fmu_name, model_name, output_path, log_level):
    """
    Run a modelica model.
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform on the model, complile, run, compile_and_run')
    parser.add_argument('model', help='Name of the model to run, if debug, then will use test PID model.')
    # Since this command is passed with jm_ipython, you can't use the -- args (e.g., --compile).
    # So we are just passing in the action and then the model to act on.
    # The actions can be (e.g., complile, run, compile_and_run)
    args = parser.parse_args()

    if args.action == 'help':
        print(parser.print_help())

    fmu_name = None
    if args.action == 'compile' or args.action == 'compile_and_run':
        model = args.model
        if args.model == 'debug':
            model = "Buildings.Controls.OBC.CDL.Continuous.Validation.LimPID"
        else:
            if os.path.isfile(args.model):
                model = args.model.replace(os.path.sep, '.')[:-3]
        fmu_name = compile(model)

    if args.action == 'run' or args.action == 'compile_and_run':
        # Run the FMU either that is passed in or from the previous step
        if not fmu_name:
            fmu_name = args.model
        if os.path.exists(fmu_name):
            run(fmu_name)
        else:
            print("FMU model does not exist: {}".format(fmu_name))
