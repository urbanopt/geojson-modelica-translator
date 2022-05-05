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

import json
import logging
import os
from copy import deepcopy
from pathlib import Path

import pandas as pd
import requests
from jsonpath_ng.ext import parse
from jsonschema.validators import _LATEST_VERSION as LatestValidator

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class SystemParameters(object):
    """
    Object to hold the system parameter data (and schema).
    """

    PATH_ELEMENTS = [
        {"json_path": "$.buildings.default.load_model_parameters.spawn.idf_filename"},
        {"json_path": "$.buildings.default.load_model_parameters.spawn.epw_filename"},
        {"json_path": "$.buildings.default.load_model_parameters.spawn.mos_weather_filename"},
        {"json_path": "$.buildings.default.load_model_parameters.rc.mos_weather_filename"},
        {"json_path": "$.buildings.default.load_model_parameters.time_series.filepath"},
        {"json_path": "$.buildings.*[?load_model=spawn].load_model_parameters.spawn.idf_filename"},
        {"json_path": "$.buildings.*[?load_model=spawn].load_model_parameters.spawn.epw_filename"},
        {"json_path": "$.buildings.*[?load_model=spawn].load_model_parameters.spawn.mos_weather_filename"},
        {"json_path": "$.buildings.*[?load_model=rc].load_model_parameters.rc.mos_weather_filename"},
        {"json_path": "$.buildings.*[?load_model=time_series].load_model_parameters.time_series.filepath"},
        {"json_path": "$.buildings.*[?load_model=time_series_massflow_temperature].load_model_parameters.time_series.filepath"},
        {"json_path": "$.district_system.default.central_cooling_plant_parameters.weather_filepath"},
        {"json_path": "$.combined_heat_and_power_systems.*.performance_data_path"}
    ]

    def __init__(self, filename=None):
        """
        Read in the system design parameter file

        :param filename: string, (optional) path to file to load
        """
        # load the schema for validation
        schema = Path(__file__).parent / "schema.json"
        self.schema = json.loads(schema.read_text())
        self.data = {}
        self.filename = filename

        if self.filename:
            if Path(self.filename).exists():
                with open(self.filename, "r") as f:
                    self.data = json.load(f)
            else:
                raise Exception(f"System design parameters file does not exist: {self.filename}")

            errors = self.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

            self.resolve_paths()
            # self.resolve_defaults()

        self.param_template = {}
        self.sys_param_filename = None

    @classmethod
    def loadd(cls, d, validate_on_load=True):
        """
        Create a system parameters instance from a dictionary
        :param d: dict, system parameter data

        :return: object, SystemParameters
        """
        sp = cls()
        sp.data = d

        if validate_on_load:
            errors = sp.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

        return sp

    def resolve_paths(self):
        """Resolve the paths in the file to be absolute if they were defined as relative. This method uses
        the JSONPath (with ext) to find if the value exists in the self.data object. If so, it then uses
        the set_param which navigates the JSON tree to set the value as needed."""
        filepath = Path(self.filename).parent.resolve()

        for pe in self.PATH_ELEMENTS:
            matches = parse(pe["json_path"]).find(self.data)
            for index, match in enumerate(matches):
                # print(f"Index {index} to update match {match.path} | {match.value} | {match.context}")
                new_path = Path(filepath) / match.value
                parse(str(match.full_path)).update(self.data, new_path.as_posix())

    # def resolve_defaults(self):
    #     """This method will expand the default data blocks into all the subsequent custom sections. If the value is
    #     specificed in the custom block then that will be used, otherwise the default value will be replaced"""
    #     pass

    def get_default(self, jsonpath, default=None):
        """Return either the default in the system parameter file, or the specified default.

        :param jsonpath: string, raw jsonpath to what parameter was being requested
        :param default: variant, default value
        :return: value
        """
        schema_default = self.get_param(jsonpath, impute_default=False)
        return schema_default or default

    def get_param(self, jsonpath, data=None, default=None, impute_default=True):
        """Return the parameter(s) from a jsonpath. If the default is not specified, then will attempt to read the
        default from the "default" section of the file. If there is no default there, then it will use the value
        specified as the argument. It is not recommended to use the argument default as those values will not be
        configurable. Argument-based defaults should be used sparingly.

        :param path: string, period delimited path of the data to retrieve
        :param data: dict, (optional) the data to parse
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """
        if jsonpath is None or jsonpath == "":
            return None

        # If this is the first entry into the method, then set the data to the
        data = data or self.data
        matches = parse(jsonpath).find(data)

        default_value = default
        if impute_default:
            default_value = self.get_default(jsonpath, default)

        results = []
        for index, match in enumerate(matches):
            # print(f"Index {index} to update match {match.path} | {match.value} | {match.context}")
            if match.value is None:
                results.append(default_value)
            else:
                results.append(match.value)

        if len(results) == 1:
            # If only one value, then return that value and not a list of values
            results = results[0]
        elif len(results) == 0:
            return default_value

        # otherwise return the list of values
        return results

    def get_param_by_building_id(self, building_id, jsonpath, default=None):
        """
        return a parameter for a specific building_id. This is similar to get_param but allows the user
        to constrain the data based on the building id.

        :param building_id: string, id of the building to look up in the custom section of the system parameters
        :param jsonpath: string, jsonpath formatted string to return
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """

        # This will get reworked after moving to jsonpath. but for now, hack in the default. First return the default
        # dict from the system parameter file.
        # Grab first the default data block, then find the path in the default data block.
        # "building.default" might need to reconsider, as it is fixed for flake8 currently.
        default_data = self.get_param("$.buildings.default", impute_default=False)
        schema_default = self.get_param(jsonpath, default_data, impute_default=False)
        default = schema_default or default
        for b in self.data.get("buildings", {}).get("custom", {}):
            if b.get("geojson_id", None) == building_id:
                return self.get_param(jsonpath, b, default=default)
        else:
            raise SystemExit("No building_id submitted. Please retry and include the feature_id")

    def validate(self):
        """
        Validate an instance against a loaded schema

        :param instance: dict, json instance to validate
        :return: validation results
        """
        results = []
        v = LatestValidator(self.schema)
        for error in sorted(v.iter_errors(self.data), key=str):
            results.append(error.message)

        return results

    def download_weatherfile(self, filename, save_directory: str) -> str:
        """Download the MOS or EPW weather file from energyplus.net

        This routine downloads the weather file, either an MOS or EPW, which is selected based
        on the file extension.

            filename, str: Name of weather file to download, e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos
            save_directory, str: Location where to save the downloaded content. The path must exist before downloading.
        """
        p_download = Path(filename)
        p_save = Path(save_directory)

        if not p_save.exists():
            raise Exception(f"Save path for the weatherfile does not exist, {str(p_save)}")

        # get country & state from weather file name
        try:
            weatherfile_location_info = p_download.parts[-1].split("_")
            weatherfile_country = weatherfile_location_info[0]
            weatherfile_state = weatherfile_location_info[1]
        except IndexError:
            raise Exception(
                "Malformed location, needs underscores of location (e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)"
            )

        # download mos file from energyplus website
        mos_weatherfile_url = 'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/' \
            f'{weatherfile_country}/{weatherfile_state}/{p_download.stem}/{p_download.name}'
        logger.debug(f"Downloading weather file from {mos_weatherfile_url}")
        try:
            mos_weatherfile_data = requests.get(mos_weatherfile_url)
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Could not download weather file: {mos_weatherfile_url}"
                "\nAt this time we only support USA weather stations"
                f"\n{e}"
            )

        # Save mos weatherfile into the requested path.
        outputname = p_save / p_download.name
        open(outputname, 'wb').write(mos_weatherfile_data.content)
        logger.debug(f"Saved weather file to {outputname}")

        # Count lines in downloaded weather file to make sure
        # that at least 8760 lines have been downloaded. This is
        # commented out for now since wc -l won't work on windows.
        # file_lines = Popen(['wc', '-l', outputname], stdout=PIPE, stderr=PIPE)
        # result, err = file_lines.communicate()
        # if file_lines.returncode != 0:
        #     raise IOError(err)
        # lines_in_weather_file = int(result.strip().split()[0])
        # logger.debug(f"Weather file {outputname} has {lines_in_weather_file} lines")
        # if lines_in_weather_file < 8760:  # There should always be header lines above the 8760 data lines
        #     raise Exception(f"Weather file {p_download.name} does not contain 8760 lines.")
        # modelica_path = f"modelica://Buildings/Resources/weatherdata/{p_download.name}"

        return outputname

    def make_list(self, inputs):
        """ Ensure that format of inputs is a list
        :param inputs: object, inputs (list or dict)
        :return: list of inputs
        """
        list_inputs = []
        if isinstance(inputs, dict) and len(inputs) != 0:
            list_inputs.append(inputs)
        else:
            list_inputs = inputs

        return list_inputs

    def process_wind(self, inputs):
        """
        Processes wind inputs and insert into template
        :param inputs: object, wind inputs
        """
        wind_turbines = []
        for item in inputs['scenario_report']['distributed_generation']['wind']:
            # nominal voltage - Default
            wt = {}
            wt['nominal_voltage'] = 480

            # scaling factor: parameter used by the wind turbine model
            # from Modelica Buildings Library, to scale the power output
            # without changing other parameters. Multiplies "Power curve"
            # value to get a scaled up power output.
            # add default = 1
            wt['scaling_factor'] = 1

            # calculate height_over_ground and power curve from REopt
            #  "size_class" (defaults to commercial) res = 2.5kW, com = 100kW, mid = 250kW, large = 2000kW
            heights = {'residential': 20, 'commercial': 40, 'midsize': 50, 'large': 80}
            size_class = None
            if item['size_class']:
                size_class = item['size_class']

            if size_class is None:
                size_class = 'commercial'

            # height over ground. default 10m
            wt['height_over_ground'] = heights[size_class]

            # add power curve
            curves = self.get_wind_power_curves()
            wt['power_curve'] = curves[size_class]

            # capture size_kw just in case
            wt['rated_power'] = item['size_kw']
            # and yearly energy produced
            wt['annual_energy_produced'] = item['average_yearly_energy_produced_kwh']

            # append to results array
            wind_turbines.append(wt)

        self.param_template['wind_turbines'] = wind_turbines

    def get_wind_power_curves(self):
        # from: https://reopt.nrel.gov/tool/REopt%20Lite%20Web%20Tool%20User%20Manual.pdf#page=61
        # curves given in Watts (W)
        power_curves = {}
        power_curves['residential'] = [[2, 0],
                                       [3, 70.542773],
                                       [4, 167.2125],
                                       [5, 326.586914],
                                       [6, 564.342188],
                                       [7, 896.154492],
                                       [8, 1337.7],
                                       [9, 1904.654883],
                                       [10, 2500]]
        power_curves['commercial'] = [[2, 0],
                                      [3, 3505.95],
                                      [4, 8310.4],
                                      [5, 16231.25],
                                      [6, 28047.6],
                                      [7, 44538.55],
                                      [8, 66483.2],
                                      [9, 94660.65],
                                      [10, 100000]]
        power_curves['midsize'] = [[2, 0],
                                   [3, 8764.875],
                                   [4, 20776],
                                   [5, 40578.125],
                                   [6, 70119],
                                   [7, 111346.375],
                                   [8, 166208],
                                   [9, 236651.625],
                                   [10, 250000]]

        power_curves['large'] = [[2, 0],
                                 [3, 70119],
                                 [4, 166208],
                                 [5, 324625],
                                 [6, 560952],
                                 [7, 890771],
                                 [8, 1329664],
                                 [9, 1893213],
                                 [10, 2000000]]
        return power_curves

    def process_pv(self, inputs, latitude):
        """
        Processes pv inputs
        :param inputs: object, pv inputs
        :return photovoltaic_panels section to be inserted per-building or globally
        """

        items = self.make_list(inputs)
        pvs = []
        # hardcode nominal_system_voltage 480V
        # add latitude
        for item in items:
            pv = {}
            pv['nominal_voltage'] = 480
            pv['latitude'] = latitude
            if 'tilt' in item:
                pv['surface_tilt'] = item['tilt']
            else:
                pv['surface_tilt'] = 0
            if 'azimuth' in item:
                pv['surface_azimuth'] = item['azimuth']
            else:
                pv['surface_azimuth'] = 0

            # Size (kW) = Array Area (m²) × 1 kW/m² × Module Efficiency (%)
            # area = size (kW) / 1 kW/m2 / module efficiency (%)
            # module efficiency tied to module type: 0 -> standard: 15%, 1-> premium: 19%, 2-> thin film: 10%
            # defaults to standard
            efficiencies = {0: 15, 1: 19, 2: 10}
            module_type = 0
            if 'module_type' in item:
                module_type = item['module_type']

            eff = efficiencies[module_type]
            pv['net_surface_area'] = item['size_kw'] / eff

            pvs.append(pv)

        return pvs

    def process_chp(self, inputs):
        """
        Processes global chp inputs and insert into template
        :param inputs: object, raw inputs
        """
        # this uses the raw inputs
        items = self.make_list(inputs['outputs']['Scenario']['Site']['CHP'])
        chps = []
        for item in items:
            # fuel type. options are: natural_gas (default), landfill_bio_gas, propane, diesel_oil
            chp = {}
            chp['fuel_type'] = 'natural_gas'
            if inputs['inputs']['Scenario']['Site']['FuelTariff']["chp_fuel_type"]:
                chp['fuel_type'] = inputs['inputs']['Scenario']['Site']['FuelTariff']["chp_fuel_type"]

            # single_electricity_generation_capacity
            chp['single_electricity_generation_capacity'] = item['size_kw']

            # performance data filename
            # TODO: not sure how to pass this in
            # how to default this? retrieve from the template, or right here in code?
            chp['performance_data_path'] = ''

            # number of machines
            # TODO: not in REopt...default?
            chp['number_of_machines'] = 1

            chps.append(chp)

        self.param_template['combined_heat_and_power_systems'] = chps

    def process_storage(self, inputs):
        """
        Processes global battery bank outputs and insert into template
        :param inputs: object, raw inputs
        """
        # this uses the raw inputs
        items = []
        try:
            items = self.make_list(inputs['scenario_report']['distributed_generation']['storage'])
        except KeyError:
            pass

        batts = []
        for item in items:

            batt = {}

            # energy capacity 'size_kwh' % 1000 to convert to MWh
            batt['capacity'] = item['size_kwh'] / 1000

            # Nominal Voltage - DEFAULT
            batt['nominal_voltage'] = 480

            batts.append(batt)

        self.param_template['battery_banks'] = batts

    def process_generators(self, inputs):
        """
        Processes generators outputs and insert into template
        :param inputs: object, raw inputs
        """
        # this uses the raw inputs
        items = []
        try:
            items = self.make_list(inputs['scenario_report']['distributed_generation']['generators'])
        except KeyError:
            pass

        generators = []
        for item in items:

            generator = {}

            # size_kw, then convert to W
            generator['nominal_power_generation'] = item['size_kw'] * 1000

            # source phase shift
            # TODO: Not in REopt
            generator['source_phase_shift'] = 0

            generators.append(generator)

        self.param_template['diesel_generators'] = generators

    def process_grid(self):
        grid = {}

        # frequency - default
        grid['frequency'] = 60
        # TODO: RMS voltage source - default
        # grid['source_rms_voltage'] = 0

        # TODO: phase shift (degrees) - default
        # grid['source_phase_shift'] = 0

        self.param_template['electrical_grid'] = grid

    def process_electrical_components(self, scenario_dir: Path):
        """ process electrical results from OpenDSS
            electrical grid
            substations
            transformers
            distribution lines
            capacitor banks (todo)
        """
        dss_data = {}
        opendss_json_file = os.path.join(scenario_dir, 'scenario_report_opendss.json')
        if (os.path.exists(opendss_json_file)):
            with open(opendss_json_file, "r") as f:
                dss_data = json.load(f)

        if dss_data:
            # ELECTRICAL GRID: completely defaulted for now
            self.process_grid()

            # SUBSTATIONS
            substations = []
            try:
                data = dss_data['scenario_report']['scenario_power_distribution']['substations']
                for item in data:
                    try:
                        s = {}
                        # TODO: default RNM Voltage (high side?)

                        # RMS Voltage (low side)
                        s['RMS_voltage_low_side'] = item['nominal_voltage']
                        substations.append(s)
                    except KeyError:
                        pass
            except KeyError:
                pass

            self.param_template['substations'] = substations

            # DISTRIBUTION LINES
            lines = []
            try:
                data = dss_data['scenario_report']['scenario_power_distribution']['distribution_lines']
                for item in data:
                    try:
                        line = {}
                        line['length'] = item['length']
                        line['ampacity'] = item['ampacity']

                        # nominal voltage is defaulted (data not available in OpenDSS)
                        line['nominal_voltage'] = 480

                        line['commercial_line_type'] = item['commercial_line_type']

                        lines.append(line)
                    except KeyError:
                        pass
            except KeyError:
                pass

            self.param_template['distribution_lines'] = lines

            # CAPACITOR BANKS
            caps = []
            try:
                data = dss_data['scenario_report']['scenario_power_distribution']['capacitors']
                for item in data:
                    try:
                        cap = {}
                        # nominal capacity (var)
                        cap['nominal_capacity'] = item['nominal_capacity']

                        caps.append(cap)
                    except KeyError:
                        pass
            except KeyError:
                pass

            self.param_template['capacitor_banks'] = caps

            # TRANSFORMERS
            transformers = []
            data = [d for d in dss_data['feature_reports'] if d['id'].startswith('Transformer')]
            for item in data:
                t = {}
                t['id'] = item['id']
                t['nominal_capacity'] = None
                if item['power_distribution']['nominal_capacity']:
                    t['nominal_capacity'] = item['power_distribution']['nominal_capacity']

                t['reactance_resistance_ratio'] = None
                if item['power_distribution']['reactance_resistance_ratio']:
                    t['reactance_resistance_ratio'] = item['power_distribution']['reactance_resistance_ratio']
                transformers.append(t)

            self.param_template['transformers'] = transformers

            # Loads (buildings from geojson file)
            # grab all the building loads
            data = [d for d in dss_data['feature_reports'] if d['feature_type'] == 'Building']

            # grab records to modify
            for bldg in self.param_template['buildings']['custom']:
                # find match in data
                match = [d for d in data if d['id'] == bldg['geojson_id']]
                if match:
                    # add data
                    bldg['load'] = {}
                    # print("Found match for {}: {}".format(bldg['geojson_id'], match[0]['id']))
                    bldg['load']['nominal_voltage'] = match[0]['power_distribution']['nominal_voltage']
                    bldg['load']['max_power_kw'] = match[0]['power_distribution']['max_power_kw']
                    bldg['load']['max_reactive_power_kvar'] = match[0]['power_distribution']['max_reactive_power_kvar']

    def process_building_microgrid_inputs(self, building, scenario_dir: Path):
        """
        Processes microgrid inputs for a single building
        :param building: list, building
        :param scenario_dir: Path, location/name of folder with uo_sdk results
        :return building, updated building list object
        """
        feature_opt_file = os.path.join(
            scenario_dir, building['geojson_id'], 'feature_reports', 'feature_optimization.json')
        if (os.path.exists(feature_opt_file)):
            with open(feature_opt_file, "r") as f:
                reopt_data = json.load(f)

        # extract Latitude
        latitude = reopt_data['location']['latitude_deg']

        # PV
        if reopt_data['distributed_generation'] and reopt_data['distributed_generation']['solar_pv']:
            building['photovoltaic_panels'] = self.process_pv(
                reopt_data['distributed_generation']['solar_pv'], latitude)

        return building

    def process_microgrid_inputs(self, scenario_dir: Path):
        """
        Processes microgrid inputs and adds them to param_template from csv_to_sys_param method
        :param scenario_dir: Path, location/name of folder with uo_sdk results
        """
        reopt_data = {}
        raw_data = {}
        # look for REopt scenario_optimization.json file in scenario dir (uo report)
        scenario_opt_file = os.path.join(scenario_dir, 'scenario_optimization.json')
        if (os.path.exists(scenario_opt_file)):
            with open(scenario_opt_file, "r") as f:
                reopt_data = json.load(f)
        # also look for raw REopt report with inputs and xzx for non-uo results
        raw_scenario_file = os.path.join(scenario_dir, 'reopt', 'scenario_report_reopt_scenario_reopt_run.json')
        if (os.path.exists(raw_scenario_file)):
            with open(raw_scenario_file, "r") as f:
                raw_data = json.load(f)

        # PV (add if results are found in scenario_report)
        # extract latitude
        latitude = reopt_data['scenario_report']['location']['latitude_deg']
        if reopt_data['scenario_report']['distributed_generation']['solar_pv']:
            self.param_template['photovoltaic_panels'] = self.process_pv(
                reopt_data['scenario_report']['distributed_generation']['solar_pv'],
                latitude
            )

        # Wind (add if results are found in scenario_report)
        if reopt_data['scenario_report']['distributed_generation']['wind']:
            self.process_wind(reopt_data)

        # CHP (add if results are found in reopt results-raw_data)
        # this is the only item not in the default URBANopt report file
        if raw_data['outputs']['Scenario']['Site']['CHP']['size_kw'] != 0.0:
            # there is a CHP, process
            self.process_chp(raw_data)

        # Battery Bank
        try:
            if reopt_data['scenario_report']['distributed_generation']['storage']:
                # there is storage, process
                self.process_storage(reopt_data)
        except KeyError:
            pass

        # Generators
        try:
            if reopt_data['scenario_report']['distributed_generation']['generators']:
                # process diesel generators
                self.process_generators(reopt_data)
        except KeyError:
            pass

        # process electrical components (from OpenDSS results)
        self.process_electrical_components(scenario_dir)

        # Power Converters
        # TODO: not handled in UO / OpenDSS

    def csv_to_sys_param(self,
                         model_type: str,
                         scenario_dir: Path,
                         feature_file: Path,
                         sys_param_filename: Path,
                         overwrite=True,
                         microgrid=False) -> None:
        """
        Create a system parameters file using output from URBANopt SDK

        :param model_type: str, model type to select which sys_param template to use
        :param scenario_dir: Path, location/name of folder with uo_sdk results
        :param feature_file: Path, location/name of uo_sdk input file
        :param sys_param_filename: Path, location/name of system parameter file to be created
        :param microgrid: Boolean, Optional. If set to true, also process microgrid fields
        :return None, file created and saved to user-specified location
        """
        self.sys_param_filename = sys_param_filename

        if model_type == 'time_series':
            # TODO: delineate between time_series and time_series_mft
            if microgrid:
                param_template_path = Path(__file__).parent / 'time_series_microgrid_template.json'
            else:
                param_template_path = Path(__file__).parent / 'time_series_template.json'
        elif model_type == 'spawn':
            # TODO: We should support spawn as well
            pass
        else:
            raise Exception(f"No template found. {model_type} is not a valid template")

        if not Path(scenario_dir).exists():
            raise Exception(f"Unable to find your scenario. The path you provided was: {scenario_dir}")

        if not Path(feature_file).exists():
            raise Exception(f"Unable to find your feature file. The path you provided was: {feature_file}")

        if Path(self.sys_param_filename).exists() and not overwrite:
            raise Exception(f"Output file already exists and overwrite is False: {self.sys_param_filename}")

        with open(param_template_path, "r") as f:
            self.param_template = json.load(f)

        measure_list = []

        # Grab building load filepaths from sdk output
        for thing in scenario_dir.iterdir():
            if thing.is_dir():
                for item in thing.iterdir():
                    if item.is_dir():
                        if str(item).endswith('_export_time_series_modelica'):
                            measure_list.append(Path(item) / "building_loads.csv")
                        elif str(item).endswith('_export_modelica_loads'):
                            measure_list.append(Path(item) / "modelica.mos")

        # Get each feature id from the SDK FeatureFile
        building_ids = []
        with open(feature_file) as json_file:
            sdk_input = json.load(json_file)
            weather_filename = sdk_input['project']['weather_filename']
            weather_path = self.sys_param_filename.parent / weather_filename
            for feature in sdk_input['features']:
                # KAF change: this should only gather features of type 'Building'
                if feature['properties']['type'] == 'Building':
                    building_ids.append(feature['properties']['id'])

        # Check if the weatherfile exists, if not, try to download
        if not weather_path.exists():
            self.download_weatherfile(weather_path.name, weather_path.parent)
        # Now check again if the file exists, error if not!
        if not weather_path.exists():
            raise SystemExit(f"Could not find or download weatherfile for {str(weather_path)}")

        # also download the MOS -- this is the file that will
        # be set in the sys param file, so make the weather_path object this one
        weather_path = weather_path.with_suffix('.mos')
        if not weather_path.exists():
            self.download_weatherfile(weather_path.name, weather_path.parent)
        # Now check again if the file exists, error if not!
        if not weather_path.exists():
            raise SystemExit(f"Could not find or download weatherfile for {str(weather_path)}")

        # Make sys_param template entries for each feature_id
        building_list = []
        for building in building_ids:
            feature_info = deepcopy(self.param_template['buildings']['custom'][0])
            feature_info['geojson_id'] = str(building)
            building_list.append(feature_info)

        # Grab the modelica file for the each Feature, and add it to the appropriate building dict
        district_nominal_mfrt = 0
        for building in building_list:
            building_nominal_mfrt = 0
            for measure_file_path in measure_list:
                # Grab the relevant 2 components of the path: feature name and measure folder name, items -3 & -2 respectively
                feature_name = Path(measure_file_path).parts[-3]
                measure_folder_name = Path(measure_file_path).parts[-2]
                if feature_name != building['geojson_id']:
                    continue
                if (measure_file_path.suffix == '.mos'):
                    building['load_model_parameters']['time_series']['filepath'] = str(measure_file_path.resolve())
                if (measure_file_path.suffix == '.csv') and ('_export_time_series_modelica' in str(measure_folder_name)):
                    mfrt_df = pd.read_csv(measure_file_path)
                    building_nominal_mfrt = mfrt_df['massFlowRateHeating'].max().round(3)
                    building['ets_model_parameters']['indirect']['nominal_mass_flow_building'] = float(
                        building_nominal_mfrt)
                district_nominal_mfrt += building_nominal_mfrt

        # Remove template buildings that weren't used or don't have successful simulations with modelica outputs
        # FIXME: Another place where we only support time series for now.
        building_list = [x for x in building_list if not x['load_model_parameters']
                         ['time_series']['filepath'].endswith("populated")]
        if len(building_list) == 0:
            raise SystemExit("No Modelica files found. Modelica files are expected to be found within each feature in folders "
                             "with names that include '_modelica'\n"
                             f"For instance: {scenario_dir / '2' / '016_export_modelica_loads'}\n"
                             "If these files don't exist the UO SDK simulations may not have been successful")

        # Update specific sys-param settings for each building
        for building in building_list:
            building['ets_model_parameters']['indirect']['nominal_mass_flow_district'] = float(
                district_nominal_mfrt.round(3))
            if microgrid:
                building = self.process_building_microgrid_inputs(building, scenario_dir)

        # Add all buildings to the sys-param file
        self.param_template['buildings']['custom'] = building_list

        # Update district sys-param settings
        # Parens are to allow the line break
        (self.param_template['district_system']['default']
            ['central_cooling_plant_parameters']['weather_filepath']) = str(weather_path)

        if microgrid:
            self.process_microgrid_inputs(scenario_dir)

        # save
        self.save()

    def save(self):
        """
        Write the system parameters file with param_template and save
        """
        with open(self.sys_param_filename, 'w') as outfile:
            json.dump(self.param_template, outfile, indent=2)
