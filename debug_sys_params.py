import copy
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import namedtuple

from jsonpath_ng.ext import parse

base_geojson_path = 'baseline_geojson.json'
base_sys_params_path = 'baseline_sys_params.json'

SYS_PARAMS_SCHEMA_PATH = 'geojson_modelica_translator/system_parameters/schema.json'

def create_package(package_name, geojson_path, sys_params_path):
    process = subprocess.Popen(
        ['poetry', 'run', 'uo_des', 'create-model', sys_params_path, geojson_path, package_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(stdout.decode())
        print(stderr.decode())
        raise Exception('Failed to create model')

def get_terminal_paths(obj, current_path):
    """
    :param obj: dict
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
            import pdb; pdb.set_trace()
            raise Exception('Uh oh')

    return paths

def get_all_terminal_paths(obj):
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

def print_diffs(p1, p2):
    for root, dirnames, filenames in os.walk(p1):
        for filename in filenames:

            f1 = f'{root}/{filename}'
            f2 = f'{root.replace(p1, p2)}/{filename}'

            with open(f1) as f:
                f1_text = f.readlines()
            with open(f2) as f:
                f2_text_orig = f.readlines()
                f2_text = []
                for line in f2_text_orig:
                    f2_text.append(line.replace(p2, p1))

            # remove annotations (placements might get moved around)
            f1_used_lines = []
            for line in f1_text:
                if not line.strip().startswith('annotation'):
                    f1_used_lines.append(line)

            f2_used_lines = []
            for line in f2_text:
                if not line.strip().startswith('annotation'):
                    f2_used_lines.append(line)

            for diff in difflib.unified_diff(
                f1_used_lines, f2_used_lines,
                fromfile=f1, tofile=f2, lineterm=''):
                print(diff)

BASELINE_PACKAGE = 'baseline_package'
if __name__ == '__main__':
    create_package(BASELINE_PACKAGE, base_geojson_path, base_sys_params_path)

    with open(base_sys_params_path) as f:
        base_sys_params = json.loads(f.read())

    params = get_all_terminal_paths(base_sys_params)

    # for each param, see what happens to the package when we modify it
    for idx, param in enumerate(params):
        if param['skip']:
            print(f'{param["path"]} Skipped (duplicate)')
            continue

        if param['type'] == 'string':
            print(f'{param["path"]} Skipped (string)')
            continue

        jsonpath = parse(param['path'])
        original_value = jsonpath.find(base_sys_params)[0].value

        if param['type'] == 'number':
            value = 1337000
        elif param['type'] == 'bool':
            value = not original_value
        else:
            raise Exception('Oops')

        test_sys_params = copy.deepcopy(base_sys_params)
        jsonpath.update(test_sys_params, value)
        test_package_name = f'test_package_{idx}'

        # generate the package
        with open('test_sys_params.json', 'w') as fp:
            fp.write(json.dumps(test_sys_params))
            fp.seek(0)
            test_sys_params_path = fp.name
            create_package(test_package_name, base_geojson_path, test_sys_params_path)

        print(f'{param["path"]}   Testing    Original: {original_value}; New: {value}')

        # compare the package to baseline (find diffs)
        print_diffs(BASELINE_PACKAGE, test_package_name)


        shutil.rmtree(test_package_name)

    shutil.rmtree(BASELINE_PACKAGE)
