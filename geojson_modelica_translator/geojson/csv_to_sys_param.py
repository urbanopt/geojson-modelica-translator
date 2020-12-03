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

# import logging
# import geojson
# import json
from pathlib import Path
import pandas as pd
# from geojson_modelica_translator.geojson.schemas import Schemas

# _log = logging.getLogger(__name__)

class CSVToSysParam(object):
    """
    Parser for URBANopt output to write a system_parameters file
    """
    pass

    def __init__(self, input_mfrt_file=None, input_loads_file=None):
        if Path(input_mfrt_file).exists() and Path(input_loads_file).exists():
            self.input_mfrt_file = pd.read_csv(input_mfrt_file)
            self.input_loads_file = pd.read_csv(input_loads_file)
        else:
            raise Exception(f"Unable to convert CSV file because one of these paths does not exist: \
                \n{Path(input_mfrt_file)}\n{Path(input_loads_file)}")

    def csv_to_sys_param(self, sys_param_filename, overwrite=True):
        if Path(sys_param_filename).exists() and not overwrite:
            raise Exception(f"Output file already exists and overwrite is False: {sys_param_filename}")

        sys_param_starter = {
            "Buildings": {
                "default": {
                    "load_model": "time_series",
                    "ets_model": None,
                    "ets_model_parameters": {
                        "indirect": {
                            "q_flow_nominal": None,
                            "eta_efficiency": None,
                            "nominal_flow_district": None,
                            "nominal_flow_building": None,
                            "pressure_drop_valve": None,
                            "pressure_drop_hx_secondary": None,
                            "pressure_drop_hx_primary": None,
                            "cooling_supply_water_temperature_district": None,
                            "cooling_supply_water_temperature_building": None,
                            "heating_supply_water_temperature_district": None,
                            "heating_supply_water_temperature_building": None,
                            "booster_heater": False,
                            "ets_generation": None
                        }
                    }
                }
            },
            "custom": [
                "asdf",
                "jkl;"
            ]
        }

        # Build starter dataframe of sys_params json file
        self.sys_param_df = pd.DataFrame.from_dict(sys_param_starter)

        ## Populate the starter df
        # Scaffold for Filepaths and thermal zones
        # self.sys_param_df['Buildings']['default']['load_model_parameters'] = {self.sys_param_df["Buildings"]["default"]["load_model"]: {
        #                         "idf_filename": None,
        #                         "epw_filename": None,
        #                         "mos_weather_filename": None,
        #                         "mos_wet_bulb_filename": None,
        #                         "thermal_zone_names": None
        #                     }
        # }

        # Thermal zone names
        # input_loads_columns = list(self.input_loads_file.columns)
        # thermal_zone_names = []
        # for column_header in input_loads_columns:
        #     if 'Zone' in column_header:
        #         thermal_zone_names.append(column_header.split('_')[-1])
        # thermal_zone_names = list((set(thermal_zone_names)))
        # self.sys_param_df['Buildings']['default']['load_model_parameters']['time_series']['thermal_zone_names'] = thermal_zone_names

        # Default cooling plant
        # self.sys_param_df['district_system']['default']['cooling_plant'] = {
        #                 "delta_t_nominal": None,
        #                 "fan_power_nominal": None,
        #                 "chilled_water_pump_pressure_drop": None,
        #                 "condenser_water_pump_pressure_drop": None
        #             }

        # self.sys_param_df['Buildings']['default']['ets_model_parameters']['nominal_flow_building'] = self.input_mfrt_file['massFlowRateHeating'].max()

        building_1 = {
            "geojson_id": 1234,
            "load_model": "time_series",
            "load_model_parameters": {
                "time_series": {
                    "filepath": None,
                    "delTDisCoo": None
                }
            }
        }

        building_2 = {
            "geojson_id": "asdf"
        }

        # self.sys_param_df["custom"] = [building_1, building_2]

        self.sys_param_df.to_json(sys_param_filename, indent=2)
