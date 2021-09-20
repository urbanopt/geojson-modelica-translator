# compile and simulate the model here, called separately by the measure
# make sure this approach works with the measure ! it shouldn't need to pass any files=>should just be persisted in the directory
#  need to adjust path so that it can find modules

# import pandas as pd

# import buildingspy
# import pkg_resources
# from buildingspy.io.outputfile import Reader
import os

import pymodelica
from pyfmi import load_fmu

os.environ['JMODELICA_HOME'] = '/usr/local/JModelica'

name = 'Districts.DistrictEnergySystem'
file_path = '/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/'


def compile_and_simulate(bldg_1_conn):
    os.chdir(file_path)

    compile_options = {'runtime_log_to_file': True, 'generate_html_diagnostics': True, 'log_level': 6}

    fmu = pymodelica.compile_fmu(name, compiler_options=compile_options, compiler_log_level='d', jvm_args='-Xmx10g', target='cs')
    fmu_sim = load_fmu(fmu)
    fmu_sim.simulate(start_time=0, final_time=5)  # could assign to res later # update simulation time!
