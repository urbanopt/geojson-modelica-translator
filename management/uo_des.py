# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from shutil import rmtree

import click

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """URBANopt District Energy Systems"""


@cli.command(short_help="Create sys-param file")
@click.argument(
    "sys_param_filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.argument(
    "scenario_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.argument(
    "feature_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.argument(
    "model_type",
    default='time_series',
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help="Delete and replace any existing file of the same name & location",
    default=False
)
@click.option(
    '-m',
    '--microgrid',
    is_flag=True,
    help="If specified, microgrid inputs will be added to system parameters file",
    default=False
)
@click.option(
    '-g',
    '--ghe',
    is_flag=True,
    help="If specified, Ground Heat Exchanger properties will be added to System Parameters File",
    default=False
)
def build_sys_param(model_type: str,
                    sys_param_filename: Path,
                    scenario_file: Path,
                    feature_file: Path,
                    ghe: bool,
                    overwrite: bool,
                    microgrid: bool
                    ):
    """
    Create system parameters file using uo_sdk output

    SYS_PARAM_FILENAME: Path/name to sys-param file be created. Be sure to include the ".json" suffix.

    SCENARIO_FILE: Path to sdk scenario file.

    FEATURE_FILE: Path to sdk json feature file with data about the buildings.

    \b
    MODEL_TYPE: selection for which kind of simulation this sys-param file will support.
        Valid choices for MODEL_TYPE: "time_series"

    \f
    :param model_type: string, selection of which model type to use in the GMT
    :param sys_param_filename: Path, location & name of json output file to save
    :param scenario_file: Path, location of SDK scenario_file
    :param feature_file: Path, location of SDK feature_file
    :param ghe: Boolean, flag to add Ground Heat Exchanger properties to System Parameter File
    :param overwrite: Boolean, flag to overwrite an existing file of the same name/location
    :param microgrid: Boolean, flag to add Microgrid properties to System Parameter File
    """

    # Use scenario_file to be consistent with sdk
    scenario_name = Path(scenario_file).stem
    scenario_dir = Path(scenario_file).parent / 'run' / scenario_name
    sp = SystemParameters()
    sp.csv_to_sys_param(
        model_type=model_type,
        sys_param_filename=Path(sys_param_filename),
        scenario_dir=Path(scenario_dir),
        feature_file=Path(feature_file),
        ghe=ghe,
        overwrite=overwrite,
        microgrid=microgrid
    )

    if Path(sys_param_filename).exists():
        print(f"\nSystem parameters file {sys_param_filename} successfully created.")
    else:
        raise SystemExit(f"{sys_param_filename} failed. Please check your inputs and try again.")


@cli.command(short_help="Create Modelica model")
@click.argument(
    "sys_param_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.argument(
    "geojson_feature_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.argument(
    "project_path",
    default="model_from_sdk",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help="Delete and replace any existing folder of the same name & location",
    default=False
)
def create_model(sys_param_file: Path, geojson_feature_file: Path, project_path: Path, overwrite: bool):
    """Build Modelica model from user data

    SYS_PARAM_FILE: Path/name to sys-param file, possibly created with this CLI.

    GEOJSON_FEATURE_FILE: Path to sdk json feature file with data about the buildings.

    PROJECT_PATH: Path for Modelica project directory created with this command

    \f
    :param model_type: String, type of model to create
    :param sys_param_file: Path, location and name of file created with this cli
    :param geojson_feature_file: Path, location and name of sdk feature_file
    :param project_path: Path, location and name of Modelica model dir to be created
    :param overwrite: Boolean, flag to overwrite an existing file of the same name/location
    """
    project_path = Path(project_path)
    if project_path.exists():
        if overwrite:
            rmtree(project_path, ignore_errors=True)
        else:
            raise SystemExit(f"Output dir '{project_path}' already exists and overwrite flag is not given")
    if len(project_path.name.split()) > 1:  # Modelica can't handle spaces in project name
        raise SystemExit(
            f"\n'{project_path}' failed. Modelica does not support spaces in project names or paths. "
            "Please choose a different 'project_path'")

    gmt = GeoJsonModelicaTranslator(
        geojson_feature_file,
        sys_param_file,
        project_path.parent,
        project_path.name
    )

    gmt.to_modelica()


@cli.command(short_help="Run Modelica model")
@click.argument(
    "modelica_project",
    default="./model_from_sdk",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.argument(
    "start_time",
    default=17280000,
    type=int,
    required=False,
)
@click.argument(
    "stop_time",
    default=17366400,
    type=int,
    required=False,
)
@click.argument(
    "step_size",
    default=90,
    type=int,
    required=False,
)
def run_model(modelica_project: Path, start_time: int, stop_time: int, step_size: int):
    """
    \b
    Run the Modelica project in a docker-based environment.
    Results are saved at the same level as the project path that is passed.
    The model that runs is hard coded to be the Districts/DistrictEnergySystem.mo within the package.

    \b
    MODELICA_PROJECT: Path to the Modelica project, possibly created by this cli
        default = ./model_from_sdk

    \f
    :param modelica_project: Path, name & location of modelica project, possibly created with this cli
    """
    run_path = Path(modelica_project).resolve()
    project_name = run_path.stem

    if len(str(run_path).split()) > 1:  # Modelica can't handle spaces in project name or path
        raise SystemExit(
            f"\n'{run_path}' failed. Modelica does not support spaces in project names or paths. "
            "Please update your directory tree to not include spaces in any name")

    # setup modelica runner
    mr = ModelicaRunner()
    mr.run_in_docker('compile_and_run',
                     f'{project_name}.Districts.DistrictEnergySystem',
                     file_to_load=run_path / 'package.mo',
                     run_path=run_path,
                     start_time=start_time,
                     stop_time=stop_time,
                     step_size=step_size
                     )

    if (run_path.parent / f'{project_name}/{project_name}.Districts.DistrictEnergySystem_results' / f'{project_name}_Districts_DistrictEnergySystem_res.mat').exists():
        print(f"\nModelica model {project_name} ran successfully")
    else:
        raise SystemExit(f"\n{project_name} failed. Check the error log at {project_name}_results/stdout.log for more info.")
