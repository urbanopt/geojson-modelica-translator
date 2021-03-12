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
from abc import ABC, abstractmethod
from collections import defaultdict
from string import Template

from geojson_modelica_translator.model_connectors.couplings.utils import (
    DiagramLine,
    DiagramTransformation,
    parse_diagram_commands
)


class Diagram:
    grid_cells_width = 10  # width and height of grid in number of cells
    grid_cell_size = 20
    grid_size = grid_cells_width * grid_cell_size
    icon_padding = grid_cell_size

    def __init__(self, coupling_graph):
        self._coupling_graph = coupling_graph
        self._initial_diagram_graph = self._parse_coupling_graph(coupling_graph)

        # TODO: organize diagram rather than using x, y coords for placing
        # track coordinates, with 0,0 at top left, coords increasing moving down and right
        self._current_x, self._current_y = 0, 0

    def to_dict(self, id, is_coupling):
        """Get the diagram as a dictionary, to be used for templating for model
        instances or couplings.

        :param id: str, model or coupling ID to get the dictionary for
        :param is_coupling: bool, True if id is for a coupling, False if id is for a model

        {
            'transformation': {
                '<model name>': {
                    '<model type>': 'transformation(extent={{0,-10},{20,10}})'
                }
            },
            'line': {
                '<model A name>': {
                    '<model A port>': {
                        'model B name': {
                            'model B port': 'Line(points={{21,0},{46,0}},color={0,0,127})'
                        }
                    }
                }
            }
        }
        """
        def translate_x(pos):
            # translate from origin at upper left of grid to center of grid
            return pos - (self.grid_size / 2)

        def translate_y(pos):
            return (self.grid_size / 2) - pos

        transformations = defaultdict(dict)
        lines = defaultdict(dict)
        transformation_template = Template('transformation(extent={{$x1,$y1},{$x2,$y2}})')
        line_template = Template('Line(points={{21,0},{46,0}},color={0,0,127})')

        # add transformations defined within this id's context
        # e.g. if id is for a model, add all transformations defined in the model instance template
        for component_name, details in self._initial_diagram_graph.get(id, {}).items():
            icon = DiagramIcon.get_icon(details['type'])
            # x1, y1 is lower left of icon, x2, y2 is upper right
            coords = {
                'x1': translate_x(self._current_x),
                'y1': translate_y(self._current_y + (icon.height * self.grid_cell_size)),
                'x2': translate_x(self._current_x + (icon.width * self.grid_cell_size)),
                'y2': translate_y(self._current_y),
            }
            transformations[component_name][details['type']] = transformation_template.substitute(coords)

            self._current_x = self._current_x + self.grid_cell_size + self.icon_padding
            if self._current_x >= self.grid_size:
                self._current_x = 0
            if self._current_x == 0:
                # move to next grid row
                self._current_y += self.grid_cell_size + self.icon_padding

        diagram_ids = [id]
        if is_coupling:
            coupling = self._coupling_graph.get_coupling(id)
            diagram_ids += [coupling.model_a.id, coupling.model_b.id]

        # add lines - including the edges connecting components not written as part of the coupling
        for diagram_id in diagram_ids:
            for component_name, details in self._initial_diagram_graph.get(diagram_id, {}).items():
                for component_port, other_components in details['edges'].items():
                    for other_component in other_components:
                        other_id, other_name, other_port = other_component
                        # include this line if either:
                        #   - we're working on the coupling lines
                        #   - this edge connects to another model we might be interested in
                        #     (e.g. model a instance connecting to model b instance)
                        include_line = diagram_id == id or other_id in diagram_ids
                        if include_line:
                            line = line_template.substitute()
                            if component_port not in lines[component_name]:
                                lines[component_name][component_port] = {
                                    other_name: {
                                        other_port: line
                                    }
                                }
                            else:
                                lines[component_name][component_port][other_name] = {
                                    other_port: line
                                }

        return {
            'transformation': transformations,
            'line': lines,
        }

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
        template_files_by_id = defaultdict(list)
        for coupling in coupling_graph.couplings:
            template_files_by_id[coupling.id].append(coupling.component_definitions_template_path)
            template_files_by_id[coupling.id].append(coupling.connect_statements_template_path)

        for model in coupling_graph.models:
            template_files_by_id[model.id].append(model.instance_template_path)

        diagram_commands_by_id = defaultdict(list)
        for id_, template_files in template_files_by_id.items():
            for template_file in template_files:
                try:
                    with open(template_file) as f:
                        diagram_commands_by_id[id_].extend(parse_diagram_commands(f.read()))
                except Exception as e:
                    raise Exception(f'Failed to parse diagram commands for {template_file}: {str(e)}')

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
                        f'in the coupling or either of the coupled models ({coupling_model_a_id} and {coupling_model_b_id})'
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


class DiagramIcon(ABC):
    @property
    @abstractmethod
    def height(self):
        """fraction of a diagram grid cell height (1 is full height, 0.5 is half, etc)"""
        pass

    @property
    @abstractmethod
    def width(self):
        """fraction of a diagram grid cell width (1 is full width, 0.5 is half, etc)"""
        pass

    @staticmethod
    def get_icon(icon_type):
        if icon_type == 'load':
            return LoadIcon()
        elif icon_type == 'network':
            return NetworkIcon()
        else:
            # use load icon as default for now
            return LoadIcon()


class LoadIcon(DiagramIcon):
    @property
    def height(self):
        return 1

    @property
    def width(self):
        return 1


class NetworkIcon(DiagramIcon):
    @property
    def height(self):
        return 0.5

    @property
    def width(self):
        return 1
