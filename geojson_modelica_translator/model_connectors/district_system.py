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
from jinja2 import Environment, FileSystemLoader

# from modelica_builder.model import Model


class DistrictSystemConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.template_env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))
        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files = [
            os.path.join(self.template_dir, 'ChilledWaterPumpSpeed.mo'),
            os.path.join(self.template_dir, 'DesignDataParallel4GDC.mo'),
            os.path.join(self.template_dir, 'CoolingTowerParellel.mo'),
            os.path.join(self.template_dir, 'CoolingTowerWithBypass.mo'),
            os.path.join(self.template_dir, 'CentralCoolingPlant.mo'),
            os.path.join(self.template_dir, 'PartialBuilding.mo'),
            os.path.join(self.template_dir, 'PartialBuildingWithCoolingIndirectETS.mo'),
            os.path.join(self.template_dir, 'BuildingSpawnZ6WithCoolingIndirectETS.mo'),
            os.path.join(self.template_dir, 'UnidirectionalParallel.mo'),
            os.path.join(self.template_dir, 'ConnectionParallel.mo'),
            os.path.join(self.template_dir, 'PartialDistribution2Pipe.mo'),
            os.path.join(self.template_dir, 'PipeDistribution.mo'),
        ]

    def to_modelica(self, scaffold):
        """
        # TODO: Need to pass in list of buildings to connect to network.

        Create district system models based on the data in the geojson and system parameter file.

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        curdir = os.getcwd()

        try:
            # Convert this to DistrictCoolingSystem.mot
            district_cooling_system_template = self.template_env.get_template("DistrictCoolingSystem.mo")

            template_data = {
                "hold": self.system_parameters.get_param("todo")
            }
            self.run_template(
                district_cooling_system_template,
                os.path.join(scaffold.districts_path.files_dir, "DistrictCoolingSystem.mo"),
                project_name=scaffold.project_name,
                model_name="SOMEMODELNAME",
                data=template_data
            )

            for f in self.required_mo_files:
                new_filename = os.path.join(scaffold.districts_path.files_dir, os.path.basename(f))
                shutil.copy(f, new_filename)

                # # Fix the within clause
                # mofile = Model(new_filename)
                #
                # # previous paths and replace with the new one.
                # # Make sure to update the names of any resources as well.
                # mofile.set_within_statement(f'{scaffold.project_name}.Districts')
                # mofile.save()

        finally:
            os.chdir(curdir)

        # run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """
        Cleanup the export of district systems. This includes the following:

            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """

        # now create the Districts level package. This (for now) will create the package without considering any existing
        # files in the Districts directory.
        order_files = [os.path.splitext(os.path.basename(mo))[0] for mo in self.required_mo_files]
        order_files.append("DistrictCoolingSystem")
        package = PackageParser.new_from_template(
            scaffold.districts_path.files_dir, "Districts",
            order=order_files,
            within=f"{scaffold.project_name}"
        )
        package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Districts"]
        )
        pp.save()
