import re
from collections import deque, namedtuple

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


def find_path_bfs(matrix, start_row, start_col, end_row, end_col):
    """Find path from start to end in the matrix. Matrix items that are None are
    considered "empty" and traversable. Raises an exception if no path is found.

    :param matrix: list[list[]]
    :param start_row: int
    :param start_col: int
    :param end_row: int
    :param end_col: int
    :return: list, list of (row, col) tuples
    """
    start = (start_row, start_col)
    finish = (end_row, end_col)

    queue = deque([([], start)])
    visited = []

    def visitable(pos):
        return (
            # must be valid matrix position
            pos[0] >= 0
            and pos[0] < len(matrix)
            and pos[1] >= 0
            and pos[1] < len(matrix[0])
            # must be empty or the finish
            and (matrix[pos[0]][pos[1]] is None or pos == finish)
            # must not be visited
            and pos not in visited
        )

    def get_neighbors(pos):
        north = (pos[0] - 1, pos[1])
        south = (pos[0] + 1, pos[1])
        east = (pos[0], pos[1] - 1)
        west = (pos[0], pos[1] + 1)
        neighbors = [north, south, east, west]
        return [direction for direction in neighbors if visitable(direction)]

    while queue:
        path, current = queue.popleft()

        if current == finish:
            return path
        if current in visited:
            continue

        visited.append(current)

        for neighbor in get_neighbors(current):
            queue.append((path + [neighbor], neighbor))

    # failed to find a path
    raise Exception(f'Failed to find path from {start} to {finish}')
