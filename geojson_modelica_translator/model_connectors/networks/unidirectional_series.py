# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.networks.network_base import NetworkBase
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)


class UnidirectionalSeries(NetworkBase):
    model_name = "UnidirectionalSeries"

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "dis_" + simple_uuid()
        self.unidirectional_series_name = "UnidirectionalSeries_" + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, "Connection1PipePlugFlow_v.mo"))

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
            "number_of_segments": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.number_of_segments"
            ),
            "buried_depth": self.system_parameters.get_param(
                "$.district_system.fifth_generation.horizontal_piping_parameters.buried_depth"
            ),
        }

        # process pipe wall thickness
        if template_data["hydraulic_diameter"] and template_data["diameter_ratio"]:
            template_data["pipe_wall_thickness"] = template_data["hydraulic_diameter"] / (
                template_data["diameter_ratio"] - 2
            )
        else:
            template_data["pipe_wall_thickness"] = None

        # create distribution network package paths
        b_modelica_path = ModelicaPath(self.unidirectional_series_name, scaffold.networks_path.files_dir, True)

        # load templates
        distribution_template = self.template_env.get_template("UnidirectionalSeries.mot")

        self.run_template(
            distribution_template,
            os.path.join(b_modelica_path.files_dir, "UnidirectionalSeries.mo"),
            project_name=scaffold.project_name,
            model_name=self.unidirectional_series_name,
            distribution_data=template_data,
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.networks_path.files_dir, within=f"{scaffold.project_name}.Networks"
        )

        # UnidirectionalSeries_ package
        subpackage_models = ["UnidirectionalSeries"]
        distribution_package = PackageParser.new_from_template(
            path=b_modelica_path.files_dir,
            name=self.unidirectional_series_name,
            order=subpackage_models,
            within=f"{scaffold.project_name}.Networks",
        )
        distribution_package.save()

        # Networks package
        package = PackageParser(scaffold.project_path)
        if "Networks" not in package.order:
            package.add_model("Networks")
            package.save()

        package_models = [self.unidirectional_series_name] + [Path(mo).stem for mo in self.required_mo_files]
        networks_package = PackageParser(scaffold.networks_path.files_dir)
        if networks_package.order_data is None:
            networks_package = PackageParser.new_from_template(
                path=scaffold.networks_path.files_dir,
                name="Networks",
                order=package_models,
                within=scaffold.project_name,
            )
        else:
            for model_name in package_models:
                # We only want a single model named Connection1PipePlugFlow_v to be included, so we skip adding
                # (One was included when the Networks package order_data was first created just above)
                if model_name != "Connection1PipePlugFlow_v":
                    networks_package.add_model(model_name)
        networks_package.save()

    def get_modelica_type(self, scaffold):
        return f"Networks.{self.unidirectional_series_name}.UnidirectionalSeries"
