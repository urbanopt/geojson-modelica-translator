# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import math
import os
from pathlib import Path

import pandas as pd
import scipy.io as sio
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class Borefield(PlantBase):
    model_name = 'Borefield'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'borFie_' + simple_uuid()
        self.borefield_name = 'Borefield_' + simple_uuid()

        self.required_mo_files.append(os.path.join(self.template_dir, 'GroundTemperatureResponse.mo'))

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        template_data = {
            "gfunction": {
                "input_path": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_dir"
                ),
                "ghe_id": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params[0].ghe_id"
                )
            },
            "soil": {
                "initial_ground_temperature": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.soil.undisturbed_temp"
                ),
                "conductivity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.soil.conductivity"
                ),
                "volumetric_heat_capacity": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.soil.rho_cp"
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
                "borehole_height": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params[0].borehole.length_of_boreholes"
                ),
                "borehole_diameter": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params[0].borehole.diameter"
                ),
                "borehole_buried_depth": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params[0].borehole.buried_depth"
                ),
                "number_of_boreholes": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params[0].borehole.number_of_boreholes"
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

        # process g-function file
        if Path(template_data["gfunction"]["input_path"]).expanduser().is_absolute():
            gfunction = pd.read_csv(Path(template_data["gfunction"]["input_path"]) / template_data["gfunction"]["ghe_id"] / "Gfunction.csv", header=0, usecols=[0, 2])
        else:
            sys_param_dir = Path(self.system_parameters.filename).parent.resolve()
            try:
                gfunction = pd.read_csv(sys_param_dir / template_data["gfunction"]["input_path"] / template_data["gfunction"]["ghe_id"] / "Gfunction.csv", header=0, usecols=[0, 2])
            except FileNotFoundError:
                raise SystemExit(f'When using a relative path to your ghe_dir, your path \'{template_data["gfunction"]["input_path"]}\' must be relative to the dir your sys-param file is in.')
        template_data["gfunction"]["gfunction_file_rows"] = gfunction.shape[0] + 1

        # convert the values to match Modelica gfunctions
        for i in range(len(gfunction)):
            gfunction[gfunction.columns[0]].iloc[i] = math.exp(gfunction[gfunction.columns[0]].iloc[i]) * template_data["configuration"]["borehole_height"]**2 / (9 * template_data["soil"]["conductivity"] / template_data["soil"]["volumetric_heat_capacity"])
            gfunction[gfunction.columns[1]].iloc[i] = gfunction[gfunction.columns[1]].iloc[i] / (template_data["configuration"]["number_of_boreholes"] * 2 * math.pi * template_data["configuration"]["borehole_height"] * template_data["soil"]["conductivity"])

        # add zeros to the first row
        new_row = pd.Series({gfunction.columns[0]: 0, gfunction.columns[1]: 0})
        gfunction = pd.concat([gfunction.iloc[:0], pd.DataFrame([new_row]), gfunction.iloc[0:]]).reset_index(drop=True)

        # create borefield package paths
        b_modelica_path = ModelicaPath(self.borefield_name, scaffold.plants_path.files_dir, True)

        # add to dict and save MAT file to the borefield's resources folder
        data_dict = {'TStep': gfunction.values}
        gfunction_path = os.path.join(b_modelica_path.resources_dir, 'Gfunction.mat')
        sio.savemat(gfunction_path, data_dict)
        template_data["gfunction"]["gfunction_file_path"] = b_modelica_path.resources_relative_dir + "/Gfunction.mat"

        # process nominal mass flow rate
        if template_data["configuration"]["flow_type"] == "system":
            template_data["configuration"]["nominal_mass_flow_per_borehole"] = template_data["configuration"]["nominal_mass_flow_per_borehole"] / template_data["configuration"]["number_of_boreholes"]

        # process tube thickness
        if template_data["tube"]["outer_diameter"] and template_data["tube"]["inner_diameter"]:
            template_data["tube"]["thickness"] = (template_data["tube"]["outer_diameter"] - template_data["tube"]["inner_diameter"]) / 2
        else:
            template_data["tube"]["thickness"] = None

        # process shank spacing
        if template_data["tube"]["shank_spacing"] and template_data["tube"]["outer_diameter"]:
            template_data["tube"]["shank_spacing"] = (template_data["tube"]["shank_spacing"] + template_data["tube"]["outer_diameter"]) / 2
        else:
            template_data["tube"]["shank_spacing"] = None

        # load templates
        oneutube_template = self.template_env.get_template("BorefieldOneUTube.mot")
        twoutube_template = self.template_env.get_template("BorefieldTwoUTubes.mot")

        if template_data["configuration"]["borehole_configuration"] == "singleutube":
            plant_template = oneutube_template
            template_data["configuration"]["borehole_configuration"] = "Buildings.Fluid.Geothermal.Borefields.Types.BoreholeConfiguration.SingleUTube"
            template_data["configuration"]["borehole_type"] = "Buildings.Fluid.Geothermal.Borefields.BaseClasses.Boreholes.OneUTube"
        elif template_data["configuration"]["borehole_configuration"] == "doubleutube":
            plant_template = twoutube_template
            template_data["configuration"]["borehole_configuration"] = "Buildings.Fluid.Geothermal.Borefields.Types.BoreholeConfiguration.DoubleUTubeSeries"
            template_data["configuration"]["borehole_type"] = "Buildings.Fluid.Geothermal.Borefields.BaseClasses.Boreholes.TwoUTube"
        else:
            raise ValueError("The type of geothermal heat exchanger pipe arrangement is not supported.")

        self.run_template(
            plant_template,
            os.path.join(b_modelica_path.files_dir, "Borefield.mo"),
            project_name=scaffold.project_name,
            model_name=self.borefield_name,
            ghe_data=template_data
        )

        # generate Modelica package
        self.copy_required_mo_files(
            dest_folder=scaffold.plants_path.files_dir,
            within=f'{scaffold.project_name}.Plants')

        # Borefield_ package
        subpackage_models = ['Borefield']
        borefield_package = PackageParser.new_from_template(
            path=b_modelica_path.files_dir,
            name=self.borefield_name,
            order=subpackage_models,
            within=f"{scaffold.project_name}.Plants"
        )
        borefield_package.save()

        # Plants package
        package = PackageParser(scaffold.project_path)
        if 'Plants' not in package.order:
            package.add_model('Plants')
            package.save()

        package_models = [self.borefield_name] + [Path(mo).stem for mo in self.required_mo_files]
        plants_package = PackageParser(scaffold.plants_path.files_dir)
        if plants_package.order_data is None:
            plants_package = PackageParser.new_from_template(
                path=scaffold.plants_path.files_dir,
                name="Plants",
                order=package_models,
                within=scaffold.project_name)
        else:
            for model_name in package_models:
                plants_package.add_model(model_name)
        plants_package.save()

    def get_modelica_type(self, scaffold):
        return f'Plants.{self.borefield_name}.Borefield'
