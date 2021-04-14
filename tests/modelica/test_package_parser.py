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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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
import unittest

from geojson_modelica_translator.modelica.input_parser import PackageParser


class PackageParserTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_new_from_template(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'new_model_name', ["model_a", "model_b"], within="SomeWithin"
        )
        package.save()

        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'package.mo')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'package.order')))

        # check for strings in files
        with open(os.path.join(self.output_dir, 'package.mo')) as f:
            file_data = f.read()
            self.assertTrue('within SomeWithin;' in file_data, 'Incorrect within clause')
            self.assertTrue('package new_model_name' in file_data, 'Incorrect package definition')
            self.assertTrue('end new_model_name;' in file_data, 'Incorrect package ending')

        with open(os.path.join(self.output_dir, 'package.order')) as f:
            self.assertTrue('model_a\nmodel_b' in f.read(), 'Incorrect package order')

    def test_round_trip(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'another_model', ["model_x", "model_y"], within="DifferentWithin"
        )
        package.save()

        # Read in the package
        package = PackageParser(self.output_dir)
        self.assertListEqual(package.order, ["model_x", "model_y"])

    def test_rename_model(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'rename_model', ["model_1", "model_2"], within="RenameWithin"
        )
        package.save()

        package.rename_model('model_1', 'my_super_new_model')
        self.assertEqual(len(package.order), 2)
        self.assertIn('my_super_new_model', package.order)

    def test_add_model(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'so_many_models', ["model_beta", "model_gamma"], within="SoMany"
        )
        package.save()

        package.add_model('model_delta')
        package.add_model('model_alpha', 0)
        self.assertEqual(len(package.order), 4)
        self.assertListEqual(['model_alpha', 'model_beta', 'model_gamma', 'model_delta'], package.order)
