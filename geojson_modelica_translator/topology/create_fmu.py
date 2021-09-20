import json
import os
# import subprocess
import sys

# from pyfmi import load_fmu
# from pymodelica import compile_fmu

sys.path.append("/usr/local/JModelica/Python")

# from subprocess import call

# import pyfmi
# from pyfmi import load_fmu

# subprocess.call([sys.executable, '-m', 'pip3', 'install', 'numpy'])
# call([sys.executable, '-m', 'pip3', 'install', 'numpy'])

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("/opt/openstudio/server/PyFMI/OCT_install/tmpinstalldir/install/Python")
heat_cap_water = 4182  # J/kg/deg C
# Site to source factors, per ESPM 2020: https://portfoliomanager.energystar.gov/pdf/reference/Source%20Energy.pdf
source_site_elec = 2.80
source_site_gas = 1.05
boiler_eff = 0.9

# update this as needed
file_path = '/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/'

results_file_name = '/opt/openstudio/server/MAT_File/mixed_loads_rev_sca_fac_2/mixed_loads_Districts_DistrictEnergySystem_result.mat'


def configure(bldg_1_conn):
    os.chdir(file_path)
    os.system('poetry run uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json')
    with open(file_path + "sys_param.json", "r+") as jsonFile:
        data = json.load(jsonFile)  # returns a dict

    if bldg_1_conn < 0.5:  # need to map to a particular bldg, could put these all into some sort of dict
        data['buildings']['custom'][0]['load_model'] = 'ind'  # otherwise, leave it as is

    with open(file_path + "sys_param.json", 'w') as fp:
        json.dump(data, fp)
        fp.write('\n')

    os.system('poetry run uo_des create-model sys_param.json example_project.json model_from_sdk')

    # os.system('uo_des run-model model_from_sdk')

    # need to add in post-processing of results, and add in alternative load profile for ind case
