# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path


def strcat(value, append):
    return value + str(append)


def basename(value):
    return Path(value).name


ALL_CUSTOM_FILTERS = {"strcat": strcat, "basename": basename}
