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
from geojson_modelica_translator.model_connectors.couplings.utils import (
    DiagramLine,
    DiagramTransformation,
    parse_diagram_commands
)

from ..base_test_case import TestCaseBase


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
