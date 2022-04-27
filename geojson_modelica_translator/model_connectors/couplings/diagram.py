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
from collections import defaultdict, namedtuple
from itertools import zip_longest
from random import uniform
from string import Template

from geojson_modelica_translator.model_connectors.couplings.utils import (
    DiagramLine,
    DiagramTransformation,
    find_path_bfs,
    parse_diagram_commands
)

NodePort = namedtuple('NodePort', ['node', 'port'])


class DiagramNode:
    def __init__(self, context_id, model_name, model_type):
        """
        :param context_id: str, used for "grouping" nodes. E.g. this would be
          either the coupling id or the model id (depending on where the icon is declared)
        :param model_name: str
        :param model_type: str, general type of the component (e.g. load, network, etc)
        """
        self.context_id = context_id
        self.model_name = model_name
        self.model_type = model_type
        self.icon = DiagramIcon.get_icon(model_type)
        self.connections = defaultdict(list)
        self.grid_col = None
        self.grid_row = None

    def __eq__(self, other):
        if not isinstance(other, DiagramNode):
            return False

        def _simple_eq(a, b):
            return (
                a.context_id == b.context_id
                and a.model_name == b.model_name
            )

        if not _simple_eq(self, other):
            return False

        # check connections iteratively to avoid infinite recursion
        if self.connections.keys() != other.connections.keys():
            return False

        for port_name in self.connections.keys():
            for self_conn, other_conn in zip(self.connections[port_name], other.connections[port_name]):
                if not _simple_eq(self_conn.node, other_conn.node) or self_conn.port != other_conn.port:
                    return False

        return True

    def __hash__(self):
        return hash((self.context_id, self.model_name, self.model_type))

    def add_connection(self, this_port, other_node, other_port):
        """
        :param this_port: str, name or dotted path of port for this node (should not start with '.' though)
        :param other_node: DiagramNode, other node connecting to
        :param other_port: str, name or dotted path of port for other node (should not start with '.' though)
        """
        self.connections[this_port].append(NodePort(other_node, other_port))


