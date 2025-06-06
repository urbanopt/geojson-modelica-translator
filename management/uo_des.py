# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path
from shutil import rmtree

import click

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.results_ghp import ResultsModelica
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """URBANopt District Energy Systems"""


@cli.command(short_help="Create sys-param file")
@click.argument(
    "sys_param_filename",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path, readable=True, resolve_path=True),
)
@click.argument(
    "scenario_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path, readable=True, resolve_path=True),
)
@click.argument(
    "feature_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path, readable=True, resolve_path=True),
)
@click.argument(
    "district_type",
    default="4G",
)
@click.argument(
    "model_type",
    default="time_series",
)
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    help="Delete and replace any existing file of the same name & location",
    default=False,
)
@click.option(
    "-m",
    "--microgrid",
    is_flag=True,
    help="If specified, microgrid inputs will be added to system parameters file",
    default=False,
)
@click.option(
    "-w",
    "--skip_weather_download",
    is_flag=True,
    help="If specified, weather files will not be downloaded",
    default=False,
)
def build_sys_param(
    model_type: str,
    sys_param_filename: Path,
    scenario_file: Path,
    feature_file: Path,
    district_type: str,
    overwrite: bool,
    microgrid: bool,
    skip_weather_download: bool,
):
    """Create system parameters file using uo_sdk output

    SYS_PARAM_FILENAME: Path/name to sys-param file be created. Be sure to include the ".json" suffix.

    SCENARIO_FILE: Path/name to sdk scenario file.

    FEATURE_FILE: Path/name to sdk json feature file with data about the buildings.

    DISTRICT_TYPE: selection for which kind of simulation this sys-param file will support.
    Available options are: ['steam', '4G', '5G', '5G_ghe']
    Defaults to '4G'

    \b
    MODEL_TYPE: selection for which kind of simulation this sys-param file will support.
    Available options are: "time_series"

    \f
    :param model_type: string, selection of which model type to use in the GMT
    :param sys_param_filename: Path, location & name of json output file to save
    :param scenario_file: Path, location of SDK scenario_file
    :param feature_file: Path, location of SDK feature_file
    :param district_type: string, district type to model
    :param overwrite: Boolean, flag to overwrite an existing file of the same name/location
    :param microgrid: Boolean, flag to add Microgrid properties to System Parameter File
    """

    # Use scenario_file to be consistent with sdk
    scenario_name = scenario_file.stem
    scenario_dir = scenario_file.parent / "run" / scenario_name
    sp = SystemParameters()
    sp.csv_to_sys_param(
        model_type=model_type,
        sys_param_filename=sys_param_filename,
        scenario_dir=scenario_dir,
        feature_file=feature_file,
        district_type=district_type,
        overwrite=overwrite,
        microgrid=microgrid,
        skip_weather_download=skip_weather_download,
    )

    if Path(sys_param_filename).exists():
        print(f"\nSystem parameters file {sys_param_filename} successfully created.")
    else:
        raise SystemExit(f"{sys_param_filename} failed. Please check your inputs and try again.")


@cli.command(short_help="Create Modelica model")
@click.argument(
    "sys_param_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path, readable=True, resolve_path=True),
)
@click.argument(
    "geojson_feature_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path, readable=True, resolve_path=True),
)
@click.argument(
    "project_path",
    default="model_from_sdk",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path, readable=True, resolve_path=True),
)
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    help="Delete and replace any existing folder of the same name & location",
    default=False,
)
def create_model(sys_param_file: Path, geojson_feature_file: Path, project_path: Path, overwrite: bool):
    """Build Modelica model from user data

    SYS_PARAM_FILE: Path/name to sys-param file, possibly created with this CLI.

    GEOJSON_FEATURE_FILE: Path to sdk json feature file with data about the buildings.

    PROJECT_PATH: Path for Modelica project directory created with this command

    \f
    :param sys_param_file: Path, location and name of file created with this cli
    :param geojson_feature_file: Path, location and name of sdk feature_file
    :param project_path: Path, location and name of Modelica model dir to be created
    :param overwrite: Boolean, flag to overwrite an existing file of the same name/location
    """

    if project_path.exists():
        if overwrite:
            rmtree(project_path, ignore_errors=True)
        else:
            raise SystemExit(f"Output dir '{project_path}' already exists and overwrite flag is not given")
    if len(project_path.name.split()) > 1:  # Modelica can't handle spaces in project name
        raise SystemExit(
            f"\n'{project_path}' failed. Modelica does not support spaces in project names or paths. "
            "Please choose a different 'project_path'"
        )

    gmt = GeoJsonModelicaTranslator(geojson_feature_file, sys_param_file, project_path.parent, project_path.name)

    gmt.to_modelica()


