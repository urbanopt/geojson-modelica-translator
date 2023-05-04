# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from shutil import rmtree

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.modelica.GMT_Lib.DHC.DHC_5G_waste_heat_GHX import (
    DHC5GWasteHeatAndGHX
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)
from geojson_modelica_translator.utils import linecount

PARENT_DIR = Path(__file__).parent
GMT_LIB_PATH = PARENT_DIR.parent.parent / 'geojson_modelica_translator' / 'modelica' / 'GMT_Lib'
DES_PARAMS = PARENT_DIR.parent / 'data_shared' / 'system_params_des_5g.json'

env = Environment(
    loader=FileSystemLoader(GMT_LIB_PATH),
    undefined=StrictUndefined,
    variable_start_string='{$',
    variable_end_string='$}'
)


def test_5G_des_waste_heat_and_ghx():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output'
    package_name = 'DES_5G'
    if (package_output_dir / package_name).exists():
        rmtree(package_output_dir / package_name)
    sys_params = SystemParameters(DES_PARAMS)

    # -- Act
    cpv = DHC5GWasteHeatAndGHX(sys_params)
    cpv.build_from_template(package_output_dir, 'DES_5G')

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / package_name / 'Districts' / 'district.mo') > 20

    # Test to make sure that a zero SWH peak is set to a minimum value.
    # Otherwise, Modelica will error out.
    with open(package_output_dir / package_name / 'Resources' / 'Data' / 'Districts' / '8' / 'B11.mos', 'r') as f:
        assert '#Peak water heating load = 7714 Watts' in f.read()
