"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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

from pathlib import Path

import pandas as pd


class CSVModelica(object):

    def __init__(self, input_csv_file_path, sig_fig=3):
        """
        Convert a CSV file into the format required by Modelica. Expects a file resulting from
        https://github.com/urbanopt/DES_HVAC/tree/develop/Measures/export_time_series_modelica, which is included
        in the URBANopt SDK (potentially via common-measures-gem).
        FIXME: this is in process as of 2020-11-18
        If providing a csv file not from the DES_HVAC measure, ensure it contains the following headers in this order:

        0: Date/Time, string, date time. This column isn't used and will be removed upon writing out.
        1: NODE 62:System Node Temperature[C], double, Temperature hot water return, degC
        2: NODE 67:System Node Temperature[C], double, Temperature hot water setpoint, degC
        3: NODE 70:System Node Temperature[C], double, Temperature chilled water return, degC
        4: NODE 98:System Node Temperature[C], double, Temperature chilled water setpoint, degC
        5: massFlowRateHeating, double, heating water mass flow rate, kg/s
        6: massFlowRateCooling, double, cooling water mass flow rate, kg/s

        :param input_csv_file_path: string, path to input file
        :param sig_fig: integer, number of decimal places to round input csv file to. If file has fewer sig-figs,
            this will not add trailing zeroes.
        """

        if not Path(input_csv_file_path).exists():
            raise Exception(f"Unable to convert CSV file because this path does not exist: {input_csv_file_path}")

        # read the data set
        columns_to_use = [
            'SecondsFromStart',
            'heatingReturnTemperature[C]',
            'heatingSupplyTemperature[C]',
            'massFlowRateHeating',
            'ChilledWaterReturnTemperature[C]',
            'ChilledWaterSupplyTemperature[C]',
            'massFlowRateCooling']
        try:
            self.timeseries_output = pd.read_csv(input_csv_file_path, usecols=columns_to_use).round(sig_fig)
        except ValueError:
            self.timeseries_output = pd.read_csv(input_csv_file_path).round(sig_fig)

        if 'massFlowRateHeating' not in self.timeseries_output.columns \
                or 'massFlowRateCooling' not in self.timeseries_output.columns:
            raise Exception(f'Columns are missing or misspelled in your file: {input_csv_file_path}')

        if 'SecondsFromStart' in self.timeseries_output.columns:
            self.timeseries_output['heatingReturnTemperature[C]'] = self.timeseries_output[
                'heatingReturnTemperature[C]'].round(1)
            self.timeseries_output['heatingSupplyTemperature[C]'] = self.timeseries_output[
                'heatingSupplyTemperature[C]'].round(1)
            self.timeseries_output['ChilledWaterReturnTemperature[C]'] = self.timeseries_output[
                'ChilledWaterReturnTemperature[C]'].round(1)
            self.timeseries_output['ChilledWaterSupplyTemperature[C]'] = self.timeseries_output[
                'ChilledWaterSupplyTemperature[C]'].round(1)
        elif 'NODE 62:System Node Temperature[C]' in self.timeseries_output.columns:
            self.timeseries_output['NODE 62:System Node Temperature[C]'] = self.timeseries_output[
                'NODE 62:System Node Temperature[C]'].round(1)
            self.timeseries_output['NODE 67:System Node Temperature[C]'] = self.timeseries_output[
                'NODE 67:System Node Temperature[C]'].round(1)
            self.timeseries_output['NODE 70:System Node Temperature[C]'] = self.timeseries_output[
                'NODE 70:System Node Temperature[C]'].round(1)
            self.timeseries_output['NODE 98:System Node Temperature[C]'] = self.timeseries_output[
                'NODE 98:System Node Temperature[C]'].round(1)
        else:
            raise Exception(f'Columns are missing or misspelled in your file: {input_csv_file_path}')

        # Dymola wants time to start at zero.
        # If time doesn't start at zero, copy the first line and set time column to zero.
        if (self.timeseries_output.loc[0][0] != 0):
            self.timeseries_timestep = self.timeseries_output.loc[[0], :]
            if 'SecondsFromStart' in self.timeseries_output.columns:
                self.timeseries_timestep['SecondsFromStart'] = 0
            # Putting timeseries_timestep first in the concat puts the copied row at the top
            # reset_index() makes the index unique again, while keeping the duplicated row at the top
            self.timeseries_output = pd.concat(
                [self.timeseries_timestep, self.timeseries_output]).reset_index(drop=True)

        # Extract the nominal flow rates from the file
        self.nominal_heating_mass_flow_rate = pd.DataFrame(
            {'#heating': ['#Nominal heating water mass flow rate (kg/s)'],
             '#value': [self.timeseries_output['massFlowRateHeating'].max()],
             '#units': ['kg/s']},
            columns=['#heating', '#value', '#units']
        )
        self.nominal_cooling_mass_flow_rate = pd.DataFrame(
            {'#cooling': ['#Nominal chilled water mass flow rate (kg/s)'],
             '#value': [self.timeseries_output['massFlowRateCooling'].max()],
             '#units': ['kg/s']},
            columns=['#cooling', '#value', '#units']
        )

    def timeseries_to_modelica_data(
            self,
            output_modelica_file_name,
            energyplus_timesteps_per_hour=4,
            data_type='double',
            overwrite=True):
        """
        Convert the loaded data to the format needed for Modelica by adding in the nominal heating water mass flow
        rate and the nominal cooling water mass flow rate into the header.

        :param output_modelica_file_name: string, The path to the desired output file name.
        :param data_type: string, data type being converted, defaults to double
        :param overwrite: boolean, if the resulting file exists, then overwrite, defaults to True.
        :return: file created to be ingested into Modelica
        """
        # evaluate dimensions of the matrix
        size = self.timeseries_output.shape

        minutes_per_hour = 60
        seconds_per_minute = 60
        seconds_in_timestep = int(minutes_per_hour / energyplus_timesteps_per_hour * seconds_per_minute)

        # Check if output is from DES_HVAC measure or straight from E+
        # The # symbol is needed to tell Dymola this line is a comment in the output file.
        if 'SecondsFromStart' in self.timeseries_output.columns:
            self.timeseries_output = self.timeseries_output.rename(columns={'SecondsFromStart': '#time'})
        else:
            self.timeseries_output.index = self.timeseries_output.index * seconds_in_timestep
            self.timeseries_output.index.name = '#time'
            self.timeseries_output.drop(self.timeseries_output.columns[0], axis=1, inplace=True)

        # write to csv for modelica
        if Path(output_modelica_file_name).exists() and not overwrite:
            raise Exception(f"Output file already exists and overwrite is False: {output_modelica_file_name}")

        with open(Path(output_modelica_file_name), 'w') as f:
            line1 = '#1'
            line2 = f"{data_type} {output_modelica_file_name}({size[0]}, {size[1]})"
            line3 = '#Nominal heating water mass flow rate=' + str(self.nominal_heating_mass_flow_rate.loc[0, '#value'])
            line4 = '#Nominal chilled water mass flow rate=' + str(self.nominal_cooling_mass_flow_rate.loc[0, '#value'])
            f.write('{}\n' '{}\n' '{}\n' '{}\n'.format(line1, line2, line3, line4))
            if 'SecondsFromStart' in self.timeseries_output.columns:
                self.timeseries_output.to_csv(f, header=True, index=False)
            else:
                self.timeseries_output.to_csv(f, header=True)
