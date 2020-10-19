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
from collections import namedtuple
import os

from geojson_modelica_translator.scaffold import Scaffold
from geojson_modelica_translator.modelica.input_parser import PackageParser

from modelica_builder.model import Model as ModBuilderModel


Component = namedtuple('Component', ['identifier', 'model'])


class District(object):
    """
    Class for modeling entire district energy systems
    """
    
    def __init__(self, root_dir, project_name, system_parameters, components, connections):
        self._scaffold = Scaffold(root_dir, project_name)

        self.system_parameters = system_parameters

        # dict of components and their connections in adjacency list format
        # [
        #   building_A.as_component('myBuildingA', {modifications}),
        #   ets_A.as_component('myBuildingB', {modifications}),
        # ]
        #
        self._components = components

        # list of tuples of ports (maybe at first this will just be the text to be inserted into modelica code
        #   but eventually there should be a Port class used in components that validates the port is valid for the component/model)
        #
        # [
        #   (componentA.ports.port_aHeaWat, componentB.ports.ports[1]),
        #   (componentA.ports.port_bHeaWat, componentC.ports.ports[1]),
        # ]
        self._connections = connections

    def to_modelica(self):
        """Generate modelica files for the components as well as the modelica file for
        the entire system.
        """
        self._scaffold.create()
        # create the root package
        root_package = PackageParser.new_from_template(self._scaffold.project_path, self._scaffold.project_name, order=[])
        root_package.save()

        # generate modelica files for all components
        for component in self._components:
            component.model.to_modelica(self._scaffold)

        # build the district energy system model by inserting and connecting components
        district_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "DistrictEnergySystem.mo")
        district_builder = ModBuilderModel(district_source)
        district_builder.set_within_statement(f'{self._scaffold.project_name}.Districts')

        component_x = -50
        COMPONENT_Y = 0
        COMPONENT_HALF_WIDTH = 10
        COMPONENT_PADDING = 20
        for component in self._components:
            district_builder.insert_component(
                type_=component.model.get_modelica_type(self._scaffold),
                identifier=component.identifier,
                annotations=[
                    "Placement(transformation(extent={{-10,-10},{10,10}},"
                    "origin={" + f"{component_x},{COMPONENT_Y}" + "}))"
                ]
            )
            component_x += COMPONENT_PADDING + (COMPONENT_HALF_WIDTH * 2)

        # make all required connections in the district modelica file
        for connection in self._connections:
            district_builder.add_connect(connection[0], connection[1])

        district_builder.save_as(f'{self._scaffold.districts_path.files_dir}/DistrictEnergySystem.mo')

        districts_package = PackageParser.new_from_template(
            self._scaffold.districts_path.files_dir, "Districts", ['DistrictEnergySystem'], within=f"{self._scaffold.project_name}"
        )
        districts_package.save()
        root_package = PackageParser(self._scaffold.project_path)
        root_package.add_model('Districts')
        root_package.save()
