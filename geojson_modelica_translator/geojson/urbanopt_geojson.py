# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import json
import logging
from pathlib import Path

import geojson
from jsonpath_ng.ext import parse

from geojson_modelica_translator.geojson.schemas import Schemas
from geojson_modelica_translator.geojson.urbanopt_load import GeoJsonValidationError, UrbanOptLoad

_log = logging.getLogger(__name__)


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

        self._filename = Path(filename).resolve()
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
                    # Do not attempt validation for features with 'detailed_model_filename' in the properties
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
        if feature_id not in self.data.features:
            raise KeyError(f"No matches found for id {feature_id}")

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
            raise KeyError(f"No matches found for jsonpath {jsonpath}")

        # otherwise return the list of values
        return results

    # TODO: test the following methods
    def get_building_paths(self, scenario_name: str) -> list[Path]:
        """Return a list of Path objects for the building GeoJSON files"""
        result = []
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building":
                building_path = self._filename.parent / "run" / scenario_name / feature["properties"]["id"]
                result.append(building_path)
                # result.append(Path(feature["properties"]["file"]))

        # verify that the paths exist
        for path in result:
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

        return result

    def get_building_ids(self) -> list:
        """Return a list of building names"""
        result = []
        for feature in self.data["features"]:
            if "type" in feature["properties"] and feature["properties"]["type"] == "Building":
                result.append(feature["properties"]["id"])
            elif "name" in feature["properties"] and feature["properties"]["name"] == "Site Origin":
                pass
            else:
                # need to implement a reasonable logger.
                pass
                # print(f"Feature does not have a type Building: {feature}")
                # print("Did you forget to call the `update_geojson_from_seed_data` method?")

        return result

    def get_building_names(self) -> list:
        """Return a list of building names. Typically this field is only used for visual display name only."""
        result = []
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building":
                result.append(feature["properties"]["name"])

        return result

    def get_buildings(self, ids: list[str] | None = None) -> list:
        """Return a list of all the properties of type Building"""
        result = []
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building" and (ids is None or feature["properties"]["id"] in ids):
                # TODO: eventually add a list of building ids to keep, for now it
                # will be all buildings.
                result.append(feature)

        return result

    def get_building_properties_by_id(self, building_id: str) -> dict:
        """Get the list of building ids in the GeoJSON file. The Building id is what
        is used in URBANopt as the identifier. It is common that this is used to name
        the building, more than the GeoJSON's building name field.

        Args:
            building_id (str): building id, this is the property.id values in the geojson's feature

        Returns:
            dict: building properties
        """
        result = {}
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building" and feature["properties"]["id"] == building_id:
                result = feature["properties"]

        return result

    def get_meters_for_building(self, building_id: str) -> list:
        """Return a list of meters for the building_id"""
        result = []
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building" and feature["properties"]["id"] == building_id:
                for meter in feature["properties"].get("meters", []):
                    result.append(meter["type"])

        if not result:
            _log.debug(f"No meters found for building {building_id}")

        return result

    def get_meter_readings_for_building(self, building_id: str, meter_type: str) -> list:
        """Return a list of meter readings for the building_id"""
        result = []
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building" and feature["properties"]["id"] == building_id:
                for meter in feature["properties"].get("meters", []):
                    if meter["type"] == meter_type:
                        result = meter["readings"]
        if not result:
            _log.debug(f"No meter readings found for building {building_id}")

        return result

    def get_monthly_readings(self, building_id: str, meter_type: str = "Electricity") -> list:
        """Return a list of monthly electricity consumption for the building_id"""
        result = []
        for feature in self.data["features"]:
            if (
                feature["properties"]["type"] == "Building"
                and feature["properties"]["id"] == building_id
                and meter_type == "Electricity"
            ):
                result = feature["properties"].get("monthly_electricity")

        if not result:
            _log.debug(f"No monthly readings found for building {building_id}")

        return result

    def set_property_on_building_id(
        self, building_id: str, property_name: str, property_value: str, overwrite=True
    ) -> None:
        """Set a property on a building_id.

        Note this method does not change the GeoJSON file, it only changes the in-memory data."""
        for feature in self.data["features"]:
            if (
                feature["properties"]["type"] == "Building"
                and feature["properties"]["id"] == building_id
                and (overwrite or property_name not in feature["properties"])
            ):
                feature["properties"][property_name] = property_value

    def get_property_by_building_id(self, building_id: str, property_name: str) -> str | None:
        """Get a property on a building_id"""
        for feature in self.data["features"]:
            if feature["properties"]["type"] == "Building" and feature["properties"]["id"] == building_id:
                return feature["properties"].get(property_name, None)
        return None

    def get_site_lat_lon(self) -> list | None:
        """Return the site's latitude and longitude

        Rounds to 6 decimal places, if the geojson file has more than 6 decimal places.
        Returns None if the site origin is not found."""
        for feature in self.data["features"]:
            if feature["properties"]["name"] == "Site Origin":
                # reverse the order of the coordinates
                return feature["geometry"]["coordinates"][::-1]
        _log.warning("Site Origin not found in GeoJSON file")
        return None

    def save(self) -> None:
        """Save the GeoJSON file"""
        self.save_as(self._filename)

    def save_as(self, filename: Path) -> None:
        """Save the GeoJSON file"""
        with open(filename, "w") as f:
            json.dump(self.data, f, indent=2)
