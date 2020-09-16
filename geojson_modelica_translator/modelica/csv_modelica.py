"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""
#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd

class CSVModelica(object):

   def __init__(self,scaffold,res_dir, input_csv_file_name):
        self.scaffold= scaffold
        self.res_dir = scaffold.load_path.resources_dir
        # read the whole data set
        timeseries_output = pd.read_csv(input_csv_file_name)
        # round the data command
        timeseries_output= timeseries_output.round(2)
        # copy the first line
        timeseries_15min= timeseries_output.loc[[0],:]
        timeseries_output = pd.concat([timeseries_output,timeseries_15min]).sort_index()
        # reset index
        timeseries_output = timeseries_output.reset_index(drop=True)
        #Nominal massFlowRate
        nominalHea_massFloRate=pd.DataFrame({'#heating':['#Nominal heating water mass flow rate'],'#value':    [timeseries_output['massFlowRateHeating'].max()]},
                                                columns=['#heating','#value'])
        nominalCoo_massFloRate=pd.DataFrame({'#cooling':['#Nominal chilled water mass flow rate'],'#value':[timeseries_output['massFlowRateCooling'].max()]},
                                                columns=['#cooling','#value'])

    def timeseries_to_modelica_data(file_path, EnergyPlustimestep, data_type, output_modelica_file_name):
# evaluate dimensions of the matrix
        size = timeseries_output.shape
# modifiy the index for modelica mos
        timeseries_output.index = (timeseries_output.index)*EnergyPlustimestep
        timeseries_output.index.name = '#time'
        timeseries_output.drop(['Date/Time'], axis=1, inplace=True)
# write to csv for modelica
        file = file_name + '.csv'
        with open(file,'w') as f:
            line1 = '#1'
            line2 = data_type + ' ' + file_name + '(' + str(size[0]) + ',' + str(size[1])  + ')'
            line3 = '#Nominal heating water mass flow rate=' + str(nominalHea_massFloRate.loc[0,'#value'])
            line4 = '#Nominal chilled water mass flow rate=' + str(nominalCoo_massFloRate.loc[0,'#value'])
            f.write('{}\n' '{}\n' '{}\n' '{}\n'.format(line1,line2,line3,line4))
            timeseries_output.to_csv(f, header=True)


file_path = os.path.abspath('Mass_Flow_Rates_Temperatures.csv')
energyPlus_timestep =  60*15
data_type = 'double'
output_modelica_file_name = 'modelica'
obj= CSVModelica(None,file_path)
obj.timeseries_to_modelica_data(file_path, EnergyPlustimestep, data_type, output_modelica_file_name)
