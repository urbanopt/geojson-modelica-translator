from pathlib import Path

import click
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


@click.group()
def cli():
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
    help="If a file already exists with the sys_param_filename, overwrite it."
)
def sys_param(sys_param_filename, scenario_dir, feature_file, overwrite=False):
    """GMT CLI."""
    sys_param_template_path = Path(__file__).parent.parent / 'geojson_modelica_translator' / \
        'system_parameters' / 'time_series_template.json'
    make_file = SystemParameters(sys_param_template_path)
    make_file.csv_to_sys_param(
        sys_param_filename=Path(sys_param_filename),
        scenario_dir=Path(scenario_dir),
        feature_file=Path(feature_file),
        overwrite=overwrite
    )
