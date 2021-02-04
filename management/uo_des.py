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


from pathlib import Path

import click
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


@click.group()
def cli():
    """URBANopt District Energy Systems"""
    pass


@cli.command()
@click.option(
    '-p',
    '--sys_param_filename',
    help='Name of systems parameters file to create. Include ".json" in the name.',
    required=True
)
@click.option(
    "-s",
    "--scenario_dir",
    help="Path to an urbanopt scenario, probably in the 'run' folder of your UO SDK project directory.",
    required=True
)
@click.option(
    "-f",
    "--feature_file",
    help="Path to urbanopt sdk FeatureFile, probably in the root UO SDK project directory.",
    required=True
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help="If a file already exists with the sys_param_filename, overwrite it.",
    default=False
)
@click.option(
    "-m",
    "--model",
    help="Selet the model type you're using. Available options: time_series",
    default='time_series',
    required=True
)
def sys_param(model, sys_param_filename, scenario_dir, feature_file, overwrite):
    """Create system parameters file using uo_sdk output"""
    SystemParameters.csv_to_sys_param(
        model_type=model,
        sys_param_filename=Path(sys_param_filename),
        scenario_dir=Path(scenario_dir),
        feature_file=Path(feature_file),
        overwrite=overwrite
    )
