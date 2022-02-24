import os

import pymodelica
from pyfmi import load_fmu

os.environ['JMODELICA_HOME'] = '/usr/local/JModelica'

name = 'Districts.DistrictEnergySystem'
file_path = '/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/'
fmu_name = 'Districts_DistrictEnergySystem.fmu'


def compile_and_simulate(bldg_1_conn):
    os.chdir(file_path)

    compile_options = {'runtime_log_to_file': True, 'generate_html_diagnostics': True, 'log_level': 6}
    pymodelica.compile_fmu(name, compiler_options=compile_options, compiler_log_level='d', target='cs')
    # spawn modelica --create-fmu Districts.DistrictEnergySystem  # spawn approach to be implemented in future
    fmu_sim = load_fmu(fmu_name)
    fmu_sim.simulate(start_time=0, final_time=30)  # Simulation time can be updated