@cli.command(short_help="Run Modelica model")
@click.argument(
    "modelica_project",
    default="./model_from_sdk",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path, readable=True, resolve_path=True),
)
@click.option(
    "-a",
    "--start_time",
    default=17280000,
    help="Start time of the simulation (seconds of a year)",
    type=int,
)
@click.option(
    "-z",
    "--stop_time",
    default=17366400,
    help="Stop time of the simulation (seconds of a year)",
    type=int,
)
@click.option(
    "-x",
    "--step_size",
    default=90,
    help="Step size of the simulation (seconds)",
    type=int,
)
@click.option(
    "-i",
    "--intervals",
    default=None,
    help="Number of intervals to divide the simulation into (alternative to step_size)",
    type=int,
)
@click.option(
    "-o",
    "--output_variables",
    default=None,
    help="Comma-separated list of specific output variables to capture from simulation",
    type=str,
)
@click.option(
    "-c",
    "--compiler_flags",
    default=None,
    help="Comma-separated list of OpenModelica compiler flags. For advanced users only",
    type=str,
)
@click.option(
    "-s",
    "--simulation_flags",
    default=None,
    help="Comma-separated list of OpenModelica simulation flags. For advanced users only",
    type=str,
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Keeps intermediate files for debugging if something goes wrong",
    default=False,
)
def run_model(
    modelica_project: Path,
    start_time: int,
    stop_time: int,
    step_size: int,
    intervals: int,
    output_variables: str,
    compiler_flags: str,
    simulation_flags: str,
    debug: bool,
):
    """Run the model

    \b
    Run the Modelica project in a docker-based environment.
    Results are saved at the same level as the project path that is passed.
    The model that runs is hard coded to be the Districts/DistrictEnergySystem.mo within the package.

    \b
    MODELICA_PROJECT: Path to the Modelica project, possibly created by this cli
    default = ./model_from_sdk

    \f
    :param sys_param_file: Path, location and name of file created with this cli
    :param modelica_project: Path, name & location of modelica project, possibly created with this cli
    :param start_time (int): start time of the simulation (seconds of a year)
    :param stop_time (int): stop time of the simulation (seconds of a year)
    :param step_size (int): step size of the simulation (seconds)
    :param number_of_intervals (int): number of intervals to run the simulation
    :param output_variables (str) Comma-separated list of specific output variables to capture from simulation
    :param compiler_flags (str): Comma-separated list of OpenModelica simulation flags. For advanced users only
    :param simulation_flags (str): Comma-separated list of OpenModelica simulation flags. For advanced users only
    :param debug (bool): if True, keeps intermediate files for debugging
    """
    project_name = modelica_project.stem

    if len(str(modelica_project).split()) > 1:  # Modelica can't handle spaces in project name or path
        raise SystemExit(
            f"\n'{modelica_project}' failed. Modelica does not support spaces in project names or paths. "
            "Please update your directory tree to not include spaces in any name"
        )

    # setup modelica runner
    mr = ModelicaRunner()
    mr.run_in_docker(
        "compile_and_run",
        f"{project_name}.Districts.DistrictEnergySystem",
        file_to_load=modelica_project / "package.mo",
        run_path=modelica_project,
        start_time=start_time,
        stop_time=stop_time,
        step_size=step_size,
        number_of_intervals=intervals,
        output_variables=output_variables,
        compiler_flags=compiler_flags,
        simulation_flags=simulation_flags,
        debug=debug,
    )

    run_location = modelica_project.parent / project_name / f"{project_name}.Districts.DistrictEnergySystem_results"
    if (run_location / f"{project_name}.Districts.DistrictEnergySystem_res.mat").exists():
        print(f"\nModelica model {project_name} ran successfully and can be found in {run_location}")
    else:
        raise SystemExit(f"\n{project_name} failed. Check the error log at {run_location}/stdout.log for more info.")


@cli.command(short_help="Process Modelica model")
@click.argument(
    "modelica_project",
    default="./model_from_sdk",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path, readable=True, resolve_path=True),
)
def des_process(modelica_project: Path):
    """Post Process the model

    \b
    Post process results from Modelica project run previously, for GHP LCCA analysis

    \b
    MODELICA_PROJECT: Path to the Modelica project, possibly created by this cli
    default = ./model_from_sdk

    \f
    :param modelica_project: Path, name & location of modelica project, possibly created with this cli
    """

    result = ResultsModelica(modelica_project)
    result.calculate_results()
