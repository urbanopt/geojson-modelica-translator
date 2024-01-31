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
        with pytest.raises(GeoJsonValidationError) as exc:
            UrbanOptGeoJson(fn)
        assert f"URBANopt GeoJSON file does not exist: {fn}" in str(exc.value)

    def test_valid_instance(self):
        """No exception should be raised when the geojson file is valid"""
        filename = self.data_dir / "geojson_1.json"
        UrbanOptGeoJson(filename)

    def test_validate(self):
        filename = self.data_dir / "geojson_1_invalid.json"
        with pytest.raises(GeoJsonValidationError) as ctx:
            UrbanOptGeoJson(filename)

        assert "is not valid under any of the given schemas" in str(ctx.value)
