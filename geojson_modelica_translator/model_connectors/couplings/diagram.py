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
from collections import defaultdict

from geojson_modelica_translator.model_connectors.couplings.utils import (
    DiagramLine,
    DiagramTransformation,
    parse_diagram_commands
)


class Diagram:
    def __init__(self, coupling_graph):
        self._initial_diagram_graph = self._parse_coupling_graph(coupling_graph)

    @classmethod
    def _parse_coupling_graph(cls, coupling_graph):
        """Returns a data structure representing the visual (ie diagram) of the graph
        {
            '<model instance or coupling id>' : {
                '<component name>': {
                    'type': '<component type e.g. load>',
                    'edges': {
                        '<component port name>': [
                            ('<other model instance or coupling id>', '<other component name>', '<other component port>'), ...
                        ]
                    }
                }, ...
            }, ...
        }
        """
        diagram_commands_by_id = {}
        for coupling in coupling_graph.couplings:
            with open(coupling.component_definitions_template_path) as f:
                coupling_diagram_commands = parse_diagram_commands(f.read())
            with open(coupling.connect_statements_template_path) as f:
                coupling_diagram_commands += parse_diagram_commands(f.read())
            diagram_commands_by_id[coupling.id] = coupling_diagram_commands

        for model in coupling_graph.models:
            with open(model.instance_template_path) as f:
                model_diagram_commands = parse_diagram_commands(f.read())
            diagram_commands_by_id[model.id] = model_diagram_commands

        return cls._diagram_commands_to_graph(diagram_commands_by_id, coupling_graph.couplings)

    @staticmethod
    def _diagram_commands_to_graph(diagram_commands_by_id, couplings):
        """Convert commands into a diagram graph.

        :param diagram_commands: dict
        :param couplings: list[Coupling]
        :return: dict, diagram graph
        """
        # first add the graph nodes, which are the transformation commands (they're the rendering of icons)
        diagram_graph_by_id = {}
        for diagram_context_id, commands in diagram_commands_by_id.items():
            diagram_graph_by_id[diagram_context_id] = {}
            transformation_cmds = [cmd for cmd in commands if isinstance(cmd, DiagramTransformation)]
            for cmd in transformation_cmds:
                diagram_graph_by_id[diagram_context_id][cmd.model_name] = {}
                diagram_graph_by_id[diagram_context_id][cmd.model_name]['type'] = cmd.model_type
                # we will add edges later
                diagram_graph_by_id[diagram_context_id][cmd.model_name]['edges'] = defaultdict(list)

        def _find_id_by_name(name, diagram_context_id):
            """Helper for finding the ID of the context for a given name

            Default to the scope of the provided diagram context id, and if the context
            is a coupling, fallback to the contexts of the coupled models.
            """
            if name in diagram_graph_by_id[diagram_context_id]:
                # nice! it's here, we will connect to this one
                return diagram_context_id
            else:
                # if our current context is a coupling, check the models we are coupling for the name
                # if our current context isn't a coupling (ie a model), fail
                #   (models should only connect to components within their own contexts)
                coupling = [c for c in couplings if c.id == diagram_context_id]
                if coupling:
                    coupling = coupling[0]
                else:
                    raise Exception(f'Invalid diagram line command: unable to find "{name}" in the context of {diagram_context_id}')

                # search each of the coupling's models nodes for the element
                coupling_model_a_id = coupling._model_a.id
                found_in_model_a = coupling_model_a_id in diagram_graph_by_id and name in diagram_graph_by_id[coupling_model_a_id]
                coupling_model_b_id = coupling._model_b.id
                found_in_model_b = coupling_model_b_id in diagram_graph_by_id and name in diagram_graph_by_id[coupling_model_b_id]

                if found_in_model_a and found_in_model_b:
                    raise Exception(
                        f'Invalid diagram line command: unable to determine which model "{name}" '
                        'should connect to since it was not in the coupling and was found in both '
                        'of the coupling\'s models'
                    )
                elif found_in_model_a:
                    return coupling_model_a_id
                elif found_in_model_b:
                    return coupling_model_b_id
                else:
                    raise Exception(
                        f'Invalid diagram line command: failed to find "{name}" '
                        'in the coupling or either of the coupled models'
                    )

        # add the edges between nodes, which are line commands (they're connectors between icons)
        for diagram_context_id, commands in diagram_commands_by_id.items():
            line_cmds = [cmd for cmd in commands if isinstance(cmd, DiagramLine)]
            for cmd in line_cmds:
                a_name, a_port, b_name, b_port = cmd.a_name, cmd.a_port, cmd.b_name, cmd.b_port

                # find IDs of the referenced components
                a_id = _find_id_by_name(a_name, diagram_context_id)
                b_id = _find_id_by_name(b_name, diagram_context_id)

                diagram_graph_by_id[a_id][a_name]['edges'][a_port].append((b_id, b_name, b_port))
                diagram_graph_by_id[b_id][b_name]['edges'][b_port].append((a_id, a_name, a_port))

        return diagram_graph_by_id
