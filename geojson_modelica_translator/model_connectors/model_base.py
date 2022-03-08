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

import logging
import shutil
from pathlib import Path

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions
from modelica_builder.model import Model

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


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
        self.system_parameters = system_parameters

        # initialize the templating framework (Jinja2)
        self.template_dir = template_dir
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=self.template_dir),
            undefined=StrictUndefined
        )
        self.template_env.filters.update(ALL_CUSTOM_FILTERS)

        self._template_instance = f'{self.model_name}_Instance.mopt'

        # store a list of the templated files to include when building the package
        self.template_files_to_include = []

        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files = []
        # extract data out of the urbanopt_building object and store into the base object

        # Read district-level system params. Used when templating ets mofiles, for instance in heating_indirect.py
        if system_parameters is not None:
            self.district_template_data = {
                "temp_setpoint_hhw": self.system_parameters.get_param(
                    "$.district_system.default.central_heating_plant_parameters.temp_setpoint_hhw"
                ),
                "temp_setpoint_chw": self.system_parameters.get_param(
                    "$.district_system.default.central_cooling_plant_parameters.temp_setpoint_chw"
                ),
            }

    def ft2_to_m2(self, area_in_ft2: float) -> float:
        """
        Converts square feet to square meters

        :param area_in_ft2: Area in square feet to be converted to square meters
        """
        return area_in_ft2 * 0.092936

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

    @property
    def instance_template_path(self):
        template = self.template_env.get_template(self._template_instance)
        return template.filename

    def render_instance(self, template_params):
        """Templates the *_Instance file for the model. The templated result will
        be inserted into the final District Energy System model in order to
        instantiate/define the model instance.

        :param template_params: dict, parameters for the template
        :returns: tuple (str, str), the templated result followed by the name of the file used for templating
        """
        try:
            template = self.template_env.get_template(self._template_instance)
        except exceptions.TemplateNotFound:
            raise Exception(f"Could not find mopt template '{self._template_instance}' in {self.template_dir}")

        # get template path relative to the package
        template_filename = Path(template.filename).as_posix()
        _, template_filename = template_filename.rsplit('geojson_modelica_translator', 1)

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
