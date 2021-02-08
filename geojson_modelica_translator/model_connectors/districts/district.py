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
import os

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.scaffold import Scaffold
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_template(template_name, template_params):
    """Helper for rendering a template

    :param template_name: string, name of template (relative to templates directory)
    :param template_params: dict, template parameters
    :return: string, templated result
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    template_env = Environment(
        loader=FileSystemLoader(searchpath=template_dir),
        undefined=StrictUndefined)
    template_env.filters.update(ALL_CUSTOM_FILTERS)
    template = template_env.get_template(template_name)
    return template.render(template_params)


class District:
    """
    Class for modeling entire district energy systems
    """

    def __init__(self, root_dir, project_name, system_parameters, coupling_graph):
        self._scaffold = Scaffold(root_dir, project_name)
        self.system_parameters = system_parameters
        self._coupling_graph = coupling_graph

    def to_modelica(self):
        """Generate modelica files for the models as well as the modelica file for
        the entire district system.
        """
        self._scaffold.create()
        # create the root package
        root_package = PackageParser.new_from_template(
            self._scaffold.project_path, self._scaffold.project_name, order=[])
        root_package.save()

        # generate model modelica files
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        district_template_params = {
            "district_within_path": '.'.join([self._scaffold.project_name, 'Districts']),
            "couplings": [],
            "models": []
        }
        common_template_params = {
            'globals': {
                'medium_w': 'MediumW',
                'delChiWatTemBui': 'delChiWatTemBui',
                'delChiWatTemDis': 'delChiWatTemDis',
                'delHeaWatTemBui': 'delHeaWatTemBui',
                'delHeaWatTemDis': 'delHeaWatTemDis',
            },
            'graph': self._coupling_graph
        }
        # render each coupling
        for coupling in self._coupling_graph.couplings:
            templated_result = coupling.render_templates(common_template_params)
            district_template_params['couplings'].append({
                'id': coupling.id,
                'component_definitions': templated_result['component_definitions'],
                'connect_statements': templated_result['connect_statements'],
                'coupling_definitions_template_path': templated_result['component_definitions_template_path'],
                'connect_statements_template_path': templated_result['connect_statements_template_path'],
            })

        # render each model instance
        for model in self._coupling_graph.models:
            template_params = {
                'model': model.to_dict(self._scaffold),
                'couplings': self._coupling_graph.couplings_by_type(model.id),
            }
            template_params.update(**common_template_params)
            templated_instance, instance_template_path = model.render_instance(template_params)
            district_template_params['models'].append({
                'id': model.id,
                'instance_template_path': instance_template_path,
                'instance': templated_instance
            })

        # render the full district file
        final_result = render_template('DistrictEnergySystem.mot', district_template_params)
        with open(f'{self._scaffold.districts_path.files_dir}/DistrictEnergySystem.mo', 'w') as f:
            f.write(final_result)

        districts_package = PackageParser.new_from_template(self._scaffold.districts_path.files_dir, "Districts", [
            'DistrictEnergySystem'], within=f"{self._scaffold.project_name}")
        districts_package.save()
        root_package = PackageParser(self._scaffold.project_path)
        root_package.add_model('Districts')
        root_package.save()
