# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
import logging
import math
from copy import deepcopy
from pathlib import Path
from typing import Union

import pandas as pd
import requests
from jsonpath_ng.ext import parse
from jsonschema.validators import Draft202012Validator as LatestValidator

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
        {"json_path": "$.buildings[?load_model=spawn].load_model_parameters.spawn.idf_filename"},
        {"json_path": "$.buildings[?load_model=spawn].load_model_parameters.spawn.epw_filename"},
        {"json_path": "$.buildings[?load_model=spawn].load_model_parameters.spawn.mos_weather_filename"},
        {"json_path": "$.buildings[?load_model=rc].load_model_parameters.rc.mos_weather_filename"},
        {"json_path": "$.buildings[?load_model=time_series].load_model_parameters.time_series.filepath"},
        {"json_path": "$.buildings[?load_model=time_series_massflow_temperature].load_model_parameters.time_series.filepath"},
        {"json_path": "$.weather"},
        {"json_path": "$.combined_heat_and_power_systems.[*].performance_data_path"}
    ]

    def __init__(self, filename=None):
        """
        Read in the system design parameter file

        :param filename: string, (optional) path to file to load
        """
        # load the schema for validation
        schema = Path(__file__).parent / "schema.json"
        self.schema = json.loads(schema.read_text())
        self.param_template = {}
        self.filename = filename

        if self.filename:
            if Path(self.filename).is_file():
                with open(self.filename, "r") as f:
                    self.param_template = json.load(f)
            else:
                raise Exception(f"System design parameters file does not exist: {self.filename}")

            errors = self.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

            self.resolve_paths()

        self.sys_param_filename = None

    @classmethod
    def loadd(cls, d, validate_on_load=True):
        """
        Create a system parameters instance from a dictionary
        :param d: dict, system parameter data

        :return: object, SystemParameters
        """
        sp = cls()
        sp.param_template = d

        if validate_on_load:
            errors = sp.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

        return sp

    def resolve_paths(self):
        """Resolve the paths in the file to be absolute if they were defined as relative. This method uses
        the JSONPath (with ext) to find if the value exists in the self.param_template object. If so, it then uses
        the set_param which navigates the JSON tree to set the value as needed."""
        filepath = Path(self.filename).parent.resolve()

        for pe in self.PATH_ELEMENTS:
            matches = parse(pe["json_path"]).find(self.param_template)
            for index, match in enumerate(matches):
                # print(f"Index {index} to update match {match.path} | {match.value} | {match.context}")
                new_path = Path(filepath) / match.value
                parse(str(match.full_path)).update(self.param_template, new_path.as_posix())

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
        data = data or self.param_template
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

    def get_param_by_building_id(self, building_id, jsonpath):
        """
        return a parameter for a specific building_id. This is similar to get_param but allows the user
        to constrain the data based on the building id.

        :param building_id: string, id of the building to look up in the custom section of the system parameters
        :param jsonpath: string, jsonpath formatted string to return
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """

        for b in self.param_template.get("buildings", []):
            if b.get("geojson_id", None) == building_id:
                return self.get_param(jsonpath, data=b)
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
        for error in sorted(v.iter_errors(self.param_template), key=str):
            results.append(error.message)

        return results

    def download_weatherfile(self, filename, save_directory: str) -> Union[str, Path]:
        """Download the MOS or EPW weather file from energyplus.net

        This routine downloads the weather file, either an MOS or EPW, which is selected based
        on the file extension.

            filename, str: Name of weather file to download, e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos
            save_directory, str: Location where to save the downloaded content. The path must exist before downloading.
        """
        p_download = Path(filename)
        p_save = Path(save_directory)

        if not p_save.is_dir():
            print(f"Creating directory to save weather file, {str(p_save)}")
            p_save.mkdir(parents=True, exist_ok=True)

        # get country & state from weather file name
        try:
            weatherfile_location_info = p_download.parts[-1].split("_")
            weatherfile_country = weatherfile_location_info[0]
            weatherfile_state = weatherfile_location_info[1]
        except IndexError:
            raise Exception(
                "Malformed location, needs underscores of location (e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)"
            )

        # download file from energyplus website
        weatherfile_url = 'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/' \
            f'{weatherfile_country}/{weatherfile_state}/{p_download.stem}/{p_download.name}'
        outputname = p_save / p_download.name
        logger.debug(f"Downloading weather file from {weatherfile_url}")
        try:
            weatherfile_data = requests.get(weatherfile_url)
            if weatherfile_data.status_code == 200:
                with open(outputname, 'wb') as f:
                    f.write(weatherfile_data.content)
            else:
                raise Exception(f"Returned non 200 status code trying to download weather file: {weatherfile_data.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Could not download weather file: {weatherfile_url}"
                "\nAt this time we only support USA weather stations"
                f"\n{e}"
            )

        if not outputname.exists():
            raise Exception(f"Could not find or download weather file for {str(p_download)}")

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
        opendss_json_file = Path(scenario_dir) / 'scenario_report_opendss.json'
        if opendss_json_file.exists():
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
                t['nominal_capacity'] = item['power_distribution'].get('nominal_capacity', None)
                t['reactance_resistance_ratio'] = item['power_distribution'].get('reactance_resistance_ratio', None)
                t['tx_incoming_voltage'] = item['power_distribution'].get('tx_incoming_voltage', None)
                t['tx_outgoing_voltage'] = item['power_distribution'].get('tx_outgoing_voltage', None)

                # Validate transformer input voltage is same as substation output voltage
                if t['tx_incoming_voltage'] is not None and t['tx_incoming_voltage'] != self.param_template['substations']['RMS_voltage_low_side']:
                    raise ValueError(f"Transformer input voltage {t['tx_incoming_voltage']} does not "
                                     f"match substation output voltage {self.param_template['substations']['RMS_voltage_low_side']}")

                transformers.append(t)

            self.param_template['transformers'] = transformers

            # Loads (buildings from geojson file)
            # grab all the building loads
            data = [d for d in dss_data['feature_reports'] if d['feature_type'] == 'Building']

            # grab records to modify
            for bldg in self.param_template['buildings']:
                # find match in data
                match = [d for d in data if d['id'] == bldg['geojson_id']]
                if match:
                    # add data
                    bldg['load'] = {}
                    # print(f"Found match for {bldg['geojson_id']}: {match[0]['id']}")
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
        feature_opt_file = Path(
            scenario_dir) / building['geojson_id'] / 'feature_reports' / 'feature_optimization.json'
        if feature_opt_file.exists():
            with open(feature_opt_file, "r") as f:
                reopt_data = json.load(f)

        # extract Latitude
        try:
            latitude = reopt_data['location']['latitude_deg']
        except KeyError:
            logger.info(f"Latitude not found in {feature_opt_file}. Skipping PV.")
        except UnboundLocalError:
            logger.info(f"REopt data not found in {feature_opt_file}. Skipping PV.")

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
        scenario_opt_file = Path(scenario_dir) / 'scenario_optimization.json'
        if scenario_opt_file.exists():
            with open(scenario_opt_file, "r") as f:
                reopt_data = json.load(f)
        # also look for raw REopt report with inputs and xzx for non-uo results
        raw_scenario_file = Path(scenario_dir) / 'reopt' / f'scenario_report_{scenario_dir.name}_reopt_run.json'
        if raw_scenario_file.exists():
            with open(raw_scenario_file, "r") as f:
                raw_data = json.load(f)

        # PV (add if results are found in scenario_report)
        # extract latitude
        try:
            latitude = reopt_data['scenario_report']['location']['latitude_deg']
            if reopt_data['scenario_report']['distributed_generation']['solar_pv']:
                self.param_template['photovoltaic_panels'] = self.process_pv(
                    reopt_data['scenario_report']['distributed_generation']['solar_pv'],
                    latitude
                )
        except KeyError:
            logger.info("Latitude not found in scenario_report. Skipping PV.")

        # Wind (add if results are found in scenario_report)
        # if reopt_data['scenario_report']['distributed_generation']['wind']:
        try:
            self.process_wind(reopt_data)
        except KeyError:
            logger.info("Wind data not found in scenario_report. Skipping wind.")

        # CHP (add if results are found in reopt results-raw_data)
        # this is the only item not in the default URBANopt report file
        if Path(raw_scenario_file).exists() and raw_data['outputs']['Scenario']['Site']['CHP']['size_kw'] != 0.0:
            # there is a CHP, process
            self.process_chp(raw_data)

        # Battery Bank
        try:
            if reopt_data['scenario_report']['distributed_generation']['storage']:
                # there is storage, process
                self.process_storage(reopt_data)
        except KeyError:
            logger.info("Energy storage data not found in scenario_report. Skipping storage.")

        # Generators
        try:
            if reopt_data['scenario_report']['distributed_generation']['generators']:
                # process diesel generators
                self.process_generators(reopt_data)
        except KeyError:
            logger.info("Generator data not found in scenario_report. Skipping generator.")

        # process electrical components (from OpenDSS results)
        self.process_electrical_components(scenario_dir)

        # Power Converters
        # TODO: not handled in UO / OpenDSS

    def calculate_dimensions(self, area, perimeter):

        discriminant = perimeter ** 2 - 16 * area

        if discriminant < 0:
            raise ValueError("No valid rectangle dimensions exist for the given area and perimeter.")

        length = (perimeter + math.sqrt(discriminant)) / 4
        width = (perimeter - 2 * length) / 2

        return length, width

    def csv_to_sys_param(self,
                         model_type: str,
                         scenario_dir: Path,
                         feature_file: Path,
                         sys_param_filename: Path,
                         ghe=False,
                         overwrite=True,
                         microgrid=False,
                         **kwargs) -> None:
        """
        Create a system parameters file using output from URBANopt SDK

        :param model_type: str, model type to select which sys_param template to use
        :param scenario_dir: Path, location/name of folder with uo_sdk results
        :param feature_file: Path, location/name of uo_sdk input file
        :param sys_param_filename: Path, location/name of system parameter file to be created
        :param overwrite: Boolean, whether to overwrite existing sys-param file
        :param ghe: Boolean, flag to add Ground Heat Exchanger properties to System Parameter File
        :param microgrid: Boolean, Optional. If set to true, also process microgrid fields

        :kwargs (optional):
            - relative_path: Path, set the paths (time series files, weather file, etc) relate to `relative_path`
        :return None, file created and saved to user-specified location


        """
        self.sys_param_filename = sys_param_filename
        self.rel_path = kwargs.get('relative_path', None)

        if model_type == 'time_series':
            # TODO: delineate between time_series and time_series_massflow_rate
            if microgrid:
                param_template_path = Path(__file__).parent / 'time_series_microgrid_template.json'
            else:
                param_template_path = Path(__file__).parent / 'time_series_template.json'
        elif model_type == 'spawn':
            # TODO: We should support spawn as well
            raise SystemExit('Spawn models are not implemented at this time.')
        else:
            raise SystemExit(f"No template found. {model_type} is not a valid template")

        if not Path(scenario_dir).is_dir():
            raise SystemExit(f"Unable to find your scenario. The path you provided was: {scenario_dir}")

        if not Path(feature_file).is_file():
            raise SystemExit(f"Unable to find your feature file. The path you provided was: {feature_file}")

        if Path(self.sys_param_filename).is_file() and not overwrite:
            raise SystemExit(f"Output file already exists and overwrite is False: {self.sys_param_filename}")

        with open(param_template_path, "r") as f:
            self.param_template = json.load(f)

        measure_list = []

        # Grab building load filepaths from sdk output
        for thing in scenario_dir.iterdir():
            if thing.is_dir():
                for item in thing.iterdir():
                    if item.is_dir():
                        if str(item).endswith('_export_time_series_modelica'):
                            measure_list.append(Path(item) / "building_loads.csv")  # used for mfrt
                        elif str(item).endswith('_export_modelica_loads'):
                            measure_list.append(Path(item) / "modelica.mos")  # space heating/cooling & water heating
                            measure_list.append(Path(item) / "building_loads.csv")  # used for max electricity load

        # Get each building feature id from the SDK FeatureFile
        building_ids = []
        with open(feature_file) as json_file:
            sdk_input = json.load(json_file)
        weather_filename = sdk_input['project']['weather_filename']
        weather_path = self.sys_param_filename.parent / weather_filename
        for feature in sdk_input['features']:
            if feature['properties']['type'] == 'Building':
                building_ids.append(feature['properties']['id'])

        # Check if the EPW weatherfile exists, if not, try to download
        if not weather_path.exists():
            self.download_weatherfile(weather_path.name, weather_path.parent)

        # also download the MOS weatherfile -- this is the file that will be set in the sys param file
        mos_weather_path = weather_path.with_suffix('.mos')
        if not mos_weather_path.exists():
            self.download_weatherfile(mos_weather_path.name, mos_weather_path.parent)

        # Make sys_param template entries for each feature_id
        building_list = []
        for building in building_ids:
            feature_info = deepcopy(self.param_template['buildings'][0])
            feature_info['geojson_id'] = str(building)
            building_list.append(feature_info)

        # Grab the modelica file for the each Feature, and add it to the appropriate building dict
        district_nominal_massflow_rate = 0
        for building in building_list:
            building_nominal_massflow_rate = 0
            for measure_file_path in measure_list:
                # Grab the relevant 2 components of the path: feature name and measure folder name, items -3 & -2 respectively
                feature_name = Path(measure_file_path).parts[-3]
                measure_folder_name = Path(measure_file_path).parts[-2]
                if feature_name != building['geojson_id']:
                    continue
                if (measure_file_path.suffix == '.mos'):
                    # if there is a relative path, then set the path relative
                    to_file_path = measure_file_path.resolve()
                    if self.rel_path:
                        to_file_path = to_file_path.relative_to(self.rel_path)

                    building['load_model_parameters']['time_series']['filepath'] = str(to_file_path)
                if (measure_file_path.suffix == '.csv') and ('_export_time_series_modelica' in str(measure_folder_name)):
                    massflow_rate_df = pd.read_csv(measure_file_path)
                    try:
                        building_nominal_massflow_rate = round(massflow_rate_df['massFlowRateHeating'].max(), 3)  # round max to 3 decimal places
                        # Force casting to float even if building_nominal_massflow_rate == 0
                        # FIXME: This might be related to building_type == `lodging` for non-zero building percentages
                        building['ets_indirect_parameters']['nominal_mass_flow_building'] = float(building_nominal_massflow_rate)
                    except KeyError:
                        # If massFlowRateHeating is not in the export_time_series_modelica output, just skip this step.
                        # It probably won't be in the export for hpxml residential buildings, at least as of 2022-06-29
                        logger.info("mass-flow-rate heating is not present. It is not expected in residential buildings. Skipping.")
                        continue
                district_nominal_massflow_rate += building_nominal_massflow_rate
                if measure_file_path.suffix == '.csv' and measure_folder_name.endswith('_export_modelica_loads'):
                    try:
                        building_loads = pd.read_csv(measure_file_path, usecols=['ElectricityFacility'])  # only use the one column to make the df small
                    except ValueError:  # hack to handle the case where there is no ElectricityFacility column in the csv
                        continue
                    max_electricity_load = int(building_loads['ElectricityFacility'].max())
                    building['load_model_parameters']['time_series']['max_electrical_load'] = max_electricity_load

        # Remove template buildings that weren't used or don't have successful simulations with modelica outputs
        # TODO: Another place where we only support time series for now.
        building_list = [x for x in building_list if not x['load_model_parameters']
                         ['time_series']['filepath'].endswith("populated")]
        if len(building_list) == 0:
            raise SystemExit("No Modelica files found. Modelica files are expected to be found within each feature in folders "
                             "with names that include '_modelica'\n"
                             f"For instance: {scenario_dir / '2' / '016_export_modelica_loads'}\n"
                             "If these files don't exist the UO SDK simulations may not have been successful")

        # Update specific sys-param settings for each building
        for building in building_list:
            building['ets_indirect_parameters']['nominal_mass_flow_district'] = district_nominal_massflow_rate
            feature_opt_file = scenario_dir / building['geojson_id'] / 'feature_reports' / 'feature_optimization.json'
            if microgrid and not feature_opt_file.exists():
                logger.debug(f"No feature optimization file found for {building['geojson_id']}. Skipping REopt for this building")
            elif microgrid and feature_opt_file.exists():
                building = self.process_building_microgrid_inputs(building, scenario_dir)

        # Add all buildings to the sys-param file
        self.param_template['buildings'] = building_list

        # Update district sys-param settings
        # Parens are to allow the line break
        to_file_path = mos_weather_path
        if self.rel_path:
            to_file_path = to_file_path.relative_to(self.rel_path)
        self.param_template['weather'] = str(to_file_path)
        if microgrid and not feature_opt_file.exists():
            logger.warn("Microgrid requires OpenDSS and REopt feature optimization for full functionality.\n"
                        "Run opendss and reopt-feature post-processing in the UO SDK for a full-featured microgrid.")
        try:
            self.process_microgrid_inputs(scenario_dir)
        except UnboundLocalError:
            raise SystemExit(f"\nError: No scenario_optimization.json file found in {scenario_dir}\n"
                             "Perhaps you haven't run REopt post-processing step in the UO sdk?")

        # Update ground heat exchanger properties if true
        if ghe:
            ghe_ids = []
            # add properties from the feature file
            with open(feature_file) as json_file:
                sdk_input = json.load(json_file)
            for feature in sdk_input['features']:
                if feature['properties']['type'] == 'District System':
                    try:
                        district_system_type = feature['properties']['district_system_type']
                    except KeyError:
                        pass
                    if district_system_type == 'Ground Heat Exchanger':
                        length, width = self.calculate_dimensions(feature['properties']['footprint_area'], feature['properties']['footprint_perimeter'])
                        ghe_ids.append({'ghe_id': feature['properties']['id'],
                                        'length_of_ghe': length,
                                        'width_of_ghe': width})

            ghe_sys_param = self.param_template['district_system']['fifth_generation']['ghe_parameters']
            # Make sys_param template entries for GHE specific properties
            ghe_list = []
            for ghe in ghe_ids:
                # update GHE specific properties
                ghe_info = deepcopy(ghe_sys_param['ghe_specific_params'][0])
                # Update GHE ID
                ghe_info['ghe_id'] = str(ghe['ghe_id'])
                # Add ghe geometric properties
                ghe_info['ghe_geometric_params']['length_of_ghe'] = ghe['length_of_ghe']
                ghe_info['ghe_geometric_params']['width_of_ghe'] = ghe['width_of_ghe']
                ghe_list.append(ghe_info)

            # Add all GHE specific properties to sys-param file
            ghe_sys_param['ghe_specific_params'] = ghe_list

            # Update ghe_dir
            ghe_dir = scenario_dir / 'ghe_dir'
            ghe_sys_param['ghe_dir'] = str(ghe_dir)

            # remove fourth generation district system type
            del self.param_template['district_system']['fourth_generation']

        else:
            # remove fifth generation district system type if it exists in template and ghe is not true
            try:
                del self.param_template['district_system']['fifth_generation']
            except KeyError:
                pass

        # save the file to disk
        self.save()

    def save(self):
        """
        Write the system parameters file with param_template and save
        """
        with open(self.sys_param_filename, 'w') as outfile:
            json.dump(self.param_template, outfile, indent=2)
