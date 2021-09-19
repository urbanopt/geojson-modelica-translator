import json
import os
# import subprocess
import sys

# import buildingspy
import pandas as pd
# import pkg_resources
from buildingspy.io.outputfile import Reader

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
file_path = '/opt/openstudio/server/MAT_File/mixed_loads_rev_sca_fac_2/CSV/GMT/geojson-modelica-translator/tests/ \
    management/data/sdk_project_scraps/'

results_file_name = '/opt/openstudio/server/MAT_File/mixed_loads_rev_sca_fac_2/mixed_loads_Districts_DistrictEnergySystem_result.mat'


def simulate(bldg_1_conn):
    os.system('poetry run uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json')
    with open("sys_param.json", "r+") as jsonFile:
        data = json.load(jsonFile)  # returns a dict

    if bldg_1_conn < 0.5:  # need to map to a particular bldg, could put these all into some sort of dict
        data['buildings']['custom'][0]['load_model'] = 'ind'  # otherwise, leave it as is
        ind_energy = pd.read_csv('in.csv')  # Need to specify file name
        elec_ind = sum(ind_energy['Electricity:Facility [J](TimeStep)'])  # Needs to have EnergyPlus column headings preserved
        gas_ind = sum(ind_energy['NaturalGas:Facility [J](TimeStep) '])  # Extra space present at end of clmn heading in csv from E+
    else:
        elec_ind = 0
        gas_ind = 0

    with open("sys_param.json", 'w') as fp:
        json.dump(data, fp)
        fp.write('\n')

    os.system('poetry run uo_des create-model sys_param.json example_project.json model_from_sdk')

    # os.system('uo_des run-model model_from_sdk')

    # need to add in post-processing of results, and add in alternative load profile for ind case

    r = Reader(results_file_name, 'dymola')  # subsitute in file name
    # assumes existing structure of CHW plant model

    # get var names for clg
    chiller_var_names = r.varNames('mulChiSys.P')
    if len(chiller_var_names) != 2:
        print("Variable names for chiller energy use, printed below, may not have been identified correctly.")
        print(chiller_var_names)
    # add a test for # of results?
    elec_DES = r.integral(chiller_var_names[0]) + r.integral(chiller_var_names[1])  # result in J
    # get var names for htg
    htg_var_names_mdot = r.varNames('heaPla.*senMasFlo.m_flow')
    htg_var_names_mdot_int = [i for i in htg_var_names_mdot if not ('pum' in i or 'nominal' in i)]
    htg_st_var_output = r.varNames('heaPla.*THWSup.T')
    htg_st_var_int = [i for i in htg_st_var_output if not ('start' in i or 'Amb' in i or 'inflow' in i or 'TMed' in i or 'der' in i)]
    htg_rt_var_output = r.varNames('heaPla.*THWRet.T')
    htg_rt_var_int = [i for i in htg_rt_var_output if not ('start' in i or 'Amb' in i or 'inflow' in i or 'TMed' in i or 'der' in i)]
    gas_DES = (r.integral(htg_var_names_mdot_int[0]) * (r.mean(htg_st_var_int[0]) - r.mean(htg_rt_var_int[0]))
               * heat_cap_water)/boiler_eff  # result in J

    # combine overall gas and elec
    elec_total = elec_DES + elec_ind
    gas_total = gas_DES + gas_ind

    # calculate source energy
    source_enr_tot = source_site_elec * elec_total + source_site_gas * gas_total

    return source_enr_tot
