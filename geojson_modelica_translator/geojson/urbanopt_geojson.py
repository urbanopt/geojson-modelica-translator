# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
from pathlib import Path

import geojson
from jsonpath_ng.ext import parse

from geojson_modelica_translator.geojson.schemas import Schemas

_log = logging.getLogger(__name__)


class GeoJsonValidationError(Exception):
    pass


# TODO: Inherit from GeoJSON Feature class, move to its own file
class UrbanOptLoad:
    """An UrbanOptLoad is a container for holding Building-related data in a dictionary. This object
    does not do much work on the GeoJSON definition of the data at the moment, rather it creates
    an isolation layer between the GeoJSON data and the GMT.
    """

    def __init__(self, feature):
        self.feature = feature
        self.id = feature.get("properties", {}).get("id", None)

        # do some validation
        if self.id is None:
            raise GeoJsonValidationError("GeoJSON feature requires an ID property but value was null")

    def __str__(self):
        return f"ID: {self.id}"


class UrbanOptGeoJson:
    """Root class for parsing an URBANopt GeoJSON file. This class simply reads and parses
    URBANopt GeoJSON files.
    """

    def __init__(self, filename, building_ids=None, skip_validation=False):
        """Initialize the UrbanOptGeoJson object by reading the GeoJSON file

        :param filename: str, path to the GeoJSON file to parse
        :param building_ids: list[str | int] | None, optional, list of GeoJSON building
            IDs to parse from the file. If None or an empty list, parse all buildings.
        """
        if not Path(filename).exists():
            raise GeoJsonValidationError(f"URBANopt GeoJSON file does not exist: {filename}")

        with open(filename) as f:
            self.data = geojson.load(f)

        self.schemas = Schemas()

        errors = ""
        building_errors = {}
        self.buildings = []
        for feature in self.data.features:
            if feature["properties"]["type"] == "Building":
                building = UrbanOptLoad(feature)
                if not building_ids or building.id in building_ids:
                    # Ignore validation failures for features with 'detailed_model_filename' in the properties
                    # Buildings defined by an osm don't have all keys in geojson, therefore will always fail validation
                    if "detailed_model_filename" not in feature["properties"]:
                        errors = self.schemas.validate("building", building.feature.properties)

                    if errors and not skip_validation:
                        building_errors[building.id] = errors
                    else:
                        self.buildings.append(building)

        if building_errors:
            formatted_errors = ""
            for building_id, errors in building_errors.items():
                building_errors_bullets = "".join([f"\n    * {error}" for error in errors])
                formatted_errors += f"\n  ID {building_id}:{building_errors_bullets}"

            message = f"GeoJSON file is not valid:{formatted_errors}"
            raise GeoJsonValidationError(message)

        if not self.buildings:
            raise GeoJsonValidationError(f"No valid buildings found in GeoJSON file: {filename}")

    def get_feature_by_id(self, feature_id=None):
        """return geojson data for a specific feature (building, pipe, wire, junction, district system, etc).

        :param feature_id: string, id of the object to look up in the geojson file
        :return: dict, full feature data for the object with the given id
        """

        if feature_id is None:
            raise SystemExit("No id submitted. Please retry and include the appropriate id")

        for feature in self.data.features:
            if feature["properties"]["id"] == str(feature_id):
                return feature

    def get_feature(self, jsonpath):
        """Return the parameter(s) from a jsonpath.

        :param path: string, period delimited path of the data to retrieve
        :return: dict, full feature data for the object with the given id
        """

        if jsonpath is None or jsonpath == "":
            return None

        matches = parse(jsonpath).find(self.data)

        results = []
        for match in matches:
            results.append(match.value)

        if len(results) == 1:
            # If only one value, then return that value and not a list of values
            results = results[0]
        elif len(results) == 0:
            return print(f"No matches found for jsonpath {jsonpath}")

        # otherwise return the list of values
        return results
