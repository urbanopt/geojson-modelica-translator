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
# !/usr/bin/env python
# coding: utf-8

import os

import pandas as pd


class CSVModelica(object):

    def __init__(self, input_csv_file_path):
        """
        Convert a CSV file into the format required by Modelica. This is specific to the Mass Flow Rate file
        only as the header of the file adds in the nominal heating and cooling flow rates. Note that the columns
        of the CSV file need to be massFlorRateHeating

        :param input_csv_file_path: string, path to file to convert.
        """

        if not os.path.exists(input_csv_file_path):
            raise Exception(f"Unable to convert CSV file because it does not exist: {input_csv_file_path}")

        # read the whole data set
        self.timeseries_output = pd.read_csv(input_csv_file_path)
        # round the data command since energyplus reports too many sigfigs.
        self.timeseries_output = self.timeseries_output.round(2)
        # copy the first line since Dymola wants to have time start at zero.
        timeseries_15min = self.timeseries_output.loc[[0], :]
        self.timeseries_output = pd.concat([self.timeseries_output, timeseries_15min]).sort_index()
        # reset index
        self.timeseries_output = self.timeseries_output.reset_index(drop=True)

        # Note that the file that is in this test repo does not have the column you are looking for (massFlowRateHeating),
        # It only contains (print(self.timeseries_output.columns) -- 'NODE 62:System Node Temperature[C]',
        #        'NODE 67:System Node Temperature[C]',
        #        'NODE 70:System Node Temperature[C]',
        #        'NODE 98:System Node Temperature[C]',
        #        'NODE 62:System Node Mass Flow Rate[kg/s]',
        #        'NODE 67:System Node Mass Flow Rate[kg/s]',
        #        'NODE 70:System Node Mass Flow Rate[kg/s]',
        #        'NODE 98:System Node Mass Flow Rate[kg/s]',

        # Nominal massFlowRate.
        self.nominal_heating_mass_flow_rate = pd.DataFrame(
            {'#heating': ['#Nominal heating water mass flow rate'],
             '#value': [self.timeseries_output['massFlowRateHeating'].max()]},
            columns=['#heating', '#value']
        )
        self.nominal_cooling_mass_flow_rate = pd.DataFrame(
            {'#cooling': ['#Nominal chilled water mass flow rate'],
             '#value': [self.timeseries_output['massFlowRateCooling'].max()]},
            columns=['#cooling', '#value']
        )

    def timeseries_to_modelica_data(self, output_modelica_file_name, energyplus_timestep=15, data_type='double', overwrite=True):
        """
        Convert the loaded data to the format needed for Modelica by adding in the nominal heating water mass flow
        rate and the nominal cooling water mass flow rate into the header.

        :param output_modelica_file_name: string, The name of the outputfile. The extension is automatically added.
        :param energyplus_timestep: int, EnergyPlus timestep, defaults to 15
        :param data_type: string, data type being converted, defaults to double
        :param overwrite: boolean, if the resulting file exists, then overwrite, defaults to True.
        :return:
        """
        # evaluate dimensions of the matrix
        size = self.timeseries_output.shape
        print(size)
        print(self.timeseries_output.index)
        # modify the index for modelica mos
        self.timeseries_output.index = self.timeseries_output.index * energyplus_timestep
        self.timeseries_output.index.name = '#time'
        # Date
        self.timeseries_output.drop(['Date/Time'], axis=1, inplace=True)
        # write to csv for modelica
        output_modelica_file_name_full = f'{output_modelica_file_name}.csv'
        if os.path.exists(output_modelica_file_name_full) and not overwrite:
            raise Exception(f"Output file already exists and overwrite is False: {output_modelica_file_name}")

        print(output_modelica_file_name)
        print(os.path.basename(output_modelica_file_name))
        with open(output_modelica_file_name_full, 'w') as f:
            line1 = '#1'
            line2 = f"{data_type} {os.path.basename(output_modelica_file_name)}({size[0]}, {size[1]})"
            line3 = '#Nominal heating water mass flow rate=' + str(self.nominal_heating_mass_flow_rate.loc[0, '#value'])
            line4 = '#Nominal chilled water mass flow rate=' + str(self.nominal_cooling_mass_flow_rate.loc[0, '#value'])
            f.write('{}\n' '{}\n' '{}\n' '{}\n'.format(line1, line2, line3, line4))
            self.timeseries_output.to_csv(f, header=True)
