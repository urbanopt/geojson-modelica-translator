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
from pathlib import Path
from shutil import copyfile

import pytest
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from jinja2 import Environment, FileSystemLoader, StrictUndefined

PARENT_DIR = Path(__file__).parent
GMT_LIB_PATH = PARENT_DIR.parent.parent / 'geojson_modelica_translator' / 'modelica' / 'GMT_Lib'
COOLING_PLANT_PATH = GMT_LIB_PATH / 'DHC' / 'Components' / 'CentralPlant' / 'Cooling'

env = Environment(
    loader=FileSystemLoader(GMT_LIB_PATH),
    undefined=StrictUndefined,
    variable_start_string='{$',
    variable_end_string='$}'
)

COOLING_PLANT_PARAMS = {
    'chiller_performance':  'Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_York_YT_1055kW_5_96COP_Vanes',
    'plant_type': 'Buildings.Experimental.DHC.CentralPlants.Cooling.Plant',
    'delta_temp_approach': 3,
    'chw_mass_flow_nominal':  18.3,
    'chw_pressure_drop_nominal': 44800,
    'chiller_water_flow_minimum': 0.03,
    'cw_mass_flow_nominal':  34.7,
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
    actual = env.get_template(str(template_path)).render(**COOLING_PLANT_PARAMS)

    # -- Assert
    assert actual == snapshot


@pytest.mark.mbl_v8
@pytest.mark.simulation
def test_simulate_cooling_plant():
    # -- Setup
    template_path = (COOLING_PLANT_PATH / 'CoolingPlant.mot').relative_to(GMT_LIB_PATH)
    output = env.get_template(str(template_path)).render(**COOLING_PLANT_PARAMS)
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
