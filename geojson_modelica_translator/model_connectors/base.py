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

from jinja2 import Environment, FileSystemLoader


class Base(object):
    """
    Base class of the model connectors. The connectors can utilize various methods to create a building (or other
    feature) to a detailed Modelica connection. For example, a simple RC model (using TEASER), a ROM, CSV file, etc.
    """

    def __init__(self, system_parameters):
        """
        Base initializer

        :param system_parameters: SystemParameters object
        """
        self.buildings = []
        self.system_parameters = system_parameters

        # initialize the templating framework (Jinja2)
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.template_env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))

        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files = []
        # extract data out of the urbanopt_building object and store into the base object

    def copy_required_mo_files(self, dest_folder):
        """Copy any required_mo_files to the destination

        :param dest_folder: String, folder to copy the resulting MO files into.
        """
        result = []
        for f in self.required_mo_files:
            if not os.path.exists(f):
                raise Exception(f"Required MO file not found: {f}")

            result.append(shutil.copy(f, os.path.join(dest_folder, os.path.basename(f))))

        return result

    def run_template(self, template, save_file_name, **kwargs):
        """Create an instance from a jinja template"""
        file_data = template.render(**kwargs)

        os.makedirs(os.path.dirname(save_file_name), exist_ok=True)
        with open(save_file_name, "w") as f:
            f.write(file_data)

    # These methods need to be defined in each of the derived model connectors
    # def to_modelica(self):
