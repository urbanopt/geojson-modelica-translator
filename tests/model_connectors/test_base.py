"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import os
import shutil
import unittest

from geojson_modelica_translator.model_connectors.load_connectors.load_base import \
    LoadBase as model_connector_base
from jinja2 import Template


class TestModelConnectorBase(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output', 'templates')
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

        os.makedirs(self.output_dir)

    def test_init(self):
        mc = model_connector_base(None)
        self.assertIsNotNone(mc)

    def test_ft2_to_m2(self):
        self.assertEqual(model_connector_base.ft2_to_m2(self, area_in_ft2=1000), 92.936)

    def test_template(self):
        mc = model_connector_base(None)

        with open(os.path.join(self.data_dir, 'template_ex.tmpl')) as f:
            template = Template(f.read())

        mc.run_template(template, os.path.join(self.output_dir, 'template.out'), file_name='test_123')
        self.assertIsNotNone(mc)

        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'template.out')))
        with open(os.path.join(self.output_dir, 'template.out'), 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, 'test_123')
