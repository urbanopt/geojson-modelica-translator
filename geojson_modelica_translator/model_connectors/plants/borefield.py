# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import math
import os
import re
from pathlib import Path

import pandas as pd
import scipy.io as sio
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)


class Borefield(PlantBase):
    model_name = "Borefield"

    def __init__(self, system_parameters, ghe=None):
        super().__init__(system_parameters)
        self.id = "borFie_" + simple_uuid()
        self.borefield_name = "Borefield_" + simple_uuid()
        self.ghe_id = ghe["ghe_id"]

        self.required_mo_files.append(os.path.join(self.template_dir, "GroundTemperatureResponse.mo"))

    def validate_undisturbed_soil_temperature(self, undisturbed_temp_value):
        # Validate undisturbed soil temperature - this is required field, but warn if different than lookup
        difference_threshold = 0.5  # degrees C

        # lookup by weather station name
        weather = self.system_parameters.get_param("$.weather")
        parts = weather.split("/")[-1].split("_")
        if len(parts) == 4:
            station_name = parts[2]
        elif len(parts) == 3:
            station_name = parts[1]
        else:
            logger.warning(
                "Unexpected weather file name format '%s'. Using last underscore-separated part as station name.",
                weather,
            )
            station_name = os.path.splitext(parts[-1])[0]
        station_name = re.sub(r"\d+", "", station_name).replace(".", " ")

        # lookup undisturbed soil temperature from csv based on station name
        weather_station_df = pd.read_csv(
            Path(__file__).parent.parent / "networks" / "data" / "Soil_temp_coefficients.csv"
        )

        # if weather file is not found, it won't actually get this far in the process
        # but just in case we can have this here
        matched_rows = weather_station_df[weather_station_df["Station"].str.contains(station_name, case=False)]
        matched_temp = None
        if not matched_rows.empty:
            matched_temp = float(matched_rows.iloc[0]["Ts,avg, C"])

        if matched_temp is not None:
            if abs(float(undisturbed_temp_value) - matched_temp) > difference_threshold:
                logger.warning(
                    f"Undisturbed soil temperature is set to "
                    f"{undisturbed_temp_value} °C in system parameters, which "
                    f"differs from the lookup value of {matched_temp} °C for weather station '{station_name}'. "
                    f"Consider updating the undisturbed soil temperature value in the system parameters file."
                )
        else:
            logger.warning(
                f"Could not validate undisturbed soil temperature in system parameters file against our weather "
                f"station lookup file. Undisturbed soil temperature is currently set to "
                f"{undisturbed_temp_value} °C."
            )

    def to_modelica(self, scaffold):
        """Convert the Borefield to Modelica code
        Create timeSeries models based on the data in the buildings and GeoJSONs

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        template_data = {
            "gfunction": {
                "input_path": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_dir"
                ),
                "ghe_id": self.ghe_id,
            },
            "soil": {
                "initial_ground_temperature": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.soil.undisturbed_temp"
                ),
                "conductivity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.soil.conductivity"
                ),
                "volumetric_heat_capacity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.soil.rho_cp"
                ),
            },
            "fill": {
                "conductivity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.grout.conductivity"
                ),
                "volumetric_heat_capacity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.grout.rho_cp"
                ),
            },
            "configuration": {
                "borehole_configuration": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.pipe.arrangement"
                ),
                "nominal_mass_flow_per_borehole": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.design.flow_rate"
                ),
                "flow_type": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.design.flow_type"
                ),
                "borehole_height": self.system_parameters.get_param_by_id(self.ghe_id, "$.*.borehole_length"),
                "borehole_diameter": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.borehole.diameter"
                ),
                "borehole_buried_depth": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.borehole.buried_depth"
                ),
                "number_of_boreholes": self.system_parameters.get_param_by_id(
                    # The borefield could be one of several types, so we have to use the wildcard to get in.
                    self.ghe_id,
                    "$.*.number_of_boreholes",
                ),
            },
            "tube": {
                "outer_diameter": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.pipe.outer_diameter"
                ),
                "inner_diameter": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.pipe.inner_diameter"
                ),
                "conductivity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.pipe.conductivity"
                ),
                "shank_spacing": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.pipe.shank_spacing"
                ),
            },
        }

        if template_data["configuration"]["number_of_boreholes"] is None:
            template_data["configuration"]["number_of_boreholes"] = len(
                self.system_parameters.get_param_by_id(self.ghe_id, "$.pre_designed_borefield.borehole_x_coordinates")
            )

        # Validate undisturbed soil temperature (validates and warns - does not change values)
        self.validate_undisturbed_soil_temperature(template_data["soil"]["initial_ground_temperature"])

        # process g-function file
        if Path(template_data["gfunction"]["input_path"]).expanduser().is_absolute():
            gfunction = pd.read_csv(
                Path(template_data["gfunction"]["input_path"]) / template_data["gfunction"]["ghe_id"] / "Gfunction.csv",
                header=0,
                usecols=[0, 2],
            )
        else:
            sys_param_dir = Path(self.system_parameters.filename).parent.resolve()
            try:
                gfunction = pd.read_csv(
                    sys_param_dir
                    / template_data["gfunction"]["input_path"]
                    / template_data["gfunction"]["ghe_id"]
                    / "Gfunction.csv",
                    header=0,
                    usecols=[0, 2],
                )
            except FileNotFoundError:
                raise SystemExit(
                    f"Can't find g-function file for ghe with ID: {template_data['gfunction']['ghe_id']}.\n"
                    "If using a relative path to your ghe_dir, your path "
                    f" '{template_data['gfunction']['input_path']}' must be relative to the dir your "
                    "sys-param file is in."
                )
        template_data["gfunction"]["gfunction_file_rows"] = gfunction.shape[0] + 1

        # convert the values to match Modelica gfunctions
        for i in range(len(gfunction)):
            gfunction.loc[i, gfunction.columns[0]] = (
                math.exp(gfunction.loc[i, gfunction.columns[0]])
                * template_data["configuration"]["borehole_height"] ** 2
                / (9 * template_data["soil"]["conductivity"] / template_data["soil"]["volumetric_heat_capacity"])
            )
            gfunction.loc[i, gfunction.columns[1]] = gfunction.loc[i, gfunction.columns[1]] / (
                template_data["configuration"]["number_of_boreholes"]
                * 2
                * math.pi
                * template_data["configuration"]["borehole_height"]
                * template_data["soil"]["conductivity"]
            )

        # add zeros to the first row
        new_row = pd.Series({gfunction.columns[0]: 0, gfunction.columns[1]: 0})
        gfunction = pd.concat([gfunction.iloc[:0], pd.DataFrame([new_row]), gfunction.iloc[0:]]).reset_index(drop=True)

        # create borefield package paths
        b_modelica_path = ModelicaPath(self.borefield_name, scaffold.plants_path.files_dir, True)

        # add to dict and save MAT file to the borefield's resources folder
        data_dict = {"TStep": gfunction.to_numpy()}
        gfunction_path = os.path.join(b_modelica_path.resources_dir, "Gfunction.mat")
        sio.savemat(gfunction_path, data_dict)
        template_data["gfunction"]["gfunction_file_path"] = b_modelica_path.resources_relative_dir + "/Gfunction.mat"

        # process nominal mass flow rate
        if template_data["configuration"]["flow_type"] == "system":
            template_data["configuration"]["nominal_mass_flow_per_borehole"] = (
                template_data["configuration"]["nominal_mass_flow_per_borehole"]
                / template_data["configuration"]["number_of_boreholes"]
            )

        # process tube thickness
        if template_data["tube"]["outer_diameter"] and template_data["tube"]["inner_diameter"]:
            template_data["tube"]["thickness"] = (
                template_data["tube"]["outer_diameter"] - template_data["tube"]["inner_diameter"]
            ) / 2
        else:
            template_data["tube"]["thickness"] = None

        # process shank spacing
        if template_data["tube"]["shank_spacing"] and template_data["tube"]["outer_diameter"]:
            template_data["tube"]["shank_spacing"] = (
                template_data["tube"]["shank_spacing"] + template_data["tube"]["outer_diameter"]
            ) / 2
        else:
            template_data["tube"]["shank_spacing"] = None

        # load templates
        oneutube_template = self.template_env.get_template("BorefieldOneUTube.mot")
        twoutube_template = self.template_env.get_template("BorefieldTwoUTubes.mot")

        if template_data["configuration"]["borehole_configuration"] == "singleutube":
            plant_template = oneutube_template
            template_data["configuration"]["borehole_configuration"] = (
                "Buildings.Fluid.Geothermal.Borefields.Types.BoreholeConfiguration.SingleUTube"
            )
            template_data["configuration"]["borehole_type"] = (
                "Buildings.Fluid.Geothermal.Borefields.BaseClasses.Boreholes.OneUTube"
            )
        elif template_data["configuration"]["borehole_configuration"] == "doubleutube":
            plant_template = twoutube_template
            template_data["configuration"]["borehole_configuration"] = (
                "Buildings.Fluid.Geothermal.Borefields.Types.BoreholeConfiguration.DoubleUTubeSeries"
            )
            template_data["configuration"]["borehole_type"] = (
                "Buildings.Fluid.Geothermal.Borefields.BaseClasses.Boreholes.TwoUTube"
            )
        else:
            raise ValueError("The type of geothermal heat exchanger pipe arrangement is not supported.")

        self.run_template(
            plant_template,
            os.path.join(b_modelica_path.files_dir, "Borefield.mo"),
            project_name=scaffold.project_name,
            model_name=self.borefield_name,
            ghe_data=template_data,
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir, within=f"{scaffold.project_name}.Plants"
        )

        # Borefield_ package
        subpackage_models = ["Borefield"]
        borefield_package = PackageParser.new_from_template(
            path=b_modelica_path.files_dir,
            name=self.borefield_name,
            order=subpackage_models,
            within=f"{scaffold.project_name}.Plants",
        )
        borefield_package.save()

        # Add models to Plants package using scaffold's PackageParser
        package_models = [self.borefield_name] + [Path(mo).stem for mo in self.required_mo_files]
        for model_name in package_models:
            # We only want a single model named GroundTemperatureResponse to be included, so we skip adding
            if (
                model_name == "GroundTemperatureResponse"
                and "GroundTemperatureResponse" in scaffold.package.plants.order
            ):
                continue
            scaffold.package.plants.add_model(model_name, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return f"Plants.{self.borefield_name}.Borefield"
