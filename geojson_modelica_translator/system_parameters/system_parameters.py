"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import json
import os

from jsonschema.validators import _LATEST_VERSION as LatestValidator


class SystemParameters(object):
    """
    Object to hold the system parameter data (and schema).
    """

    def __init__(self, filename=None):
        """
        Read in the system design parameter file

        :param filename: string, (optional) path to file to load
        """
        # load the schema for validation
        self.schema = json.load(
            open(os.path.join(os.path.dirname(__file__), "schema.json"), "r")
        )
        self.data = {}

        if filename:
            if os.path.exists(filename):
                self.data = json.load(open(filename, "r"))
            else:
                raise Exception(
                    f"System design parameters file does not exist: {filename}"
                )

            errors = self.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

    @classmethod
    def loadd(cls, d, validate_on_load=True):
        """
        Create a system parameters instance from a dictionary
        :param d: dict, system parameter data

        :return: object, SystemParameters
        """
        sp = cls()
        sp.data = d

        if validate_on_load:
            errors = sp.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

        return sp

    def get_param(self, path, data=None, default=None):
        """
        return the parameter(s) from the path. This is a recursive function.

        :param path: string, period delimeted path of the data to retrieve
        :param data: dict, (optional) the data to parse
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """
        # If this is the first entry into the method, then set the data to the
        if data is None:
            data = self.data

        paths = path.split(".")
        check_path = paths.pop(0)
        if check_path == "":
            # no path passed
            return default
        else:
            value = data.get(check_path, None)
            if value is None:
                return default

            if len(paths) == 0:
                return value
            else:
                return self.get_param(".".join(paths), data=value, default=default)

    def get_param_by_building_id(self, building_id, path, default=None):
        """
        return a parameter for a specific building_id. This is similar to get_param but allows the user
        to constrain the data based on the building type.

        :param building_id: string, id of the building to look up in the custom section of the system parameters
        :param path: string, period delimeted path of the data to retrieve
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """

        # TODO: return the default value if the building ID is not defined
        for b in self.data.get("buildings", {}).get("custom", {}):
            if b.get("geojson_id", None) == building_id:
                # print(f"Building found for {building_id}")
                return self.get_param(path, b, default=default)

        return None

    def validate(self):
        """
        Validate an instance against a loaded schema

        :param instance: dict, json instance to validate
        :return:
        """
        results = []
        v = LatestValidator(self.schema)
        for error in sorted(v.iter_errors(self.data), key=str):
            results.append(error.message)

        return results
