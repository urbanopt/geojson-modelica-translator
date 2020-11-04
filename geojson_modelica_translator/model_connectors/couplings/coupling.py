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
from uuid import uuid4

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.model_connectors.loads.load_base import (
    LoadBase
)
from geojson_modelica_translator.model_connectors.networks.network_base import (
    NetworkBase
)
from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta


class Coupling(object):
    _template_component_definitions = 'ComponentDefinitions.mopt'
    _template_connect_statements = 'ConnectStatements.mopt'

    def __init__(self, model_a, model_b):
        model_a, model_b = self._sort_models(model_a, model_b)
        self._model_a = model_a
        self._model_b = model_b
        self._template_base_name = f'{model_a.model_name}_{model_b.model_name}'

        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", self._template_base_name)
        if not os.path.exists(template_dir):
            raise Exception(f'Invalid coupling. Missing {template_dir} directory.')

        self._template_env = Environment(
            loader=FileSystemLoader(searchpath=template_dir),
            undefined=StrictUndefined)

    def _get_model_superclass(self, model):
        valid_superclasses = [LoadBase, EnergyTransferBase, NetworkBase]
        superclasses = [cls_ for cls_ in model.__class__.mro() if cls_ in valid_superclasses]
        if len(superclasses) != 1:
            return None
        return superclasses[0]

    def _sort_models(self, a, b):
        """Return models in sorted order according to their type (load, ets, network, etc)

        This is used to have a consistent method of looking up coupling template files
        :param a: model
        :param b: model
        :return: list, a and b sorted
        """
        superclass_order = [LoadBase, EnergyTransferBase, NetworkBase]

        def _sort(x):
            # get x's superclass and return its index
            x_superclass = self._get_model_superclass(x)
            return superclass_order.index(x_superclass)

        return sorted([a, b], key=_sort)

    def _get_template_parameters(self, template_name):
        template_source = self._template_env.loader.get_source(self._template_env, template_name)[0]
        parsed_content = self._template_env.parse(template_source)
        return meta.find_undeclared_variables(parsed_content)

    def _render_template(self, template_name, template_params, generate_missing=True):
        """Return the templated partial for the coupling as well as generated variables

        :param template_name: string
        :param template_params: dict
        :param generate_missing: bool
        :return: string, dict
        """
        template = self._template_env.get_template(template_name)

        def _get_model_id(model):
            superclass_dict = {
                LoadBase: 'load_id',
                EnergyTransferBase: 'ets_id',
                NetworkBase: 'network_id'
            }
            superclass = self._get_model_superclass(model)
            return superclass_dict[superclass]

        updated_template_params = {}
        updated_template_params.update(template_params)
        updated_template_params[_get_model_id(self._model_a)] = self._model_a.identifier
        updated_template_params[_get_model_id(self._model_b)] = self._model_b.identifier

        generated_params = {}
        if generate_missing:
            required_params = self._get_template_parameters(template_name)
            for param in required_params:
                if param not in updated_template_params:
                    if param.endswith('_id'):
                        generated_params[param] = f'{param}_{str(uuid4()).split("-")[0]}'
                    else:
                        raise Exception(f'Missing required parameter that\'s not an id: "{param}". Append _id if it should be generated.')
            updated_template_params.update(generated_params)

        return template.render(updated_template_params), generated_params

    def render_templates(self, template_params):
        component_result, generated_params = self._render_template(self._template_component_definitions, template_params)
        updated_params = {}
        updated_params.update(**template_params, **generated_params)
        connect_result, _ = self._render_template(self._template_connect_statements, updated_params, generate_missing=False)

        return {
            'component_definitions': component_result,
            'connect_statements': connect_result,
            'generated_params': generated_params
        }

    def component_definitions(self, template_params):
        """Return templated component definitions partial.

        :param template_params: dict
        :return: string, dict, the templated result and generated variables
        """
        return self._render_template(self._template_component_definitions, template_params)

    def connect_statements(self, template_params):
        """Return templated connect statements partial.

        :param template_params: dict
        :return: string, the templated result
        """
        result, _ = self._render_template(self._template_connect_statements, template_params, generate_missing=False)
        return result
