# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import re
import tempfile
import unittest
from pathlib import Path
from shutil import which

import pytest

from management.format_modelica_files import SKIP_FILES, TEMPLATE_FILES, preprocess_and_format


class FormatModelicaFilesTest(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.output_dir = Path(self._temporary_directory.name)

    def tearDown(self):
        self._temporary_directory.cleanup()

    @pytest.mark.skipif(which("modelicafmt") is None, reason="Modelica formatter is not installed. Skipping.")
    def test_no_meaningful_diff_when_formatting_mot_files(self):
        """After applying formatter to .mot (Jinja) files, we expect the only differences to be in whitespace"""
        for file_ in TEMPLATE_FILES:
            outfilepath = self.output_dir / file_.name

            if file_.suffix != ".mot" or file_.name in SKIP_FILES:
                continue

            preprocess_and_format(str(file_), outfilepath)

            # strip whitespace from file contents and assert they're equal
            with open(file_) as orig, open(outfilepath) as new:
                orig_stripped = re.sub(r"\s", "", orig.read())
                new_stripped = re.sub(r"\s", "", new.read())
                assert orig_stripped == new_stripped, (
                    f"Original and formatted files for {file_} should have the same content"
                )
