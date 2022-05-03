##########################################################################
# Script to simulate Modelica models with JModelica.
#
##########################################################################
# Import the function for compilation of models and the load_fmu method

import argparse
import os
import shutil
import sys

import pymodelica
from pyfmi import load_fmu
from pymodelica import compile_fmu

#    import matplotlib.pyplot as plt
debug_solver = False


def compile(model):
    print("*** Compiling {}".format(model))
    # Increase memory
    pymodelica.environ['JVM_ARGS'] = '-Xmx4096m'

    sys.stdout.flush()

    ######################################################################
    # Compile fmu
    fmu_name = compile_fmu(model,
                           version="2.0",
                           compiler_log_level='warning',
                           compiler_options={"generate_html_diagnostics": False,
                                             "nle_solver_tol_factor": 1e-2})

    return fmu_name


def run(fmu_name):
    ######################################################################
    # Load model
    mod = load_fmu(fmu_name, log_level=3)

    ######################################################################
    # Retrieve and set solver options
    x_nominal = mod.nominal_continuous_states
    opts = mod.simulate_options()  # Retrieve the default options

    opts['solver'] = 'CVode'
    opts['ncp'] = 5000

    if opts['solver'].lower() == 'cvode':
        # Set user-specified tolerance if it is smaller than the tolerance in the .mo file
        rtol = 1.0e-6
        x_nominal = mod.nominal_continuous_states

        if len(x_nominal) > 0:
            atol = rtol * x_nominal
        else:
            atol = rtol

        opts['CVode_options'] = {
            'external_event_detection': False,
            'maxh': (mod.get_default_experiment_stop_time() - mod.get_default_experiment_start_time()) / float(opts['ncp']),
            'iter': 'Newton',
            'discr': 'BDF',
            'rtol': rtol,
            'atol': atol,
            'store_event_points': True
        }

    if debug_solver:
        opts["logging"] = True  # <- Turn on solver debug logging
        mod.set("_log_level", 6)

    ######################################################################
    # Simulate
    mod.simulate(options=opts)
    #        logging.error(traceback.format_exc())

    #    plt.plot(res['time'], res['x1'])
    #    plt.plot(res['time'], res['x2'])
    #    plt.xlabel('time in [s]')
    #    plt.ylabel('line2.y')
    #    plt.grid()
    #    plt.show()
    #    plt.savefig("plot.pdf")

    ######################################################################
    # Copy style sheets.
    # This is a hack to get the css and js files to render the html diagnostics.
    htm_dir = os.path.splitext(os.path.basename(fmu_name))[0] + "_html_diagnostics"
    if os.path.exists(htm_dir):
        for fil in ["scripts.js", "style.css", "zepto.min.js"]:
            src = os.path.join(".jmodelica_html", fil)
            if os.path.exists(src):
                des = os.path.join(htm_dir, fil)
                shutil.copyfile(src, des)

    ######################################################################
    # Get debugging information
    if debug_solver:
        # Load the debug information
        from pyfmi.debug import CVodeDebugInformation
        debug = CVodeDebugInformation(model.replace(".", "_") + "_debug.txt")

        # Below are options to plot the order, error and step-size evolution.
        # The error methos also take a threshold and a region if you want to
        # limit the plot to a certain interval.

        # Plot order evolution
        debug.plot_order()

        # Plot error evolution
        debug.plot_error()  # Note see also the arguments to the method

        # Plot the used step-size
        debug.plot_step_size()

        # See also debug?


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
