import re
from collections import namedtuple

DiagramTransformation = namedtuple('DiagramTransformation', ['model_name', 'model_type'])
DiagramLine = namedtuple('DiagramLine', ['a_name', 'a_port', 'b_name', 'b_port'])

JINJA_EXPRESSION_REGEX = re.compile(r'{{\s*(.*?)\s*}}')


def parse_diagram_command(str_cmd):
    """Returns a diagram command or None if it's not a diagram command"""
    cmd_args_list = str_cmd.split('.')
    if len(cmd_args_list) <= 1:
        return None

    context = cmd_args_list.pop(0)
    if context != 'diagram':
        return None

    command = cmd_args_list.pop(0)
    if command == 'transformation':
        if len(cmd_args_list) != 2:
            raise Exception(f'Invalid diagram templating command: "transformation" expects 2 arguments but got {cmd_args_list}')
        return DiagramTransformation(*cmd_args_list)
    elif command == 'line':
        if len(cmd_args_list) != 4:
            raise Exception(f'Invalid diagram templating command: "line" expects 4 arguments but got {cmd_args_list}')
        return DiagramLine(*cmd_args_list)
    else:
        raise Exception(f'Invalid diagram templating command "{command}"')


def parse_diagram_commands(template_contents):
    """Returns a list of diagram commands parsed from the template modelica contents
    i.e. it will find any instances of {{ diagram.<cmd>.* }} in the template

    :param template_contents: str, modelica template code
    :return: list[DiagramCommand]
    """
    matches = JINJA_EXPRESSION_REGEX.finditer(template_contents)

    commands = []
    for match in matches:
        group = match.group(1)
        diagram_command = parse_diagram_command(group)
        if diagram_command is None:
            continue

        commands.append(diagram_command)

    return commands
