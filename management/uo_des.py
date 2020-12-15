from pathlib import Path

import click
from geojson_modelica_translator.geojson.csv_to_sys_param import CSVToSysParam


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '-f',
    '--sys_param_filename',
    default="test_sys_param.json",
    help='Name of systems parameters file to create. Include ".json" in your name'
)
@click.option(
    "-s",
    "--scenario_dir",
    help="Path to an urbanopt scenario, probably in the 'run' folder of your UO SDK project directory",
    default=Path.cwd() / "tests" / "geojson" / "data" / "sdk_output_skeleton" / "run" / "baseline_15min"
)
@click.option(
    "-t",
    "--sys_param_template",
    default=Path.cwd() / "tests" / "geojson" / "data" / "time_series_template.json",
    help="Path to the template sys_param.json file"
)
def sys_param(sys_param_filename, scenario_dir, sys_param_template):
    """Test GMT CLI."""
    # click.echo(sys_param_filename)
    csv_to_sys_param = CSVToSysParam(scenario_dir=Path(scenario_dir), sys_param_template=sys_param_template)
    csv_to_sys_param.csv_to_sys_param(sys_param_filename)
