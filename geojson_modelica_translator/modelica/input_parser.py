"""
****************************************************************************************************
:copyright (c) 2019 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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


class InputParser(object):
    """
    Class to read in Modelica files (.mo) and provide basic operations.
    """

    def __init__(self, modelica_filename):
        if not os.path.exists(modelica_filename):
            raise Exception(f'File does not exist {modelica_filename}')

        self.modelica_filename = modelica_filename
        self.init_vars()
        self.parse_mo()

    def init_vars(self):
        self.withins = []
        self.model = {'name': None, 'comment': None, 'objects': []}
        self.connections = []
        self.equations = []

    def parse_mo(self):
        # eventually move this over to use token-based assessment of the files. Here is a list of some of the tokens
        # TODO: strip all spacing and reconstruct on export
        tokens = ['within', 'block', 'algorithm', 'model', 'equation', 'protected', 'package',
                  'extends', 'initial equation', 'end']
        current_block = None
        obj_data = ''
        connect_data = ''
        with open(self.modelica_filename, 'r') as f:
            for index, l in enumerate(f.readlines()):
                if l.startswith('within'):
                    # these lines typically only have a single line, so just persist it
                    self.withins.append(l)
                    continue
                elif l.startswith('model'):
                    # get the model name and save
                    self.model['name'] = l.split(' ')[1].rstrip()
                    current_block = 'model'
                    continue
                elif l.startswith('equation'):
                    current_block = 'equation'
                    continue
                elif l.startswith('end'):
                    current_block = 'end'
                else:
                    # check if any other tokens are triggered and throw a 'not-supported' message
                    for t in tokens:
                        if l.startswith(t):
                            raise Exception(f'Found other token {t} that is not supported... cannot continue')

                # now store data that is in between these other blocks
                if current_block == 'model':
                    # grab the lines that are comments:
                    if not obj_data and l.strip().startswith('"') and l.strip().endswith('"'):
                        self.model['comment'] = l
                        continue

                    # determine if this is a new object or a new object (look for ';')
                    obj_data += l
                    if l.endswith(';\n'):
                        self.model['objects'].append(obj_data)
                        obj_data = ''
                elif current_block == 'equation':
                    if l.strip().startswith('connect'):
                        connect_data += l
                    elif connect_data and l.endswith(';\n'):
                        connect_data += l
                        self.connections.append(connect_data)
                        connect_data = ''
                    elif connect_data:
                        connect_data += l
                    else:
                        self.equations.append(l)
                elif current_block == 'end':
                    pass
                else:
                    # there is nothing to do here
                    pass

    def save(self):
        """
        Save the resulting file to the same file from which it was initialized

        :return:
        """
        self.save_as(self.modelica_filename)

    def save_as(self, new_filename):
        """
        Save the resulting file with a new filename

        :param new_filename:
        :return:
        """
        with open(new_filename, 'w') as f:
            f.write(self.serialize())

    def remove_object(self, obj_name):
        """
        Remove an object by a name. Can be any part of the object name.

        :param obj_name: string, object name to match
        :return:
        """
        index, obj = self.find_model_object(obj_name)
        if index is not None:
            del self.model['objects'][index]

    def find_model_object(self, obj_name):
        """
        Find a model object in the list of parsed objects
        :param obj_name: string, name (including the instance)
        :return: list, index and string of object
        """
        for index, o in enumerate(self.model['objects']):
            if obj_name in o:
                return index, self.model['objects'][index]

        return None, None

    def reload(self):
        """
        Reparse the data. This will remove any unsaved changes.
        """
        self.init_vars()
        self.parse_mo()

    def replace_model_string(self, model_name, model_instance, old_string, new_string):
        """
        Go through the models and find the model_name with a model_instance and change the value in the field to
        the new_value. This will replace the entire value of the model field.

        This will not work with arrays or lists (e.g., {...}, [...])

        :param model_name: string,
        :param model_instance: string,
        :param field: string,
        :param new_value: string,
        :return:
        """
        index, _model = self.find_model_object(f'{model_name} {model_instance}')
        if index is not None:
            self.model['objects'][index] = self.model['objects'][index].replace(old_string, new_string)

    def add_model_object(self, model_name, model_instance, data):
        """
        Add a new model object to the model

        :param model_name: string
        :param model_instance: string
        :param data: list of strings
        """
        str = f'  {model_name} {model_instance}\n'
        for d in data:
            str += f'    {d}\n'
        self.model['objects'].append(str)

    def add_connect(self, a, b, annotation):
        """
        Add a new connection of port a to port b. The annotation will be appended on a new line.

        :param a: string, port a
        :param b: string, port b
        :param annotation: string, description
        """
        self.connections.append(f'  connect({a}, {b})\n    {annotation};\n')

    def find_connect(self, port_a, port_b):
        """
        Find an existing connection that has port_a and/or port_b. If there are more than one, then it will only
        return the first.

        :param port_a:
        :param port_b:
        :return:
        """
        for index, c in enumerate(self.connections):
            if not port_a:
                raise Exception('Unable to replace string in connect if unknown port A')
            if not port_b:
                if f'({port_a}, ' in c:
                    return index, c
            if port_a and port_b:
                if f'({port_a}, {port_b})' in c:
                    return index, c

        return None, None

    def replace_connect_string(self, a, b, new_a, new_b, replace_all=False):
        """
        Replace content of the connect string with new_a and/or new_b

        :param a: string, existing port a
        :param b: string, existing port b
        :param new_a: string, new port (or none)
        :param new_b: string, new port b (or none
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

    def serialize(self):
        """
        Serialize the modelica object to a string with line feeds

        :return: string
        """
        str = ""
        for w in self.withins:
            str += w

        str += f"model {self.model['name']}\n"
        str += f"{self.model['comment']}"
        for o in self.model['objects']:
            for l in o:
                str += l

        str += 'equation\n'
        for c in self.connections:
            str += c

        for e in self.equations:
            str += e

        str += f"end {self.model['name']};\n"

        return str
