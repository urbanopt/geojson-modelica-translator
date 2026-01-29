# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from jinja2 import Template

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.load_connectors.load_base import LoadBase
from tests.base_test_case import TestCaseBase


class TestModelConnectorBase(TestCaseBase):
    def setUp(self):
        project_name = "base_classes"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "spawn_geojson_ex1.json"
        self.gj = UrbanOptGeoJson(filename)

    def test_init(self):
        mc = LoadBase(None, self.gj.buildings[0])
        assert mc is not None

    def test_ft2_to_m2(self):
        assert LoadBase.ft2_to_m2(self, area_in_ft2=1000) == 92.936

    def test_template(self):
        mc = LoadBase(None, self.gj.buildings[0])

        with open(self.data_dir / "template_ex.tmpl") as f:
            template = Template(f.read())

        mc.run_template(template, self.output_dir / "template.out", file_name="test_123")
        assert mc is not None

        assert (self.output_dir / "template.out").exists()
        with open(self.output_dir / "template.out") as content_file:
            content = content_file.read()
            assert content == "test_123"
