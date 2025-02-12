# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
from pathlib import Path

from jsonschema.validators import Draft202012Validator as LatestValidator


class Schemas:
    """Class to hold the various schemas"""

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

        for s in self.schemas:
            path = Path(__file__).parent / "data" / "schemas" / f"{s}_properties.json"
            with open(path) as f:
                self.schemas[s] = json.load(f)

    def retrieve(self, name):
        """Name of the schema to retrieve"""
        if self.schemas.get(name):
            return self.schemas[name]
        else:
            raise NameError(f"Schema for {name} does not exist")

    def validate(self, name, instance):
        """Validate an instance against a loaded schema

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
