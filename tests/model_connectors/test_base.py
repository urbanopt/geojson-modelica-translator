# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os

from jinja2 import Template

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.load_connectors.load_base import \
    LoadBase as model_connector_base

from ..base_test_case import TestCaseBase


class TestModelConnectorBase(TestCaseBase):
    def setUp(self):
        project_name = "base_classes"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "spawn_geojson_ex1.json")
        self.gj = UrbanOptGeoJson(filename)

    def test_init(self):
        mc = model_connector_base(None, self.gj.buildings[0])
        self.assertIsNotNone(mc)

    def test_ft2_to_m2(self):
        self.assertEqual(model_connector_base.ft2_to_m2(self, area_in_ft2=1000), 92.936)

    def test_template(self):
        mc = model_connector_base(None, self.gj.buildings[0])

        with open(os.path.join(self.data_dir, 'template_ex.tmpl')) as f:
            template = Template(f.read())

        mc.run_template(template, os.path.join(self.output_dir, 'template.out'), file_name='test_123')
        self.assertIsNotNone(mc)

        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'template.out')))
        with open(os.path.join(self.output_dir, 'template.out'), 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, 'test_123')
