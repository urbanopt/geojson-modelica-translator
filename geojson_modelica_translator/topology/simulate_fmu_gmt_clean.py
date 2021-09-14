import json
import os
# import subprocess
import sys

# import buildingspy
import pandas as pd
# import pkg_resources
from buildingspy.io.outputfile import Reader

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


def simulate(bldg_1_conn):
    os.system('poetry run uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json')

    with open("sys_param.json", "r+") as jsonFile:
        data = json.load(jsonFile)  # returns a dict

    if bldg_1_conn < 0.5:  # need to map to a particular bldg, could put these all into some sort of dict
        data['buildings']['custom'][0]['load_model'] = 'ind'  # otherwise, leave it as is
        ind_energy = pd.read_csv('in.csv')  # Need to specify file name
        elec_ind = sum(ind_energy['Electricity:Facility [J](TimeStep)'])  # Needs to have EnergyPlus column headings preserved
        gas_ind = sum(ind_energy['NaturalGas:Facility [J](TimeStep) '])  # Extra space present at end of clmn heading in csv from E+

    with open("sys_param.json", 'w') as fp:
        json.dump(data, fp)
        fp.write('\n')

    os.system('poetry run uo_des create-model sys_param.json example_project.json model_from_sdk')

    # os.system('uo_des run-model model_from_sdk')

    # need to add in post-processing of results, and add in alternative load profile for ind case

    r = Reader('results/mixed_loads_Districts_DistrictEnergySystem_result_rev_HHWST_rev_Spawn.mat', 'dymola')  # subsitute in file name
    # assumes existing structure of CHW plant model
    elec_DES = r.integral('cooPla_9b327f8c.mulChiSys.P[1]') + r.integral('cooPla_9b327f8c.mulChiSys.P[2]')  # result in J
    gas_DES = r.integral('heaPla_65f1ca03.senMasFlo.m_flow') * (r.mean('heaPla_65f1ca03.THWSup.T') - r.mean('heaPla_65f1ca03.THWRet.T')) \
        * heat_cap_water  # result in J

    # combine overall gas and elec
    elec_total = elec_DES + elec_ind
    gas_total = gas_DES + gas_ind

    # calculate source energy
    source_enr_tot = source_site_elec * elec_total + source_site_gas * gas_total

    return source_enr_tot
