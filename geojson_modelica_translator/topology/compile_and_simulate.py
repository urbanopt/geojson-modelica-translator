import os

# Below may need to be uncommented
# os.environ['JMODELICA_HOME'] = '/usr/local/JModelica'
# os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
# os.environ['MODELICAPATH'] = '/usr/local/JModelica/ThirdParty/MSL:/opt/openstudio/server/modelica-buildings: \
# /opt/openstudio/server/modelica-buildings/Buildings: \
# /opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps: \
# /opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/model_from_sdk'
# os.environ['LDFLAGS'] = '/usr/local/JModelica/ThirdParty/Sundials/lib'
# os.environ['LIBRARY_PATH'] = '/usr/local/JModelica/ThirdParty/Sundials/lib'
# os.environ['LD_LIBRARY_PATH'] = '/usr/local/JModelica/ThirdParty/Sundials/lib'
import pyfmi
import pymodelica

name = 'Districts.DistrictEnergySystem'
file_path = '/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/'
fmu_name = 'Districts_DistrictEnergySystem.fmu'

starting_time = 0  # s
end_time = 31536000  # s, full year


def compile_and_simulate(bldg_1_conn):
    os.chdir(file_path)

    compile_options = {'runtime_log_to_file': True, 'generate_html_diagnostics': True, 'log_level': 6}

    # fmu=pymodelica.compile_fmu(name, compiler_options=compile_options, compiler_log_level='d', jvm_args='-Xmx10g', target='cs')
    pymodelica.compile_fmu(name, compiler_options=compile_options, compiler_log_level='d', target='cs')
    fmu_sim = pyfmi.load_fmu(fmu_name)
    fmu_sim.simulate(start_time=starting_time, final_time=end_time)  # could assign to res later # update simulation time!
