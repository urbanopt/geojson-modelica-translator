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

import os
import shutil

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath
from jinja2 import Environment, FileSystemLoader


class TimeSeriesConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.template_env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))
        self.required_mo_files = [
            os.path.join(self.template_dir, 'PartialBuilding.mo'),
        ]

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.

        :param urbanopt_building: an urbanopt_building
        """
        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality

        if mapper is None:
            number_stories = urbanopt_building.feature.properties["number_of_stories"]
            number_stories_above_ground = urbanopt_building.feature.properties["number_of_stories_above_ground"]
            self.buildings.append(
                {
                    "area": urbanopt_building.feature.properties["floor_area"] * 0.092936,  # ft2 -> m2
                    "building_id": urbanopt_building.feature.properties["id"],
                    "building_type": urbanopt_building.feature.properties["building_type"],
                    "floor_height": urbanopt_building.feature.properties["height"] * 0.3048,  # ft -> m
                    "num_stories": urbanopt_building.feature.properties["number_of_stories_above_ground"],
                    "num_stories_below_grade": number_stories - number_stories_above_ground,
                    "year_built": urbanopt_building.feature.properties["year_built"],
                }
            )

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        curdir = os.getcwd()

        time_series_coupling_template = self.template_env.get_template("time_series_coupling.mot")
        time_series_building_template = self.template_env.get_template("time_series_building.mot")
        time_series_mos_template = self.template_env.get_template("RuntimeSeriesBuilding.most")
        building_names = []
        try:
            for building in self.buildings:
                building_names.append(f"B{building['building_id']}")
                b_modelica_path = ModelicaPath(
                    f"B{building['building_id']}", scaffold.loads_path.files_dir, True
                )

                for f in self.required_mo_files:
                    shutil.copy(f, os.path.join(b_modelica_path.files_dir, os.path.basename(f)))

                # grab the data from the system_parameter file for this building id
                # TODO: create method in system_parameter class to make this easier and respect the defaults
                time_series_filename = self.system_parameters.get_param_by_building_id(
                    building["building_id"], "load_model_parameters.time_series.filepath"
                )

                # construct the dict to pass into the template
                template_data = {
                    "load_resources_path": b_modelica_path.resources_relative_dir,
                    "time_series": {
                        "filepath": time_series_filename,
                        "filename": os.path.basename(time_series_filename),
                        "path": os.path.dirname(time_series_filename),
                    }
                }

                # copy over the resource files for this building
                # TODO: move some of this over to a validation step
                if os.path.exists(template_data["time_series"]["filepath"]):
                    new_file = os.path.join(b_modelica_path.resources_dir, template_data["time_series"]["filename"])
                    os.makedirs(os.path.dirname(new_file), exist_ok=True)
                    shutil.copy(template_data["time_series"]["filepath"], new_file)
                else:
                    raise Exception(f"Missing MOS file for time series: {template_data['time_series']['filepath']}")

                self.run_template(
                    time_series_building_template,
                    os.path.join(b_modelica_path.files_dir, "building.mo"),
                    project_name=scaffold.project_name,
                    model_name=f"B{building['building_id']}",
                    data=template_data
                )

                self.run_template(
                    time_series_coupling_template,
                    os.path.join(b_modelica_path.files_dir, "coupling.mo"),
                    project_name=scaffold.project_name,
                    model_name=f"B{building['building_id']}",
                    data=template_data
                )

                self.run_template(
                    time_series_mos_template,
                    os.path.join(b_modelica_path.scripts_dir, "RuntimeSeriesBuilding.most"),
                    full_model_name=os.path.join(
                        scaffold.project_name,
                        scaffold.loads_path.files_relative_dir,
                        f"B{building['building_id']}",
                        "coupling").replace(os.path.sep, '.')
                )

        finally:
            os.chdir(curdir)

        # run post process to create the remaining project files for this building
        self.post_process(scaffold, building_names)

    def post_process(self, scaffold, building_names):
        """
        Cleanup the export of time series files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :return: None
        """
        for b in building_names:
            b_modelica_path = os.path.join(scaffold.loads_path.files_dir, b)
            new_package = PackageParser.new_from_template(
                b_modelica_path, b, ["PartialBuilding", "building", "coupling"],
                within=f"{scaffold.project_name}.Loads"
            )
            new_package.save()

        # now create the Loads level package. This (for now) will create the package without considering any existing
        # files in the Loads directory.
        package = PackageParser.new_from_template(
            scaffold.loads_path.files_dir, "Loads", building_names, within=f"{scaffold.project_name}"
        )
        package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Loads"]
        )
        pp.save()
