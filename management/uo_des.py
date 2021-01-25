from pathlib import Path

import click
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


@click.group()
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
