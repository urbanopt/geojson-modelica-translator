# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
import os

from jsonschema.validators import Draft202012Validator as LatestValidator


class Schemas(object):
    """
    Class to hold the various schemas
    """

    def __init__(self):
        """Load in the schemas"""
        self.schemas = {
            "building": None,
            "district_system": None,
            "electrical_connector": None,
            "electrical_junction": None,
            "region": None,
            "site": None,
            "thermal_connector": None,
            "thermal_junction": None,
        }

        for s in self.schemas.keys():
            path = os.path.join(
                os.path.dirname(__file__), "data/schemas/%s_properties.json" % s
            )
            with open(path, "r") as f:
                self.schemas[s] = json.load(f)

    def retrieve(self, name):
        """name of the schema to retrieve"""
        if self.schemas.get(name):
            return self.schemas[name]
        else:
            raise Exception("Schema for %s does not exist" % name)

    def validate(self, name, instance):
        """
        Validate an instance against a loaded schema

        :param name: str, name of the schema to validate against
        :param instance: dict, instance to validate
        :return:
        """
        results = []
        s = self.retrieve(name)
        v = LatestValidator(s)
        for error in sorted(v.iter_errors(instance), key=str):
            results.append(error.message)

        return results
