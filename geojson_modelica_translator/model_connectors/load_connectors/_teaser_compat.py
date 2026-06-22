# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

"""Compatibility workarounds for importing TEASER."""

from pathlib import Path

# TEASER 1.3.1 creates this directory during import using a racy
# exists-then-makedirs sequence. Ensure it exists before parallel processes
# import TEASER simultaneously.
Path.home().joinpath("TEASEROutput").mkdir(exist_ok=True)

from teaser.project import Project  # noqa: E402

__all__ = ["Project"]
