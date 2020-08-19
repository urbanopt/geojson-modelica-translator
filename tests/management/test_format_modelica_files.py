"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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
import re
import shutil
import unittest

from management.format_modelica_files import preprocess_and_format


class FormatModelicaFilesTest(unittest.TestCase):
    def setUp(self):
        self.template_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'geojson_modelica_translator', 'model_connectors', 'templates'
        )
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def test_no_meaningful_diff_when_formatting_mot_files(self):
        """After applying formatter to .mot (Jinja) files, we expect the only differences to be in whitespace"""
        for file_ in os.listdir(self.template_dir):
            filepath = os.path.join(self.template_dir, file_)
            outfilepath = os.path.join(self.output_dir, file_)

            if not file_.endswith(".mot"):
                continue

            preprocess_and_format(filepath, outfilepath)

            # strip whitespace from file contents and assert they're equal
            with open(filepath, 'r') as orig, open(outfilepath, 'r') as new:
                orig_stripped = re.sub(r'\s', '', orig.read())
                new_stripped = re.sub(r'\s', '', new.read())
                self.assertEqual(orig_stripped, new_stripped,
                                 'Original and formatted files should have the same content')
