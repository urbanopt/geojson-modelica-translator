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
from collections import defaultdict

from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.scaffold import Scaffold
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_template(template_name, template_params):
    """Helper for rendering a template

    :param template_name: string, name of template (relative to templates directory)
    :param template_params: dict, template parameters
    :return: string, templated result
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
    template_env = Environment(
        loader=FileSystemLoader(searchpath=template_dir),
        undefined=StrictUndefined)
    template = template_env.get_template(template_name)
    return template.render(template_params)


class District(object):
    """
    Class for modeling entire district energy systems
    """

    def __init__(self, root_dir, project_name, system_parameters, couplings):
        self._scaffold = Scaffold(root_dir, project_name)

        self.system_parameters = system_parameters

        if len(couplings) == 0:
            raise Exception('At least one coupling must be provided')
        self._couplings = couplings

        self._models_by_id = {}
        for coupling in self._couplings:
            a, b = coupling._model_a, coupling._model_b
            self._models_by_id[a.id] = a
            self._models_by_id[b.id] = b

        self._couplings_by_model_id = defaultdict(list)
        for coupling in self._couplings:
            a, b = coupling._model_a, coupling._model_b
            self._couplings_by_model_id[a.id].append(coupling)
            self._couplings_by_model_id[b.id].append(coupling)

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
        for _, model in self._models_by_id.items():
            model.to_modelica(self._scaffold)

        district_template_params = {
            "district_within_path": '.'.join([self._scaffold.project_name, 'Districts']),
            "couplings": [],
            "models": []
        }
        common_template_params = {
            'globals': {
                "medium_w": "MediumW"
            }
        }
        # render each coupling
        for coupling in self._couplings:
            templated_result = coupling.render_templates(common_template_params)
            district_template_params['couplings'].append({
                'component_definitions': templated_result['component_definitions'],
                'connect_statements': templated_result['connect_statements']
            })

        # render each model instance
        for identifier, model in self._models_by_id.items():
            associated_couplings = self._couplings_by_model_id[identifier]
            # directional couplings stores the associated couplings keyed by the
            # types of the _other_ model involved
            # e.g. if current model is ets, and coupled to load and network,
            # the directional coupling would be:
            # {
            #    'load_coupling': <load coupling>,
            #    'network_coupling': <network coupling>,
            # }
            directional_couplings = {}
            for coupling in associated_couplings:
                other_model = coupling.get_other_model(model)
                coupling_type = f'{other_model.simple_gmt_type}_coupling'
                directional_couplings[coupling_type] = coupling.to_dict()

            template_params = {
                'model': model.to_dict(self._scaffold),
                'couplings': directional_couplings,
            }
            template_params.update(**common_template_params)
            result = model.render_instance(template_params)
            district_template_params['models'].append(result)

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
