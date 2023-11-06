# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
from pathlib import Path
from typing import Any, List, Tuple, Union


# TODO: This needs to be removed. It is not used anywhere in the codebase.
class InputParser(object):
    """Class to read in Modelica files (.mo) and provide basic operations.

    This class is not recommended to be used and ModelicaBuilder should be used
    instead which is syntax-aware of the Modelica language.
    """

    def __init__(self, modelica_filename: Union[str, Path]) -> None:
        """Initialize the class with the modelica file to parse

        Args:
            modelica_filename (Union[str, Path]): Path to the modelica file (.mo) to parse

        Raises:
            Exception: SyntaxError, more than one within
            Exception: SyntaxError, unknown token

        """
        if not os.path.exists(modelica_filename):
            raise Exception(f"Modelica file does not exist: {modelica_filename}")

        self.modelica_filename = modelica_filename
        self.init_vars()
        self.parse_mo()

    def init_vars(self):
        self.within = None
        self.model = {"name": None, "comment": None, "objects": []}
        self.connections = []
        self.equations = []

    def parse_mo(self):
        """Parse the input if it is a .mo file. This will populate the within, model, connections, and equations
        along with various other tokens. This is a very basic parser and will not work for all cases.

        # TODO: move over to token-based parsing and assessment of the files.
        # TODO: strip all spacing and reconstruct on export

        Raises:
            Exception: General exception Exception("More than one 'within' lines found")
            Exception: _description_
        """
        tokens = [
            "within",
            "block",
            "algorithm",
            "model",
            "equation",
            "protected",
            "package",
            "extends",
            "initial equation",
            "end",
        ]
        current_block = None
        obj_data = ""
        connect_data = ""
        with open(self.modelica_filename, "r") as f:
            for line in f.readlines():
                if line == "\n":
                    # Skip blank lines (for now?
                    continue
                elif line.startswith("within"):
                    # these lines typically only have a single line, so just persist it
                    if not self.within:
                        # remove the line feed and the trailing semicolon
                        self.within = line.split(" ")[1].rstrip().replace(";", "")
                    else:
                        raise SyntaxError("More than one 'within' lines found")
                    continue
                elif line.startswith("model"):
                    # get the model name and save
                    self.model["name"] = line.split(" ")[1].rstrip()
                    current_block = "model"
                    continue
                elif line.startswith("equation"):
                    current_block = "equation"
                    continue
                elif line.startswith("end"):
                    current_block = "end"
                else:
                    # check if any other tokens are triggered and throw a 'not-supported' message
                    for t in tokens:
                        if line.startswith(t):
                            raise SyntaxError(
                                f"Found other token '{t}' in '{self.modelica_filename}' that is not supported... \
                                cannot continue"
                            )

                # now store data that is in between these other blocks
                if current_block == "model":
                    # grab the lines that are comments:
                    if (
                        not obj_data
                        and line.strip().startswith('"')
                        and line.strip().endswith('"')
                    ):
                        self.model["comment"] = line.rstrip()
                        continue

                    # determine if this is a new object or a new object (look for ';')
                    obj_data += line
                    if line.endswith(";\n"):
                        self.model["objects"].append(obj_data)
                        obj_data = ""
                elif current_block == "equation":
                    if line.strip().startswith("connect"):
                        connect_data += line
                    elif connect_data and line.endswith(";\n"):
                        connect_data += line
                        self.connections.append(connect_data)
                        connect_data = ""
                    elif connect_data:
                        connect_data += line
                    else:
                        self.equations.append(line)
                elif current_block == "end":
                    pass
                else:
                    # there is nothing to do here
                    pass

    def save(self) -> None:
        """Save the resulting file to the same file from which it was initialized
        """
        return self.save_as(self.modelica_filename)

    def save_as(self, new_filename: Union[str, Path]) -> None:
        """Save the resulting file with a new filename

        Args:
            new_filename (Union[str, Path]): name of the new file to save as
        """
        with open(new_filename, "w") as f:
            f.write(self.serialize())

    def remove_object(self, obj_name: str) -> None:
        """Remove an object by a name. Can be any part of the object name.

        Args:
            obj_name (str): object name to match
        """
        index, _ = self.find_model_object(obj_name)
        if index is not None:
            del self.model["objects"][index]

    def replace_within_string(self, new_string: str) -> None:
        """Replacement of the path portion of the within string

        Args:
            new_string (str): what to replace the existing within string with.
        """
        self.within = new_string

    def find_model_object(self, obj_name: str) -> Tuple[Union[int, None], Union[str, None]]:
        """Find a model object in the list of parsed objects

        Args:
            obj_name (str): name (including the instance)

        Returns:
            Tuple[Union[int, None], Union[str, None]]: index and string of object
        """
        for index, o in enumerate(self.model["objects"]):
            if obj_name in o:
                return index, self.model["objects"][index]

        return None, None

    def reload(self):
        """Reparse the data. This will remove any unsaved changes.
        """
        self.init_vars()
        self.parse_mo()

    def replace_model_string(self, model_name: str, model_instance: str, old_string: str, new_string: str):
        """Go through the models and find the model_name with a model_instance and change the value in the field to
        the new_value. This will replace the entire value of the model field.

        This will not work with arrays or lists (e.g., {...}, [...])

        Args:
            model_name (str): name of the model
            model_instance (str): instance of the model
            old_string (str): name of the old string to replace
            new_string (str): new string
        """
        index, _ = self.find_model_object(f"{model_name} {model_instance}")
        if index is not None:
            self.model["objects"][index] = self.model["objects"][index].replace(
                old_string, new_string
            )

    def add_model_object(self, model_name: str, model_instance: str, data: List[str]) -> None:
        """Add a new model object to the model

        Args:
            model_name (str): name of the model
            model_instance (str): model instance name
            data (List[str]): list of data to add
        """
        str = f"  {model_name} {model_instance}\n"
        for d in data:
            str += f"    {d}\n"
        self.model["objects"].append(str)

    def add_parameter(self, var_type: str, var_name: str, value: Any, description: str) -> None:
        """Add a new parameter. Will be prepended to the top of the models list

        Args:
            var_type (str): type of Modelica variable, Real, Integer, String, Modelica.Units.SI.Area, etc.
            var_name (str): name of the variable. Note that this does not check for conflicts.
            value (any): value to set the variable name to.
            description (str): description of the parameter
        """
        # is the value is a string, then wrap in quotes
        if isinstance(value, str):
            value = f'"{value}"'

        # parameter Real fraLat= 0.8 "Fraction latent of sensible persons load = 0.8 for home, 1.25 for office.";
        new_str = f"  parameter {var_type} {var_name}={value} \"{description}\";\n"
        self.model["objects"].insert(0, new_str)

    def add_connect(self, a: str, b: str, annotation: str) -> None:
        """Add a new connection of port a to port b. The annotation will be appended on a new line.

        Args:
            a (str): port a
            b (str): port b
            annotation (str): description
        """
        self.connections.append(f"  connect({a}, {b})\n    {annotation};\n")

    def find_connect(self, port_a: str, port_b: str) -> Tuple[Union[int, None], Union[str, None]]:
        """Find an existing connection that has port_a and/or port_b. If there are more than one, then it will only
        return the first.

        Args:
            port_a (str): port a
            port_b (str): port b

        Raises:
            Exception: could not find the connection

        Returns:
            Tuple[Union[int, None], Union[str, None]]: index and connection tuple
        """
        for index, c in enumerate(self.connections):
            if not port_a:
                raise Exception("Unable to replace string in connect if unknown port A")
            if not port_b:
                if f"({port_a}, " in c:
                    return index, c
            if port_a and port_b:
                if f"({port_a}, {port_b})" in c:
                    return index, c

        return None, None

    def replace_connect_string(self, a: str, b: str, new_a: Union[str, None], new_b: Union[str, None], replace_all: bool = False) -> None:
        """Replace content of the connect string with new_a and/or new_b

        Args:
            a (str): existing port a
            b (str): existing port b
            new_a (str): new port (or none)
            new_b (str): new port b (or none)
            replace_all (bool, optional):  allow replacement of all strings. Defaults to False.
        """
        # find the connection that matches a, b
        index, c = self.find_connect(a, b)
        while index:
            if index:
                if new_a:
                    self.connections[index] = self.connections[index].replace(a, new_a)
                if new_b:
                    self.connections[index] = self.connections[index].replace(b, new_b)

            if not replace_all:
                break
            else:
                index, c = self.find_connect(a, b)

    def remove_connect_string(self, a: str, b: str) -> None:
        """Remove a connection string that matches the a, b.

        Args:
            a (str): existing port a
            b (str): existing port b
        """

        # find the connection that matches a, b
        index, _ = self.find_connect(a, b)
        if index:
            del self.connections[index]

    def serialize(self) -> str:
        """Serialize the modelica object to a string with line feeds

        Returns:
            str: string representation of the data
        """
        str = f"within {self.within};\n"
        str += f"model {self.model['name']}\n"
        str += f"{self.model['comment']}\n\n"
        for o in self.model["objects"]:
            for lx in o:
                str += lx
        str += "equation\n"
        for c in self.connections:
            str += c
        for e in self.equations:
            str += e
        str += f"end {self.model['name']};\n"
        return str
