# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import re
import pandas as pd
import numpy 

from buildingspy.io.outputfile import Reader


class ResultsModelica:
    """Results from Modelica Project Simulation"""

    def __init__(self, sys_param_file, modelica_project):
        self._sys_param_file = sys_param_file
        self._modelica_project = modelica_project

    def calculate_results(self, sys_param_file, modelica_project):
        """Calculate timeseries results for a previously run Modelica project."""
        result_mat_file = os.path.join(modelica_project, f"{modelica_project}.Districts.DistrictEnergySystem_results", f"{modelica_project}.Districts.DistrictEnergySystem_res.mat")

        if os.path.exists(result_mat_file):
            print(f"The path {result_mat_file} exists.")
        else:
            print(f"The path {result_mat_file} does not exist.")
          
        results=Reader(result_mat_file, "dymola")

        heating_electric_power = results.varNames(r'^TimeSerLoa_\w+\.PHea$')

        heating_electric_power = results

       






