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
