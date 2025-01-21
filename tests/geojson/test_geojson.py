# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from unittest import TestCase

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import GeoJsonValidationError, UrbanOptGeoJson


class GeoJSONTest(TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        if not self.output_dir.exists():
            self.output_dir.mkdir(exist_ok=True)

    def test_load_geojson(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        assert json.data is not None
        assert len(json.data.features) == 4

    def test_missing_file(self):
        fn = "non-existent-path"
        with pytest.raises(GeoJsonValidationError, match=f"URBANopt GeoJSON file does not exist: {fn}"):
            UrbanOptGeoJson(fn)

    def test_valid_instance(self):
        """No exception should be raised when the geojson file is valid"""
        filename = self.data_dir / "geojson_1.json"
        assert UrbanOptGeoJson(filename)

    def test_validate(self):
        filename = self.data_dir / "geojson_1_invalid.json"
        with pytest.raises(GeoJsonValidationError, match="is not valid under any of the given schemas"):
            UrbanOptGeoJson(filename)

    def test_get_all_features(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        feature_properties = json.get_feature("$.features.[*].properties")
        assert len(feature_properties) == 4
        # Check that the first feature has the expected properties
        assert feature_properties[0]["floor_height"] == 9

    def test_get_feature(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        feature = json.get_feature("$.features[1]")
        assert feature["properties"]["floor_height"] == 3

    def test_get_feature_invalid(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        with pytest.raises(KeyError, match="No matches found"):
            json.get_feature("$.features[4]")

    def test_get_feature_by_id(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        feature = json.get_feature_by_id("5a7229e737f4de77124f946d")
        assert feature["properties"]["footprint_area"] == 8612

    def test_get_feature_by_id_invalid(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        with pytest.raises(KeyError, match="No matches found"):
            json.get_feature_by_id("non-existent-id")

    def test_get_feature_by_id_missing(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        with pytest.raises(SystemExit):
            json.get_feature_by_id()

    def test_get_building_paths(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        building_paths = json.get_building_paths(scenario_name="baseline_test")
        assert len(building_paths) == 3
        # Check that the building paths end with the dir of the building_id
        assert building_paths[0].stem == "5a6b99ec37f4de7f94020090"
        assert building_paths[1].stem == "5a72287837f4de77124f946a"
        assert building_paths[2].stem == "5a7229e737f4de77124f946d"
        # Check that the correct error is raised if the path doesn't exist
        with pytest.raises(FileNotFoundError, match="File not found"):
            json.get_building_paths(scenario_name="baseline")

    def test_get_building_ids(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        building_names = json.get_building_names()
        assert len(building_names) == 3
        assert building_names[0] == "Medium Office"

    def test_get_buildings(self):
        filename = self.data_dir / "geojson_1.json"
        json = UrbanOptGeoJson(filename)
        buildings = json.get_buildings(ids=None)
        assert len(buildings) == 3
        assert buildings[3]["properties"]["floor_area"] == 34448
