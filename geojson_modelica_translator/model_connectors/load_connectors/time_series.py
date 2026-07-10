# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import re
import shutil

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.load_connectors.load_base import LoadBase
from geojson_modelica_translator.utils import ModelicaPath, convert_c_to_k


class TimeSeries(LoadBase):
    model_name = "TimeSeries"

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = f"TimeSerLoa_{self.building_name}"

    def _is_no_plant_fifth_generation(self):
        fifth_generation = self.system_parameters.get_param("$.district_system.fifth_generation")
        if not fifth_generation:
            return False

        return not fifth_generation.get("ghe_parameters") and not fifth_generation.get("heat_source_parameters")

    def _time_series_parameters(self):
        for building in self.system_parameters.param_template.get("buildings", []):
            if building.get("geojson_id") == self.building_id:
                return building.get("load_model_parameters", {}).get("time_series", {})

        return {}

    def _use_dry_cooling_coil(self, is_no_plant_fifth_generation):
        time_series_parameters = self._time_series_parameters()
        use_dry_cooling_coil = bool(time_series_parameters.get("use_dry_cooling_coil"))
        use_wet_cooling_coil = bool(time_series_parameters.get("use_wet_cooling_coil"))

        if use_dry_cooling_coil and use_wet_cooling_coil:
            raise ValueError("Only one of use_dry_cooling_coil or use_wet_cooling_coil can be true")

        if use_wet_cooling_coil:
            return False

        return use_dry_cooling_coil or is_no_plant_fifth_generation

    @staticmethod
    def _copy_mos_with_zero_start(source_file, target_file):
        with open(source_file) as source:
            lines = source.readlines()

        table_line_index = None
        data_line_index = None
        for index, line in enumerate(lines):
            stripped = line.strip()
            if table_line_index is None and stripped.startswith("double "):
                table_line_index = index
                continue
            if table_line_index is not None and stripped and not stripped.startswith("#"):
                data_line_index = index
                break

        if table_line_index is None or data_line_index is None:
            shutil.copy(source_file, target_file)
            return

        data_values = lines[data_line_index].strip().split(";")
        if len(data_values) < 2:
            shutil.copy(source_file, target_file)
            return

        try:
            first_time = float(data_values[0])
        except ValueError:
            shutil.copy(source_file, target_file)
            return

        if first_time <= 0:
            shutil.copy(source_file, target_file)
            return

        table_line = lines[table_line_index]
        match = re.match(r"(\s*double\s+\w+\()(\d+)(\s*,\s*\d+\).*)", table_line)
        if match:
            newline = "\n" if table_line.endswith("\n") else ""
            lines[table_line_index] = f"{match.group(1)}{int(match.group(2)) + 1}{match.group(3)}{newline}"
        lines.insert(data_line_index, ";".join(["0", *["0"] * (len(data_values) - 1)]) + "\n")

        with open(target_file, "w") as target:
            target.writelines(lines)

    def to_modelica(self, scaffold):
        """Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        time_series_building_template = self.template_env.get_template("TimeSeriesBuilding.mot")
        time_series_building_with_ets_template = self.template_env.get_template("TimeSeriesBuildingWithETS.mot")
        dry_cooling_terminal_template = self.template_env.get_template("FanCoil2PipeCoolingDry.mot")
        # These templates will be rendered in order for a 5G system. 4G system uses only the first.
        building_templates = {}
        building_templates["TimeSeriesBuilding"] = time_series_building_template
        building_templates["building"] = time_series_building_with_ets_template

        b_modelica_path = ModelicaPath(self.building_name, scaffold.loads_path.files_dir, True)

        dry_cooling_terminal_path = os.path.join(scaffold.loads_path.files_dir, "FanCoil2PipeCoolingDry.mo")
        if not os.path.exists(dry_cooling_terminal_path):
            self.run_template(
                template=dry_cooling_terminal_template,
                save_file_name=dry_cooling_terminal_path,
                project_name=scaffold.project_name,
            )
            scaffold.package.loads.add_model("FanCoil2PipeCoolingDry", create_subpackage=False)
            scaffold.package.loads.save()

        self.copy_required_mo_files(b_modelica_path.files_dir, within=f"{scaffold.project_name}.Loads")

        # Note that the system_parameters object when accessing filepaths will fully resolve the
        # location of the file.
        time_series_filename = self.system_parameters.get_param_by_id(
            self.building_id, "load_model_parameters.time_series.filepath"
        )

        if not os.path.exists(time_series_filename):
            raise Exception(
                f"Missing MOS file for time series: {time_series_filename}\n"
                "If providing a relative path, ensure it is relative to the system parameters file."
            )
        elif os.path.splitext(time_series_filename)[1].lower() == ".csv":
            raise Exception("The timeseries file is CSV format. This must be converted to an MOS file for use.")

        is_no_plant_fifth_generation = self._is_no_plant_fifth_generation()
        use_dry_cooling_coil = self._use_dry_cooling_coil(is_no_plant_fifth_generation)
        service_water_start_temp = 293.15
        if is_no_plant_fifth_generation:
            service_water_start_temp = convert_c_to_k(
                self.system_parameters.get_param("$.district_system.fifth_generation.soil.undisturbed_temp")
            )

        # construct the dict to pass into the template. Depending on the type of model, not all the parameters are
        # used. The `nominal_values` are only used when the time series is coupled to an ETS system.
        building_template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "use_dry_cooling_coil": use_dry_cooling_coil,
            "heat_cool_enable_threshold": 1e-2 if use_dry_cooling_coil else 1e-4,
            "service_water_start_temp": service_water_start_temp,
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
            "district_type": self.system_parameters.get_param("district_system"),
            "nominal_values": {
                "delta_temp_air_cooling": self.system_parameters.get_param_by_id(
                    self.building_id, "load_model_parameters.time_series.delta_temp_air_cooling"
                ),
                "delta_temp_air_heating": self.system_parameters.get_param_by_id(
                    self.building_id, "load_model_parameters.time_series.delta_temp_air_heating"
                ),
                "temp_setpoint_heating": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_setpoint_heating"
                    )
                ),
                "temp_setpoint_cooling": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_setpoint_cooling"
                    )
                ),
                "chw_supply_temp": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_chw_supply"
                    )
                ),
                "chw_return_temp": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_chw_return"
                    )
                ),
                "hhw_supply_temp": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_hw_supply"
                    )
                ),
                "hhw_return_temp": convert_c_to_k(
                    self.system_parameters.get_param_by_id(
                        self.building_id, "load_model_parameters.time_series.temp_hw_return"
                    )
                ),
                "max_electrical_load": self.system_parameters.get_param_by_id(
                    self.building_id, "load_model_parameters.time_series.max_electrical_load"
                ),
                # FIXME: pick up default value from schema if not specified in system_parameters,
                # FYI: Modelica insists on booleans being lowercase, so we need to explicitly set "true" and "false"
                "has_liquid_heating": "true"
                if self.system_parameters.get_param_by_id(
                    self.building_id,
                    "load_model_parameters.time_series.has_liquid_heating",
                )
                else "false",
                "has_liquid_cooling": "true"
                if self.system_parameters.get_param_by_id(
                    self.building_id,
                    "load_model_parameters.time_series.has_liquid_cooling",
                )
                else "false",
                "has_electric_heating": "true"
                if self.system_parameters.get_param_by_id(
                    self.building_id,
                    "load_model_parameters.time_series.has_electric_heating",
                )
                else "false",
                "has_electric_cooling": "true"
                if self.system_parameters.get_param_by_id(
                    self.building_id,
                    "load_model_parameters.time_series.has_electric_cooling",
                )
                else "false",
            },
        }

        # merge ets template values from load_base.py into the building nominal values
        # If there is no ets defined in sys-param file, use the building template data alone
        try:
            nominal_values = {**building_template_data["nominal_values"], **self.ets_template_data}
            combined_template_data = {**building_template_data, **nominal_values}
        except AttributeError:
            combined_template_data = building_template_data

        # copy over the resource files for this building
        # TODO: move some of this over to a validation step
        new_file = os.path.join(b_modelica_path.resources_dir, os.path.basename(time_series_filename))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        if is_no_plant_fifth_generation:
            self._copy_mos_with_zero_start(time_series_filename, new_file)
        else:
            shutil.copy(time_series_filename, new_file)

        # This if statement exists only because we can't use the 5G model to run a 4G building.
        if "fifth_generation" not in building_template_data["district_type"]:
            self.run_template(
                template=time_series_building_template,
                save_file_name=os.path.join(b_modelica_path.files_dir, "TimeSeriesBuilding.mo"),
                project_name=scaffold.project_name,
                model_name=self.building_name,
                data=combined_template_data,
            )
        else:
            for k, v in building_templates.items():
                self.run_template(
                    template=v,
                    save_file_name=os.path.join(b_modelica_path.files_dir, f"{k}.mo"),
                    project_name=scaffold.project_name,
                    model_name=self.building_name,
                    data=combined_template_data,
                )

        # run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """Cleanup the export of time series files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """
        # Create the building-specific package within Loads. Build the order from
        # actual model files so package.order stays in sync with generated files.
        b_modelica_path = os.path.join(scaffold.loads_path.files_dir, self.building_name)
        order_files = sorted(
            os.path.splitext(fname)[0]
            for fname in os.listdir(b_modelica_path)
            if fname.endswith(".mo") and fname != "package.mo"
        )
        new_package = PackageParser.new_from_template(
            b_modelica_path, self.building_name, order_files, within=f"{scaffold.project_name}.Loads"
        )
        new_package.save()

        # Add the building to the Loads package using scaffold's PackageParser
        scaffold.package.loads.add_model(self.building_name, create_subpackage=True)
        scaffold.package.loads.save()

    def get_modelica_type(self, scaffold):
        district_params = self.system_parameters.get_param("district_system")
        if "fifth_generation" not in district_params:
            return f"Loads.{self.building_name}.TimeSeriesBuilding"
        else:
            return f"Loads.{self.building_name}.building"
