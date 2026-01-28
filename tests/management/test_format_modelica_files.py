# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import re
import shutil
import unittest
from pathlib import Path

import pytest

from management.format_modelica_files import SKIP_FILES, TEMPLATE_FILES, preprocess_and_format


class FormatModelicaFilesTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(__file__).parent / "output"
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)

    @pytest.mark.skipif(shutil.which("modelicafmt") is None, reason="Modelica formatter is not installed. Skipping.")
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
