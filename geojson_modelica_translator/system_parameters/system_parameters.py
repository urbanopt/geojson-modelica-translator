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

from jsonpath_ng.ext import parse
from jsonschema.validators import _LATEST_VERSION as LatestValidator


class SystemParameters(object):
    """
    Object to hold the system parameter data (and schema).
    """

    PATH_ELEMENTS = [
        {"json_path": "$.buildings.*[?load_model=Spawn].load_model_parameters.spawn.idf_filename"},
        {"json_path": "$.buildings.*[?load_model=Spawn].load_model_parameters.spawn.epw_filename"},
        {"json_path": "$.buildings.*[?load_model=Spawn].load_model_parameters.spawn.mos_weather_filename"},
        {"json_path": "$.buildings.*[?load_model=time_series].load_model_parameters.time_series.filepath"}
    ]

    def __init__(self, filename=None):
        """
        Read in the system design parameter file

        :param filename: string, (optional) path to file to load
        """
        # load the schema for validation
        with open(os.path.join(os.path.dirname(__file__), "schema.json"), "r") as f:
            self.schema = json.load(f)
        self.data = {}
        self.filename = filename

        if self.filename:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as f:
                    self.data = json.load(f)
            else:
                raise Exception(f"System design parameters file does not exist: {self.filename}")

            errors = self.validate()
            if len(errors) != 0:
                raise Exception(f"Invalid system parameter file. Errors: {errors}")

            self.resolve_paths()
            # self.resolve_defaults()

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

    def resolve_paths(self):
        """Resolve the paths in the file to be absolute if they were defined as relative. This method uses
        the JSONPath (with ext) to find if the value exists in the self.data object. If so, it then uses
        the set_param which navigates the JSON tree to set the value as needed."""
        filepath = os.path.abspath(os.path.dirname(self.filename))

        for pe in self.PATH_ELEMENTS:
            matches = parse(pe["json_path"]).find(self.data)
            for index, match in enumerate(matches):
                # print(f"Index {index} to update match {match.path} | {match.value} | {match.context}")
                new_path = os.path.join(filepath, match.value)
                parse(str(match.full_path)).update(self.data, new_path)

    # def resolve_defaults(self):
    #     """This method will expand the default data blocks into all the subsequent custom sections. If the value is
    #     specificed in the custom block then that will be used, otherwise the default value will be replaced"""
    #     pass

    def get_default(self, jsonpath, default=None):
        """Return either the default in the system parameter file, or the specified default.

        :param jsonpath: string, raw jsonpath to what parameter was being requested
        :param default: variant, default value
        :return: value
        """
        schema_default = self.get_param(jsonpath, impute_default=False)
        return schema_default or default

    def get_param(self, jsonpath, data=None, default=None, impute_default=True):
        """Return the parameter(s) from a jsonpath. If the default is not specified, then will attempt to read the
        default from the "default" section of the file. If there is no default there, then it will use the value
        specified as the argument. It is not recommended to use the argument default as those values will not be
        configurable. Argument-based defaults should be used sparingly.

        :param path: string, period delimited path of the data to retrieve
        :param data: dict, (optional) the data to parse
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """
        if jsonpath is None or jsonpath == "":
            return None

        # If this is the first entry into the method, then set the data to the
        data = data or self.data
        matches = parse(jsonpath).find(data)

        default_value = default
        if impute_default:
            default_value = self.get_default(jsonpath, default)

        results = []
        for index, match in enumerate(matches):
            # print(f"Index {index} to update match {match.path} | {match.value} | {match.context}")
            if match.value is None:
                results.append(default_value)
            else:
                results.append(match.value)

        if len(results) == 1:
            # If only one value, then return that value and not a list of values
            results = results[0]
        elif len(results) == 0:
            return default_value

        # otherwise return the list of values
        return results

    def get_param_by_building_id(self, building_id, jsonpath, default=None):
        """
        return a parameter for a specific building_id. This is similar to get_param but allows the user
        to constrain the data based on the building id.

        :param building_id: string, id of the building to look up in the custom section of the system parameters
        :param jsonpath: string, jsonpath formatted string to return
        :param default: variant, (optional) value to return if can't find the result
        :return: variant, the value from the data
        """

        # This will get reworked after moving to jsonpath. but for now, hack in the default. First return the default
        # dict from the system parameter file.
        # Grab first the default data block, then find the path in the default data block.
        # "building.default" might need to reconsider, as it is fixed for flake8 currently.
        default_data = self.get_param("$.buildings.default", impute_default=False)
        schema_default = self.get_param(jsonpath, default_data, impute_default=False)
        default = schema_default or default
        for b in self.data.get("buildings", {}).get("custom", {}):
            if b.get("geojson_id", None) == building_id:
                return self.get_param(jsonpath, b, default=default)
        else:
            # if there is no matching building_id, then return the default data.
            # This may come back to bite us. If the user mistypes the building id, then they may not
            # realize that they are grabbing the default data
            return default

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
