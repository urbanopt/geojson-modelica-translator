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

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """URBANopt District Energy Systems"""
    pass


@cli.command(short_help="Create sys-param file")
@click.argument(
    'sys_param_filename',
    type=click.Path(),
)
@click.argument(
    "scenario_dir",
    type=click.Path(exists=True),
)
@click.argument(
    "feature_file",
    type=click.Path(exists=True)
)
@click.argument(
    "model-type",
    default='time_series'
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help="Delete and replace any existing file of the same name & location",
    default=False
)
def sys_param(model_type, sys_param_filename, scenario_dir, feature_file, overwrite):
    """
    Create system parameters file using uo_sdk output

    SYS_PARAM_FILENAME: Path/name to sys-param file be created. Be sure to include the ".json" suffix.

    SCENARIO_DIR: Path to sdk scenario folder with OpenStudio results.

    FEATURE_FILE: Path to sdk json feature file with data about the buildings.

    \b
    MODEL_TYPE: selection for which kind of simulation this sys-param file will support.
        Valid choices for MODEL_TYPE: "time_series"

    \f
    :param model_type: string, selection of which model type to use in the GMT
    :param sys_param_filename: Path, location & name of output file to save
    :param scenario_dir: Path, location of SDK scenario to create sys-param file from
    :param feature_file: Path, location of SDK feature file
    :param overwrite: Boolean, flag to overwrite an existing file of the same name/location
    """
    SystemParameters.csv_to_sys_param(
        model_type=model_type,
        sys_param_filename=Path(sys_param_filename),
        scenario_dir=Path(scenario_dir),
        feature_file=Path(feature_file),
        overwrite=overwrite
    )
