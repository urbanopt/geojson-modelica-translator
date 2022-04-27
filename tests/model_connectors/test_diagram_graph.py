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
from geojson_modelica_translator.model_connectors.couplings.diagram import (
    Diagram,
    DiagramNode
)
from geojson_modelica_translator.model_connectors.couplings.utils import (
    DiagramLine,
    DiagramTransformation,
    parse_diagram_commands
)

from ..base_test_case import TestCaseBase


class MockCoupling:
    def __init__(self, id, a, b):
        self.id = id
        self._model_a = a
        self._model_b = b


class MockModel:
    def __init__(self, id):
        self.id = id


def mock_coupling_factory(coupling_id, model_a_id, model_b_id):
    return MockCoupling(
        id=coupling_id,
        a=MockModel(model_a_id),
        b=MockModel(model_b_id)
    )


class DiagramGraphTest(TestCaseBase):
    def test_parse_diagram_commands_parses_transformations(self):
        # Setup
        modelica_content = """
model Simple
  {{ ignored.context }}
  Modelica.Blocks.Sources.RealExpression abc(y=1)
    annnotation (Placement({{ diagram.transformation.abc.real_expression }}))
end Simple;"""

        # Act
        commands = parse_diagram_commands(modelica_content)

        # Assert
        self.assertEqual(1, len(commands))
        cmd = commands[0]
        self.assertTrue(isinstance(cmd, DiagramTransformation))
        self.assertEqual(cmd.model_name, 'abc')
        self.assertEqual(cmd.model_type, 'real_expression')

    def test_parse_diagram_commands_parses_lines(self):
        # Setup
        modelica_content = """
model Simple
  {{ ignored.context }}
equation
  connect(abc.port_a, def.port_b)
    annotation(Line({{ diagram.line.abc.port_a.def.port_b }}));
end Simple;"""

        # Act
        commands = parse_diagram_commands(modelica_content)

        # Assert
        self.assertEqual(1, len(commands))
        cmd = commands[0]
        self.assertTrue(isinstance(cmd, DiagramLine))
        self.assertEqual(cmd.a_name, 'abc')
        self.assertEqual(cmd.a_port, 'port_a')
        self.assertEqual(cmd.b_name, 'def')
        self.assertEqual(cmd.b_port, 'port_b')

    def test_parse_diagram_commands_errors_when_command_is_invalid(self):
        # Setup
        bad_transformation = "{{ diagram.transformation.bad }}"
        bad_line = "{{ diagram.line.bad }}"

        # Act/Assert
        with self.assertRaisesRegex(Exception, 'Invalid diagram templating command: "transformation".*'):
            parse_diagram_commands(bad_transformation)

        with self.assertRaisesRegex(Exception, 'Invalid diagram templating command: "line".*'):
            parse_diagram_commands(bad_line)

    def test_diagram_commands_to_graph_succeeds_for_transformations(self):
        # Setup
        load_a_id = 'load_a'
        ets_a_id = 'ets_a'
        coupling_id = 'coupling_a'
        load_ets_coupling = mock_coupling_factory(coupling_id, load_a_id, ets_a_id)
        couplings = [
            load_ets_coupling,
        ]

        diagram_commands_by_id = {
            load_a_id: [DiagramTransformation(
                model_name='some_load',
                model_type='load',
            )],
            ets_a_id: [DiagramTransformation(
                model_name='some_ets',
                model_type='ets',
            )],
            # also create a transformation which is coupling specific (ie defined in a coupling template file)
            coupling_id: [DiagramTransformation(
                model_name='some_real_expression',
                model_type='real_expression',
            )]
        }

        # Act
        diagram_graph = Diagram._diagram_commands_to_graph(
            diagram_commands_by_id,
            couplings
        )

        # Assert
        expected_diagram_graph = {
            load_a_id: {
                'some_load': DiagramNode(load_a_id, 'some_load', 'load')
            },
            ets_a_id: {
                'some_ets': DiagramNode(ets_a_id, 'some_ets', 'ets')
            },
            coupling_id: {
                'some_real_expression': DiagramNode(coupling_id, 'some_real_expression', 'real_expression')
            }
        }

        self.assertDictEqual(
            expected_diagram_graph,
            diagram_graph
        )

    def test_diagram_commands_to_graph_succeeds_for_transformations_and_lines(self):
        # Setup
        load_a_id = 'load_a'
        ets_a_id = 'ets_a'
        coupling_id = 'coupling_a'
        load_ets_coupling = mock_coupling_factory(coupling_id, load_a_id, ets_a_id)
        couplings = [
            load_ets_coupling,
        ]

        diagram_commands_by_id = {
            load_a_id: [DiagramTransformation(
                model_name='some_load',
                model_type='load',
            )],
            ets_a_id: [DiagramTransformation(
                model_name='some_ets',
                model_type='ets',
            )],
            coupling_id: [
                DiagramTransformation(
                    model_name='some_real_expression',
                    model_type='real_expression',
                ),
                # create lines which connect these components
                DiagramLine(
                    a_name='some_load',
                    a_port='port_a',
                    b_name='some_ets',
                    b_port='port_b',
                ),
                DiagramLine(
                    a_name='some_real_expression',
                    a_port='y',
                    b_name='some_ets',
                    b_port='control_in'
                ),
            ]
        }

        # Act
        diagram_graph = Diagram._diagram_commands_to_graph(
            diagram_commands_by_id,
            couplings
        )

        # Assert
        # create expected nodes and their connections
        load_node = DiagramNode(load_a_id, 'some_load', 'load')
        ets_node = DiagramNode(ets_a_id, 'some_ets', 'ets')
        real_expression_node = DiagramNode(coupling_id, 'some_real_expression', 'real_expression')
        load_node.add_connection('port_a', ets_node, 'port_b')
        ets_node.add_connection('port_b', load_node, 'port_a')
        ets_node.add_connection('control_in', real_expression_node, 'y')
        real_expression_node.add_connection('y', ets_node, 'control_in')

        expected_diagram_graph = {
            load_a_id: {
                'some_load': load_node
            },
            ets_a_id: {
                'some_ets': ets_node
            },
            coupling_id: {
                'some_real_expression': real_expression_node
            }
        }

        self.assertDictEqual(
            expected_diagram_graph,
            diagram_graph
        )
