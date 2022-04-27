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
from pathlib import Path

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.model_connectors.networks.network_base import (
    NetworkBase
)
from geojson_modelica_translator.model_connectors.plants.plant_base import (
    PlantBase
)
from geojson_modelica_translator.utils import simple_uuid
from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta


class Coupling(object):
    """A Coupling represents a connection/relationship between two models (e.g. a load and ets).
    More specifically, is used to create the required components and connections between two models.
    """
    _template_component_definitions = 'ComponentDefinitions.mopt'
    _template_connect_statements = 'ConnectStatements.mopt'

    def __init__(self, model_a, model_b):
        model_a, model_b = self._sort_models(model_a, model_b)
        self._model_a = model_a
        self._model_b = model_b
        self._template_base_name = f'{model_a.model_name}_{model_b.model_name}'

        self._template_dir = Path(__file__).parent / "templates" / self._template_base_name
        if not Path(self._template_dir).exists():
            raise Exception(f'Invalid coupling. Missing {self._template_dir} directory.')

        self._template_env = Environment(
            loader=FileSystemLoader(searchpath=self._template_dir),
            undefined=StrictUndefined)
        self._template_env.filters.update(ALL_CUSTOM_FILTERS)

        self._id = simple_uuid()

    @property
    def id(self):
        return self._id

    @property
    def model_a(self):
        return self._model_a

    @property
    def model_b(self):
        return self._model_b

    def to_dict(self):
        return {
            'id': self._id,
            self._model_a.simple_gmt_type: {
                'id': self._model_a.id,
            },
            self._model_b.simple_gmt_type: {
                'id': self._model_b.id,
            }
        }

    def get_other_model(self, model):
        """Returns the other model in the coupling

        :param model: Model
        :return: Model
        """
        if model == self._model_a:
            return self._model_b
        elif model == self._model_b:
            return self._model_a
        raise Exception(f'Provided model, "{model.id}", is not part of the coupling ({self._model_a.id}, {self._model_b.id})')

    def _get_model_superclass(self, model):
        valid_superclasses = [LoadBase, EnergyTransferBase, NetworkBase, PlantBase]
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
        superclass_order = [LoadBase, EnergyTransferBase, NetworkBase, PlantBase]

        def _sort(x):
            # get x's superclass and return its index
            x_superclass = self._get_model_superclass(x)
            return superclass_order.index(x_superclass)

        return sorted([a, b], key=_sort)

    def _get_template_parameters(self, template_name):
        template_source = self._template_env.loader.get_source(self._template_env, template_name)[0]
        parsed_content = self._template_env.parse(template_source)
        return meta.find_undeclared_variables(parsed_content)

    def _render_template(self, template_name, template_params):
        """Return the templated partial for the coupling

        :param template_name: string
        :param template_params: dict
        :return: string
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

        assert 'coupling' not in template_params, 'Template parameters for Coupling must not include the key "coupling"'
        updated_template_params = {
            'coupling': self.to_dict()
        }
        updated_template_params.update(template_params)

        # get the template file path relative to the package
        template_filename = Path(template.filename).as_posix()
        _, template_filename = template_filename.rsplit('geojson_modelica_translator', 1)

        return template.render(updated_template_params), template_filename

    def render_templates(self, template_params):
        """Renders the shared components and connect statements for the coupling.

        :param template_params: dict, parameters for the templates
        :return: dict, containing key, values: component_definitions, string; connect_statements, string
        """
        component_result, component_template_path = self._render_template(self._template_component_definitions, template_params)
        connect_result, connect_template_path = self._render_template(self._template_connect_statements, template_params)

        return {
            'component_definitions': component_result,
            'connect_statements': connect_result,
            'component_definitions_template_path': component_template_path,
            'connect_statements_template_path': connect_template_path,
        }

    def get_load(self):
        """If there's a load model in the coupling, it returns the load model. Else
        it returns None.

        This is used by the district model to find the building's sys params so
        it can be passed into the coupling templates

        :return: LoadBase | None
        """
        if self._get_model_superclass(self.model_a) is LoadBase:
            return self.model_a
        elif self._get_model_superclass(self.model_b) is LoadBase:
            return self.model_b

        return None

    @property
    def component_definitions_template_path(self):
        return self._template_env.get_template(self._template_component_definitions).filename

    @property
    def connect_statements_template_path(self):
        return self._template_env.get_template(self._template_connect_statements).filename
