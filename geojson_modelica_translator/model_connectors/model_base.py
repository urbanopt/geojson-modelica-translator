"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import shutil
from pathlib import Path

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions
from modelica_builder.model import Model


class ModelBase(object):
    """
    Base class of the model connectors. The connectors can utilize various methods to create a building (or other
    feature) to a detailed Modelica connection. For example, a simple RC model (using TEASER), a ROM, CSV file, etc.
    """
    # model_name must be overridden in subclass
    model_name = None

    def __init__(self, system_parameters, template_dir):
        """
        Base initializer

        :param system_parameters: SystemParameters object
        """
        self.buildings = []
        self.system_parameters = system_parameters

        # initialize the templating framework (Jinja2)
        self.template_dir = template_dir
        self.template_env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))
        self.template_env.filters.update(ALL_CUSTOM_FILTERS)

        # store a list of the templated files to include when building the package
        self.template_files_to_include = []

        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files = []
        # extract data out of the urbanopt_building object and store into the base object

    def ft2_to_m2(self, area_in_ft2: float) -> float:
        """
        Converts square feet to square meters

        :param area_in_ft2: Area in square feet to be converted to square meters
        """
        return area_in_ft2 * 0.092936

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.

        :param urbanopt_building: an urbanopt_building
        """

        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            try:
                building_id = urbanopt_building.feature.properties["id"]
                building_type = urbanopt_building.feature.properties["building_type"]
                number_stories = urbanopt_building.feature.properties["number_of_stories"]
                building_floor_area_m2 = self.ft2_to_m2(urbanopt_building.feature.properties["floor_area"])
            except KeyError as ke:
                raise SystemExit(f'\nMissing property {ke} in geojson feature file')

            try:
                number_stories_above_ground = urbanopt_building.feature.properties["number_of_stories_above_ground"]
            except KeyError:
                number_stories_above_ground = number_stories
                print(f"\nAssuming all building levels are above ground for building_id: {building_id}")

            try:
                floor_height = urbanopt_building.feature.properties["floor_height"]
            except KeyError:
                floor_height = 3  # Default height in meters from sdk
                print(f"\nNo floor_height found in geojson feature file for building {building_id}. Using default value of {floor_height}")

            # UO SDK defaults to current year, however TEASER only supports up to Year 2015
            # https://github.com/urbanopt/TEASER/blob/master/teaser/data/input/inputdata/TypeBuildingElements.json#L818
            try:
                year_built = urbanopt_building.feature.properties["year_built"]
                if urbanopt_building.feature.properties["year_built"] > 2015:
                    year_built = 2015
            except KeyError:
                year_built = 2015
                print(f"No 'year_built' found in geojson feature file for building {building_id}. Using default value of {year_built}")

            self.buildings.append(
                {
                    "area": building_floor_area_m2,
                    "building_id": building_id,
                    "building_type": building_type,
                    "floor_height": floor_height,
                    "num_stories": number_stories,
                    "num_stories_below_grade": number_stories - number_stories_above_ground,
                    "year_built": year_built,
                }
            )

    def copy_required_mo_files(self, dest_folder, within=None):
        """Copy any required_mo_files to the destination and update the within clause if defined. The required mo
        files need to be added as full paths to the required_mo_files member variable in the connectors derived
        classes.

        :param dest_folder: String, folder to copy the resulting MO files into.
        :param within: String, within clause to be replaced in the .mo file. Note that the original MO file needs to
        have a within clause defined to be replaced.
        """
        result = []
        for f in self.required_mo_files:
            if not Path(f).exists():
                raise Exception(f"Required MO file not found: {f}")

            new_filename = Path(dest_folder) / Path(f).name
            if within:
                mofile = Model(f)
                mofile.set_within_statement(within)
                mofile.save_as(new_filename)
                result.append(Path(dest_folder) / Path(f).name)
            else:
                # simply copy the file over if no need to update within
                result.append(shutil.copy(f, new_filename))

        return result

    def run_template(self, template, save_file_name, do_not_add_to_list=False, **kwargs):
        """
        Helper method to create the file from Jinja2's templating framework.

        :param template: object, Jinja template from the `template_env.get_template()` command.
        :param save_file_name: string, fully qualified path to save the rendered template to.
        :param do_not_add_to_list: boolean, set to true if you do not want the file to be added to the package.order
        :param kwargs: These are the arguments that need to be passed to the template.

        :return: None
        """
        file_data = template.render(**kwargs)

        Path(save_file_name).parent.mkdir(parents=True, exist_ok=True)
        with open(save_file_name, "w") as f:
            f.write(file_data)

        # add to the list of files to include in the package
        if not do_not_add_to_list:
            self.template_files_to_include.append(Path(save_file_name).stem)

    def modelica_path(self, filename):
        """Write a modelica path string for a given filename"""
        p = Path(filename)
        if p.suffix == ".idf":
            # TODO: This sucks. Not sucking would be good.
            # FIXME: String is hideous, but without stringifying it Pathlib thinks double slashes are "spurious"
            # https://docs.python.org/3/library/pathlib.html#pathlib.PurePath
            outputname = "modelica://" + str(Path("Buildings") / "Resources" / "Data"
                                             / "ThermalZones" / "EnergyPlus" / "Validation" / "RefBldgSmallOffice"
                                             / p.name)
        elif p.suffix == ".epw" or p.suffix == ".mos":
            outputname = "modelica://" + str(Path("Buildings") / "Resources" / "weatherdata" / p.name)
        return outputname

    def render_instance(self, template_params):
        """Templates the *_Instance file for the model. The templated result will
        be inserted into the final District Energy System model in order to
        instantiate/define the model instance.

        :param template_params: dict, parameters for the template
        :returns: tuple (str, str), the templated result followed by the name of the file used for templating
        """
        # TODO: both to_modelica and render_instance should use the same template environment
        # This should be fixed once all of the template files have the same variable substitution delimiters
        # TODO: move templates into specific model directories and have subclass override template_dir and template_env
        # This should be done once both to_modelica and render_instance can use the same environment
        template_env = Environment(
            loader=FileSystemLoader(searchpath=self.template_dir),
            undefined=StrictUndefined)
        template_env.filters.update(ALL_CUSTOM_FILTERS)
        template_name = f'{self.model_name}_Instance.mopt'
        try:
            template = template_env.get_template(template_name)
        except exceptions.TemplateNotFound:
            raise Exception(f"Could not find mopt template '{template_name}' in {self.template_dir}")

        # get template path relative to the package
        template_filename = template.filename
        _, template_filename = template_filename.rsplit('geojson_modelica_translator/', 1)

        return template.render(template_params), template_filename

    def to_dict(self, scaffold):
        return {
            'id': self.id,
            'modelica_type': self.get_modelica_type(scaffold)
        }

    # TODO: this should be implemented here, not in individual classes
    # def get_modelica_type(self, scaffold)

    # These methods need to be defined in each of the derived model connectors
    # def to_modelica(self):
