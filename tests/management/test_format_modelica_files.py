# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import re
import shutil
import unittest

import pytest

from management.format_modelica_files import (
    SKIP_FILES,
    TEMPLATE_FILES,
    preprocess_and_format
)


class FormatModelicaFilesTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    @pytest.mark.skipif(shutil.which("modelicafmt") is None, reason="Skipping")
    def test_no_meaningful_diff_when_formatting_mot_files(self):
        """After applying formatter to .mot (Jinja) files, we expect the only differences to be in whitespace"""
        for file_ in TEMPLATE_FILES:
            outfilepath = os.path.join(self.output_dir, file_.name)

            if file_.suffix != ".mot" or file_.name in SKIP_FILES:
                continue

            preprocess_and_format(str(file_), outfilepath)

            # strip whitespace from file contents and assert they're equal
            with open(file_, 'r') as orig, open(outfilepath, 'r') as new:
                orig_stripped = re.sub(r'\s', '', orig.read())
                new_stripped = re.sub(r'\s', '', new.read())
                self.assertEqual(orig_stripped, new_stripped,
                                 f'Original and formatted files for {file_} should have the same content')
