# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from shutil import copyfile

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Lines.Lines import (
    DistributionLines
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Loads.capacitor import (
    Capacitor
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Loads.Inductive import (
    Inductive_load
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Sources.community_pv import (
    CommunityPV
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Sources.generators import (
    Generator
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Sources.grid import (
    Grid
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Sources.wind_turbines import (
    WindTurbine
)
from geojson_modelica_translator.modelica.GMT_Lib.Electrical.AC.ThreePhasesBalanced.Storage.battery import (
    Battery
)
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)
from geojson_modelica_translator.utils import linecount

PARENT_DIR = Path(__file__).parent
GMT_LIB_PATH = PARENT_DIR.parent.parent / 'geojson_modelica_translator' / 'modelica' / 'GMT_Lib'
COOLING_PLANT_PATH = GMT_LIB_PATH / 'DHC' / 'Components' / 'Plants' / 'Cooling'
MICROGRID_PARAMS = PARENT_DIR.parent / 'data_shared' / 'system_params_microgrid_example.json'

env = Environment(
    loader=FileSystemLoader(GMT_LIB_PATH),
    undefined=StrictUndefined,
    variable_start_string='{$',
    variable_end_string='$}'
)

COOLING_PLANT_PARAMS = {
    'chiller_performance': 'Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_York_YT_1055kW_5_96COP_Vanes',
    'plant_type': 'Buildings.Experimental.DHC.Plants.Cooling.ElectricChillerParallel',
    'delta_temp_approach': 3,
    'chw_mass_flow_nominal': 18.3,
    'chw_pressure_drop_nominal': 44800,
    'chiller_water_flow_minimum': 0.03,
    'cw_mass_flow_nominal': 34.7,
    'cw_pressure_drop_nominal': 46200,
    'fan_power': 4999,
    'chw_temp_setpoint': 281.15,
    'cooling_tower_pressure_drop_valve_nominal': 5999,
    'chw_pressure_drop_valve_nominal': 5999,
    'cw_pressure_drop_valve_nominal': 5999
}


def test_generate_cooling_plant(snapshot):
    # -- Setup
    template_path = (COOLING_PLANT_PATH / 'CoolingPlant.mot').relative_to(GMT_LIB_PATH)

    # -- Act
    actual = env.get_template(template_path.as_posix()).render(**COOLING_PLANT_PARAMS)

    # -- Assert
    assert actual == snapshot


def test_build_community_pv():
    # -- Setup

    package_output_dir = PARENT_DIR / 'output' / 'CommunityPV'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = CommunityPV(sys_params)
    cpv.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'PVPanels1.mo') > 20


@pytest.mark.simulation
def test_simulate_community_pv():
    # -- Setup

    package_output_dir = PARENT_DIR / 'output' / 'CommunityPV'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = CommunityPV(sys_params)
    cpv.build_from_template(package_output_dir)

    runner = ModelicaRunner()
    success, _ = runner.run_in_docker(package_output_dir / 'PVPanels0.mo')

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'PVPanels1.mo') > 20
    # Did the simulation run?
    assert success is True


def test_build_cooling_plant():
    # -- Setup
    template_path = (COOLING_PLANT_PATH / 'CoolingPlant.mot').relative_to(GMT_LIB_PATH)

    # -- Act
    output = env.get_template(template_path.as_posix()).render(**COOLING_PLANT_PARAMS)
    package_output_dir = PARENT_DIR / 'output' / 'Cooling'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    with open(package_output_dir / 'CoolingPlant.mo', 'w') as f:
        f.write(output)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'CoolingPlant.mo') > 20


@pytest.mark.simulation
def test_simulate_cooling_plant():
    # -- Setup
    template_path = (COOLING_PLANT_PATH / 'CoolingPlant.mot').relative_to(GMT_LIB_PATH)
    output = env.get_template(template_path.as_posix()).render(**COOLING_PLANT_PARAMS)
    package_output_dir = PARENT_DIR / 'output' / 'Cooling'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    with open(package_output_dir / 'CoolingPlant.mo', 'w') as f:
        f.write(output)

    # copy over the script
    copyfile(COOLING_PLANT_PATH / 'CoolingPlant.mos', package_output_dir / 'CoolingPlant.mos')

    # -- Act
    runner = ModelicaRunner()
    success, _ = runner.run_in_docker(package_output_dir / 'CoolingPlant.mos', package_output_dir, 'Cooling')

    # -- Assert
    assert success is True


def test_build_wind_turbine():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'WindTurbine'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = WindTurbine(sys_params)
    cpv.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'WindTurbine0.mo') > 20


@pytest.mark.simulation
def test_simulate_wind_turbine():
    # -- Setup

    package_output_dir = PARENT_DIR / 'output' / 'WindTurbine'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = WindTurbine(sys_params)
    cpv.build_from_template(package_output_dir)

    runner = ModelicaRunner()
    success, _ = runner.run_in_docker(package_output_dir / 'WindTurbine0.mo')

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'WindTurbine0.mo') > 20
    # Did the simulation run?
    assert success is True


def test_build_distribution_lines():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'DistributionLines'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = DistributionLines(sys_params)
    cpv.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'ACLine0.mo') > 20


@pytest.mark.simulation
def test_simulate_distribution_lines():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'DistributionLines'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cpv = DistributionLines(sys_params)
    cpv.build_from_template(package_output_dir)

    runner = ModelicaRunner()
    success, _ = runner.run_in_docker(package_output_dir / 'ACLine0.mo')

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'ACLine0.mo') > 20
    # Did the simulation run?
    assert success is True


def test_build_capacitor():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'Capacitor'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    cap = Capacitor(sys_params)
    cap.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'Capacitor0.mo') > 20


def test_build_battery():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'Battery'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    bat = Battery(sys_params)
    bat.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'AcBattery0.mo') > 20


def test_build_generator():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'Generator'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    gen = Generator(sys_params)
    gen.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'Generator0.mo') > 20


def test_build_grid():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'Grid'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    grid = Grid(sys_params)
    grid.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'Grid.mo') > 20


def test_build_inductive_load():
    # -- Setup
    package_output_dir = PARENT_DIR / 'output' / 'Inductive'
    package_output_dir.mkdir(parents=True, exist_ok=True)
    sys_params = SystemParameters(MICROGRID_PARAMS)

    # -- Act
    inductive = Inductive_load(sys_params)
    inductive.build_from_template(package_output_dir)

    # -- Assert
    # Did the mofile get created?
    assert linecount(package_output_dir / 'Inductive0.mo') > 20

# Keeping the code below because it may come back and this was a weird issue.
# @pytest.mark.simulation
# def test_stub_mbl_v9_with_not_msl_v4():
#     """Need to have a stub where mbl_v9 is selected that is simulatable (with
#     MSV V3.2) in order to not create a failed pytest command with exit code 5."""
#     assert False is not True
