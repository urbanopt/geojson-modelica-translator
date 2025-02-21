# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.external_package_utils import load_loop_order
from geojson_modelica_translator.model_connectors.networks.network_base import NetworkBase
from geojson_modelica_translator.utils import ModelicaPath

logger = logging.getLogger(__name__)


class DesignDataSeries(NetworkBase):
    model_name = "DesignDataSeries"

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = "datDes"
        self.design_data_name = "DesignDataSeries"

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        loop_order = load_loop_order(self.system_parameters.filename)

        template_data = {
            "number_of_loops": len(loop_order),
            "data": loop_order,
        }

        # create district data package paths
        b_modelica_path = ModelicaPath(self.design_data_name, scaffold.networks_path.files_dir, True)

        # load templates
        design_data_template = self.template_env.get_template("DesignDataSeries.mot")

        self.run_template(
            design_data_template,
            os.path.join(b_modelica_path.files_dir, "DesignDataSeries.mo"),
            project_name=scaffold.project_name,
            model_name=self.design_data_name,
            design_data=template_data,
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.networks_path.files_dir, within=f"{scaffold.project_name}.Networks"
        )

        # DesignDataSeries package
        subpackage_models = ["DesignDataSeries"]
        design_data_package = PackageParser.new_from_template(
            path=b_modelica_path.files_dir,
            name=self.design_data_name,
            order=subpackage_models,
            within=f"{scaffold.project_name}.Networks",
        )
        design_data_package.save()

        # Networks package
        package = PackageParser(scaffold.project_path)
        if "Networks" not in package.order:
            package.add_model("Networks")
            package.save()

        package_models = [self.design_data_name] + [Path(mo).stem for mo in self.required_mo_files]
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
                networks_package.add_model(model_name)
        networks_package.save()

    def get_modelica_type(self, scaffold):
        return f"Networks.{self.design_data_name}.DesignDataSeries"