class Diagram:
    grid_cell_size = 20
    icon_padding = 1  # number of cells padding each icon

    def __init__(self, coupling_graph):
        # set when calculating the icon placements
        self.grid_height_px = None
        self.grid_width_px = None
        self._diagram_matrix = None

        self._coupling_graph = coupling_graph
        self._initial_diagram_graph = self._parse_coupling_graph(coupling_graph)
        self._resolve_icon_placements()

    @property
    def extent(self):
        """Returns extent as a string for templating into the district model

        :return: str
        """
        half_width = self.grid_width_px / 2
        half_height = self.grid_height_px / 2
        return f'{{{{-{half_width},-{half_height}}},{{{half_width},{half_height}}}}}'

    def _grid_to_coord(self, col, row):
        return self.grid_cell_size * col, self.grid_cell_size * row

    def _translate_x(self, pos):
        # translate from origin at upper left of grid to center of grid
        return pos - (self.grid_width_px / 2)

    def _translate_y(self, pos):
        # translate from origin at upper left of grid to center of grid
        return (self.grid_height_px / 2) - pos

    def to_dict(self, context_id, is_coupling):
        """Get the diagram as a dictionary, to be used for templating for model
        instances or couplings.

        :param context_id: str, model or coupling context_id to get the dictionary for
        :param is_coupling: bool, True if context_id is for a coupling, False if context_id is for a model

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
        transformations = defaultdict(dict)
        lines = defaultdict(dict)
        transformation_template = Template('transformation(extent={{$x1,$y1},{$x2,$y2}})')
        line_template = Template('Line(points={$points},color={0,0,127})')

        # add transformations defined within this id's context
        # e.g. if id is for a model, add all transformations defined in the model instance template
        for component_name, diagram_node in self._initial_diagram_graph.get(context_id, {}).items():
            # x1, y1 is lower left of icon, x2, y2 is upper right
            x_pos, y_pos = self._grid_to_coord(diagram_node.grid_col, diagram_node.grid_row)
            coords = {
                'x1': self._translate_x(x_pos),
                'y1': self._translate_y(y_pos + (diagram_node.icon.height * self.grid_cell_size)),
                'x2': self._translate_x(x_pos + (diagram_node.icon.width * self.grid_cell_size)),
                'y2': self._translate_y(y_pos),
            }
            transformations[component_name][diagram_node.model_type] = transformation_template.substitute(coords)

        diagram_ids = [context_id]
        if is_coupling:
            coupling = self._coupling_graph.get_coupling(context_id)
            diagram_ids += [coupling.model_a.id, coupling.model_b.id]

        # add lines - including the edges connecting components not written as part of the coupling
        for this_context_id in diagram_ids:
            for component_name, diagram_node in self._initial_diagram_graph.get(this_context_id, {}).items():
                for component_port, others in diagram_node.connections.items():
                    for other in others:
                        other_node, other_port = other.node, other.port
                        # include this connection if either:
                        #   - we're working on the coupling lines
                        #   - this connects to another model we might be interested in
                        #     (e.g. model a instance connecting to model b instance)
                        include_line = this_context_id == context_id or other_node.context_id in diagram_ids
                        if include_line:
                            points = self._calculate_connector_line(
                                diagram_node,
                                component_port,
                                other_node,
                                other_port
                            )
                            formatted_points = [f'{{{x},{y}}}' for x, y in points]
                            line = line_template.substitute(
                                points=','.join(formatted_points)
                            )
                            if component_port not in lines[component_name]:
                                lines[component_name][component_port] = {
                                    other_node.model_name: {
                                        other_port: line
                                    }
                                }
                            else:
                                lines[component_name][component_port][other_node.model_name] = {
                                    other_port: line
                                }

        return {
            'transformation': transformations,
            'line': lines,
        }

    def _calculate_connector_line(self, node_a, port_a, node_b, port_b):
        """Determines a coordinate path to get from node a's port to node b's port

        :param node_a: DiagramNode
        :param port_a: str
        :param node_b: DiagramNode
        :param port_b: str
        :return: list, list of x,y tuples
        """
        grid_path = find_path_bfs(
            self._diagram_matrix,
            node_a.grid_row,
            node_a.grid_col,
            node_b.grid_row,
            node_b.grid_col
        )

        # convert grid path into a coordinate path for the diagram
        diagram_path = []
        half_cell = self.grid_cell_size / 2
        # hack: add a random offsets to make lines overlap less
        x_offset = uniform(half_cell * -1, half_cell)
        y_offset = uniform(half_cell * -1, half_cell)
        for pos in grid_path:
            x, y = self._grid_to_coord(pos[1] + 0.5, pos[0] + 0.5)
            diagram_path.append((
                self._translate_x(x + x_offset),
                self._translate_y(y + y_offset)
            ))

        return diagram_path

    def _resolve_icon_placements(self):
        """Calculate and add locations to all diagram graph nodes. This should be
        called automatically when initializing the class.
        """

        def get_nodes_of_type(node_type):
            nodes = []
            for _, context_nodes in self._initial_diagram_graph.items():
                for _, node in context_nodes.items():
                    if node_type != 'auxillary' and node.model_type == node_type:
                        nodes.append(node)
                    if node_type == 'auxillary' and node.model_type not in ['load', 'ets', 'plant', 'network']:
                        nodes.append(node)
            return nodes

        def get_connected_nodes_of_type(node, other_node_type):
            # use a set to avoid duplicates (a node might have multiple connections to another node)
            nodes = set()
            for _, connections in node.connections.items():
                for connection in connections:
                    other_node = connection.node
                    if other_node.model_type == other_node_type:
                        nodes.add(other_node)
            return list(nodes)

        MAX_ICONS_PER_ROW = 4

        load_ets_rows = []
        # add loads and etses
        loads = get_nodes_of_type('load')
        for load_node in loads:
            etses = get_connected_nodes_of_type(load_node, 'ets')
            for load_ets_pair in zip_longest(etses, [load_node], fillvalue=None):
                load_ets_rows.append(list(load_ets_pair))

        network_plant_rows = []
        # add networks and plants
        for i, plant in enumerate(get_nodes_of_type('plant')):
            grid_row = []
            grid_row.append(plant)
            # NOTE: should only have one plant connected to a network
            for network in get_connected_nodes_of_type(plant, 'network'):
                grid_row.append(network)

            network_plant_rows.append(grid_row)

        # make sure each set of rows has the same length
        num_network_plant_rows = len(network_plant_rows)
        num_load_ets_rows = len(load_ets_rows)
        if num_network_plant_rows < num_load_ets_rows:
            # pad the network plant rows
            num_pad_rows = num_load_ets_rows - num_network_plant_rows
            NUM_ICONS = 2  # dehardcode
            for _ in range(num_pad_rows):
                network_plant_rows.append([None] * NUM_ICONS)
        elif num_load_ets_rows < num_network_plant_rows:
            # pad the load ets rows
            num_pad_rows = num_network_plant_rows - num_load_ets_rows
            NUM_ICONS = 2  # dehardcode
            for _ in range(num_pad_rows):
                load_ets_rows.append([None] * NUM_ICONS)

        # merge all of the rows
        merged_rows = []
        for left, right in zip(network_plant_rows, load_ets_rows):
            merged_rows.append(left + right)

        # add auxillary rows
        grid_row = []
        for node in get_nodes_of_type('auxillary'):
            if len(grid_row) == MAX_ICONS_PER_ROW:
                # start a new row
                merged_rows.append(grid_row)
                grid_row = [node]
            else:
                # continue building row
                grid_row.append(node)
        # add remaining row
        merged_rows.append(grid_row)

        # make sure all rows have the same number of columns by adding `None`s
        # to the end of shorter rows
        # TODO: find better solution
        longest_row = max([len(row) for row in merged_rows])
        for row in merged_rows:
            row += [None] * (longest_row - len(row))

        # add padding between icons by building an updated grid
        # first row should be empty (+1 to make sure there's pad on both sides)
        grid_cells_per_row = 1 + MAX_ICONS_PER_ROW + (MAX_ICONS_PER_ROW * self.icon_padding)
        diagram_matrix = [[None] * grid_cells_per_row]
        for row in merged_rows:
            # first col of row should be empty
            final_row = [None]
            for col in row:
                final_row += [col] + ([None] * self.icon_padding)
            diagram_matrix.append(final_row)
            for _ in range(self.icon_padding):
                diagram_matrix.append([None] * grid_cells_per_row)

        # calculate grid positions using the final result
        for i, row in enumerate(diagram_matrix):
            for j, node in enumerate(row):
                if node is None:
                    continue
                node.grid_row = i
                node.grid_col = j

        self.grid_height_px = len(diagram_matrix) * self.grid_cell_size
        self.grid_width_px = len(diagram_matrix[0]) * self.grid_cell_size
        self._diagram_matrix = diagram_matrix

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
        # parse the visual diagram from the template files
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

        :param diagram_commands: dict[str: DiagramCommand]
        :param couplings: list[Coupling]
        :return: dict, diagram graph
        """
        diagram_graph_by_id = defaultdict(dict)
        for diagram_context_id, commands in diagram_commands_by_id.items():
            # get the commands which create icons
            transformation_cmds = [cmd for cmd in commands if isinstance(cmd, DiagramTransformation)]
            for cmd in transformation_cmds:
                new_node = DiagramNode(diagram_context_id, cmd.model_name, cmd.model_type)
                diagram_graph_by_id[diagram_context_id][cmd.model_name] = new_node

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
                model_a_id = coupling._model_a.id
                found_in_model_a = model_a_id in diagram_graph_by_id and name in diagram_graph_by_id[model_a_id]
                model_b_id = coupling._model_b.id
                found_in_model_b = model_b_id in diagram_graph_by_id and name in diagram_graph_by_id[model_b_id]

                if found_in_model_a and found_in_model_b:
                    raise Exception(
                        f'Invalid diagram line command: unable to determine which model "{name}" '
                        'should connect to since it was not in the coupling and was found in both '
                        'of the coupling\'s models'
                    )
                elif found_in_model_a:
                    return model_a_id
                elif found_in_model_b:
                    return model_b_id
                else:
                    available_names_by_context_id = {
                        'coupling ' + diagram_context_id: list(diagram_graph_by_id[diagram_context_id].keys()),
                        model_a_id: list(diagram_graph_by_id[model_a_id].keys()),
                        model_b_id: list(diagram_graph_by_id[model_b_id].keys())
                    }
                    available_names_formatted = 'Available names (source):'
                    for ctx, available_names in available_names_by_context_id.items():
                        for available_name in available_names:
                            available_names_formatted += f'\n  {available_name} ({ctx})'
                    raise Exception(
                        f'Invalid diagram line command: failed to find "{name}" '
                        f'in the coupling or either of the coupled models ({model_a_id} and {model_b_id}).\n'
                        f'{available_names_formatted}'
                    )

        # add connections between nodes
        for diagram_context_id, commands in diagram_commands_by_id.items():
            line_cmds = [cmd for cmd in commands if isinstance(cmd, DiagramLine)]
            for cmd in line_cmds:
                a_name, a_port, b_name, b_port = cmd.a_name, cmd.a_port, cmd.b_name, cmd.b_port

                # find context IDs of the referenced components
                a_id = _find_id_by_name(a_name, diagram_context_id)
                b_id = _find_id_by_name(b_name, diagram_context_id)

                a_node = diagram_graph_by_id[a_id][a_name]
                b_node = diagram_graph_by_id[b_id][b_name]
                a_node.add_connection(a_port, b_node, b_port)
                b_node.add_connection(b_port, a_node, a_port)

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
