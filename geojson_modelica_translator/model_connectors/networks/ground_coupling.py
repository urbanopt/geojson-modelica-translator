# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import re
from pathlib import Path

import pandas as pd
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.networks.network_base import NetworkBase
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)


class GroundCoupling(NetworkBase):
    model_name = "GroundCoupling"

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "groCou_" + simple_uuid()
        self.ground_coupling_name = "GroundCoupling_" + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, "UndisturbedSoilTemperature.mo"))

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        template_data = {
            "hydraulic_diameter": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.hydraulic_diameter"
            ),
            "insulation_thickness": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.insulation_thickness"
            ),
            "insulation_conductivity": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.insulation_conductivity"
            ),
            "diameter_ratio": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.diameter_ratio"
            ),
            "roughness": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.roughness"
            ),
            "rho_cp": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.rho_cp"
            ),
            "buried_depth": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.buried_depth"
            ),
            "weather": self.system_parameters.get_param("$.weather"),
            "num_buildings": self.num_buildings,
            "loop_order": {
                "number_of_loops": len(self.loop_order),
                "data": self.loop_order,
            },
        }

        # process pipe wall thickness
        if template_data["hydraulic_diameter"] and template_data["diameter_ratio"]:
            template_data["pipe_wall_thickness"] = template_data["hydraulic_diameter"] / (
                template_data["diameter_ratio"] - 2
            )
        else:
            template_data["pipe_wall_thickness"] = None

        # get weather station name from weather file
        parts = template_data["weather"].split("/")[-1].split("_")
        if len(parts) == 4:
            station_name = parts[2]
        elif len(parts) == 3:
            station_name = parts[1]
        station_name = re.sub(r"\d+", "", station_name).replace(".", " ")

        # search for coefficients for calculating soil temperature based on station
        coefs = pd.read_csv(Path(__file__).parent / "data" / "Soil_temp_coefficients.csv")
        matching_rows = coefs[coefs.apply(lambda row: row.astype(str).str.contains(station_name).any(), axis=1)]
        if len(matching_rows) == 0:
            # Some of the stations in the coefs df are in all caps, so try that as well.
            # Also try to match only the first word of the station name.
            station_name = station_name.split()[0]
            matching_rows = coefs[
                coefs.apply(lambda row: row.astype(str).str.contains(station_name.upper()).any(), axis=1)
            ]
            # If still no match, raise an error
            if len(matching_rows) == 0:
                raise ValueError(
                    "No matching weather station has been found. Please check your weather file name format."
                    "(e.g., USA_NY_Buffalo-Greater.Buffalo.Intl.AP.725280_TMY3.mos)"
                )
        template_data["surface_temp"] = matching_rows["Ts,avg, C"].iloc[0] + 273.15
        template_data["first_amplitude"] = matching_rows["Ts,amplitude,1, C"].iloc[0]
        template_data["second_amplitude"] = matching_rows["Ts,amplitude,2, C"].iloc[0]
        template_data["first_phase_lag"] = matching_rows["PL1"].iloc[0]
        template_data["second_phase_lag"] = matching_rows["PL2"].iloc[0]

        # create horizontal piping package paths
        b_modelica_path = ModelicaPath(self.ground_coupling_name, scaffold.networks_path.files_dir, True)

        # load templates
        coupling_template = self.template_env.get_template("GroundCoupling.mot")

        self.run_template(
            coupling_template,
            os.path.join(b_modelica_path.files_dir, "GroundCoupling.mo"),
            project_name=scaffold.project_name,
            model_name=self.ground_coupling_name,
            piping_data=template_data,
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.networks_path.files_dir, within=f"{scaffold.project_name}.Networks"
        )

        # GroundCoupling_ package
        subpackage_models = ["GroundCoupling"]
        ground_coupling_package = PackageParser.new_from_template(
            path=b_modelica_path.files_dir,
            name=self.ground_coupling_name,
            order=subpackage_models,
            within=f"{scaffold.project_name}.Networks",
        )
        ground_coupling_package.save()

        # Add models to Networks package using scaffold's PackageParser
        package_models = [self.ground_coupling_name] + [Path(mo).stem for mo in self.required_mo_files]
        for model_name in package_models:
            scaffold.package.networks.add_model(model_name, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return f"Networks.{self.ground_coupling_name}.GroundCoupling"
