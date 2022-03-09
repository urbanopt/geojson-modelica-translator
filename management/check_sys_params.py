import copy
import difflib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import click
from jsonpath_ng.ext import parse

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / 'data'

BASELINE_PACKAGE = 'baseline_package'
BASELINE_GEOJSON = 'baseline_geojson.json'
BASELINE_SYS_PARAMS = 'baseline_sys_params.json'
BASELINE_TIME_SERIES = 'baseline_time_series.mos'
BASELINE_WEATHER_FILE = 'baseline_weather.mos'

SYS_PARAMS_SCHEMA_PATH = Path(__file__).parent.parent / 'geojson_modelica_translator' / 'system_parameters' / 'schema.json'


def create_package(package_path, geojson_path, sys_params_path):
    """Creates a package using the uo_des CLI.
    Raises an exception if it fails to create the package.

    :param package_path: Path | str, where to create the package
    :param geojson_path: Path | str, where the geojson file is located
    :param sys_params_path: Path | str, where the system parameters file is located
    :return None:
    """
    process = subprocess.Popen(
        ['poetry', 'run', 'uo_des', 'create-model', sys_params_path, geojson_path, package_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        logger.error(stdout.decode())
        logger.error(stderr.decode())
        raise Exception('Failed to create model')


def get_terminal_paths(obj, current_path):
    """Find all paths to terminal values in the object (recursively).
    Each path object contains a type (number, string, bool, etc) and a list
    of keys to reach that point.

    :param obj: dict
    :param current_path: list[str], list of keys that got us to this point
    :return: list[dict]
    """
    paths = []
    for key, value in obj.items():
        if type(value) in [int, float]:
            paths.append({'type': 'number', 'path': current_path + [key]})
        elif type(value) is str:
            paths.append({'type': 'string', 'path': current_path + [key]})
        elif type(value) is bool:
            paths.append({'type': 'bool', 'path': current_path + [key]})
        elif type(value) is list:
            if len(value) > 0 and type(value[0]) is dict:
                for idx, item in enumerate(value):
                    paths += get_terminal_paths(item, current_path + [f'{key}[{idx}]'])
            else:
                # skip lists that aren't dicts for now
                continue
        elif type(value) is dict:
            paths += get_terminal_paths(value, current_path + [key])
        else:
            raise Exception(f'Unhandled type: "{type(value)}"')

    return paths


def get_all_terminal_paths(obj):
    """Construct JSON paths to all terminal values in obj

    :param obj: dict
    :return: list[dict]
    """
    terminal_paths = get_terminal_paths(obj, ['$'])

    # reformat path arrays into jsonpaths
    for terminal_path in terminal_paths:
        terminal_path['path'] = ".".join(terminal_path["path"])

    # deduplicate array objects
    # flag duplicates with "skip"
    registered_paths = set()
    for terminal_path in terminal_paths:
        standardized_path = re.sub(r'\[\d+\]', '[*]', terminal_path['path'])
        if standardized_path not in registered_paths:
            registered_paths.add(standardized_path)
            terminal_path['skip'] = False
        else:
            terminal_path['skip'] = True

    return terminal_paths


def print_diffs(p1, p2, output_file):
    """Print the diffs between modelica packages p1 and p2

    :param p1: str, path to root of package 1
    :param p2: str, path to root of package 2
    :param output_file: File, file to print diffs to
    :return: None
    """
    package_1_name = Path(p1).name
    package_2_name = Path(p2).name

    found_any_diffs = False

    # for each file in p1, compare it to the same file in p2
    for root, _, filenames in os.walk(p1):
        for filename in filenames:

            f1 = f'{root}/{filename}'
            f2 = f'{root.replace(p1, p2)}/{filename}'

            with open(f1) as f:
                f1_text = f.readlines()
            with open(f2) as f:
                f2_text_orig = f.readlines()
                f2_text = []
                for line in f2_text_orig:
                    # replace the package names in the files
                    f2_text.append(line.replace(package_2_name, package_1_name))

            # remove annotations (placements might get moved around)
            f1_used_lines = []
            for line in f1_text:
                if not line.strip().startswith('annotation'):
                    f1_used_lines.append(line)

            f2_used_lines = []
            for line in f2_text:
                if not line.strip().startswith('annotation'):
                    f2_used_lines.append(line)

            file_diffs = difflib.unified_diff(
                f1_used_lines,
                f2_used_lines,
                fromfile=f1,
                tofile=f2,
                lineterm='',
            )
            for diff in file_diffs:
                found_any_diffs = True
                print(diff, file=output_file)

    if not found_any_diffs:
        print('No diff', file=output_file)


@click.command()
@click.option(
    '-v',
    is_flag=True,
    help="Verbose logging",
    default=False
)
@click.option(
    '-vv',
    is_flag=True,
    help="Very verbose logging",
    default=False
)
@click.option(
    '-o',
    '--output-file',
    help="Output file name. Defaults to STDOUT",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    default=None,
)
@click.option(
    '-l',
    '--log-file',
    help="Log file name. Defaults to STDERR",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    default=None,
)
def check_sys_params(v, vv, output_file, log_file):
    """Given a baseline systems parameters file, this function generates a package
    from the sys params. Then, for each system parameter, it tweaks the parameter
    from the original value, generates a new package, and compares it to the baseline
    package to see what it changed in the resulting package.

    This is used to find out what system parameters are not being propagated into
    the modelica templates.

    :param v: bool, verbose logging
    :param vv: bool, very verbose logging
    :param output_file: str | None, where to write the results -- if None, write to STDOUT
    :param log_file: str | None, where to write the logs -- if None, write to STDERR
    """
    log_level = logging.WARNING
    if v:
        log_level = logging.INFO
    if vv:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, filename=log_file)

    output_file_handle = open(output_file, 'w') if output_file else sys.stdout

    # use deterministic IDs for models so that we can diff packages without worrying
    # about different IDs
    os.environ["GMT_DETERMINISTIC_ID"] = 'True'

    DELIMITER = '=' * 50

    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.debug(f'Saving temporary models in {tmpdirname}')

        # some setup in the temp-dir
        BASELINE_GEOJSON_PATH = f'{tmpdirname}/{BASELINE_GEOJSON}'
        BASELINE_SYS_PARAMS_PATH = f'{tmpdirname}/{BASELINE_SYS_PARAMS}'
        for baseline_file_name in [BASELINE_SYS_PARAMS, BASELINE_GEOJSON, BASELINE_TIME_SERIES, BASELINE_WEATHER_FILE]:
            source_path = DATA_DIR / baseline_file_name
            destination_path = f'{tmpdirname}/{baseline_file_name}'
            logger.debug(f'Copying {source_path} to {destination_path}')
            shutil.copyfile(source_path, destination_path)

        # create the baseline package
        BASELINE_PACKAGE_PATH = f'{tmpdirname}/{BASELINE_PACKAGE}'
        create_package(BASELINE_PACKAGE_PATH, BASELINE_GEOJSON_PATH, BASELINE_SYS_PARAMS_PATH)

        with open(BASELINE_SYS_PARAMS_PATH) as f:
            base_sys_params = json.loads(f.read())

        params = get_all_terminal_paths(base_sys_params)

        # for each param, see what happens to the package when we modify it
        for idx, param in enumerate(params):
            print(DELIMITER, file=output_file_handle)
            if param['skip']:
                print(f'{param["path"]} Skipped (duplicate)', file=output_file_handle)
                continue

            if param['type'] == 'string':
                print(f'{param["path"]} Skipped (string)', file=output_file_handle)
                continue

            jsonpath = parse(param['path'])
            original_value = jsonpath.find(base_sys_params)[0].value

            if param['type'] == 'number':
                value = 1337000
            elif param['type'] == 'bool':
                value = not original_value
            else:
                raise Exception(f'Unhandled parameter type "{param["type"]}"')

            test_sys_params = copy.deepcopy(base_sys_params)
            jsonpath.update(test_sys_params, value)
            test_package_name = f'test_package_{idx}'
            test_package_path = f'{tmpdirname}/{test_package_name}'

            # generate the package
            with open(f'{tmpdirname}/test_sys_params.json', 'w') as fp:
                fp.write(json.dumps(test_sys_params))
                fp.seek(0)
                test_sys_params_path = fp.name
                create_package(test_package_path, BASELINE_GEOJSON_PATH, test_sys_params_path)

            print(f'{param["path"]}   Testing    Original: {original_value}; New: {value}', file=output_file_handle)

            # compare the package to baseline (find diffs)
            print_diffs(BASELINE_PACKAGE_PATH, test_package_path, output_file_handle)

    output_file_handle.close()
