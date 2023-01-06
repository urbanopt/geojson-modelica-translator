# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

def strcat(value, append):
    return value + str(append)


ALL_CUSTOM_FILTERS = {
    'strcat': strcat
}
