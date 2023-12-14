# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import math
import os
from pathlib import Path

import pandas as pd
import scipy.io as sio
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.couplings.diagram import (
    Diagram
)
from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.scaffold import Scaffold
from geojson_modelica_translator.utils import ModelicaPath


def render_template(template_name, template_params):
    """Helper for rendering a template

    :param template_name: string, name of template (relative to templates directory)
    :param template_params: dict, template parameters
    :return: string, templated result
    """
    template_dir = Path(__file__).parent / 'templates'
    template_env = Environment(
        loader=FileSystemLoader(searchpath=template_dir),
        undefined=StrictUndefined)
    template_env.filters.update(ALL_CUSTOM_FILTERS)
    template = template_env.get_template(template_name)
    return template.render(template_params)


def flip_matrix(list_of_dictionaries):
    # only applies to dictionaries with two nested levels
    flipped_dictionary = dict()
    for i_dict, dictionary in enumerate(list_of_dictionaries):
        for key_lvl0, value_lvl0 in dictionary.items():

            # applies to keys with a value that is not a dictionary
            # creates flipped matrix
            if not isinstance(value_lvl0, dict):
                if i_dict == 0:
                    flipped_dictionary[key_lvl0] = [value_lvl0]
                    continue
                else:
                    flipped_dictionary[key_lvl0].append(value_lvl0)
                    continue

            # applies to keys with a value that is a dictionary
            # creates empty dictionaries
            if not flipped_dictionary.get(key_lvl0, None):
                flipped_dictionary[key_lvl0] = dict()

            # applies to keys with a value that is a dictionary
            # creates flipped matrix
            for key_lvl1, value_lvl1 in value_lvl0.items():
                if i_dict == 0:
                    flipped_dictionary[key_lvl0][key_lvl1] = [value_lvl1]
                else:
                    flipped_dictionary[key_lvl0][key_lvl1].append(value_lvl1)

    # returns dictionary with same key structure with a list of flipped values
    return (flipped_dictionary)


def process_gfunction(list_of_gfunctions, flipped_sys_params, sys_params_ghe_parameters, b_modelica_path, project_name):
    list_of_gfunction_file_paths = []
    for i_gfun, gfunction in enumerate(list_of_gfunctions):
        # convert the values to match Modelica gfunctions
        for i in range(len(gfunction)):
            gfunction[gfunction.columns[0]].iloc[i] = math.exp(gfunction[gfunction.columns[0]].iloc[i]) * flipped_sys_params["borehole"]["length_of_boreholes"][i_gfun]**2 / (
                9 * sys_params_ghe_parameters["soil"]["conductivity"] / sys_params_ghe_parameters["soil"]["rho_cp"])
            gfunction[gfunction.columns[1]].iloc[i] = gfunction[gfunction.columns[1]].iloc[i] / \
                (flipped_sys_params["borehole"]["number_of_boreholes"][i_gfun] * 2 * math.pi * flipped_sys_params["borehole"]["length_of_boreholes"][i_gfun] * sys_params_ghe_parameters["soil"]["conductivity"])

        # add zeros to the first row
        new_row = pd.Series({gfunction.columns[0]: 0, gfunction.columns[1]: 0})
        gfunction = pd.concat([gfunction.iloc[:0], pd.DataFrame([new_row]), gfunction.iloc[0:]]).reset_index(drop=True)

        # add to dict and save MAT file to the borefield's resources folder
        data_dict = {'TStep': gfunction.values}
        gfunction_path = os.path.join(b_modelica_path.resources_dir, "Gfunction_" + str(i_gfun) + ".mat")
        sio.savemat(gfunction_path, data_dict)
        gfunction_file_path = b_modelica_path.resources_relative_dir + "/Gfunction_" + str(i_gfun) + ".mat"

        gfunction_file_path = "modelica://" + project_name + "/Plants/" + gfunction_file_path

        list_of_gfunction_file_paths.append(gfunction_file_path)

    return (list_of_gfunction_file_paths)


class District:
    """
    Class for modeling entire district energy systems
    """

    def __init__(self, root_dir, project_name, system_parameters, coupling_graph, **kwargs):
        self._scaffold = Scaffold(root_dir, project_name)
        self.system_parameters = system_parameters
        self._coupling_graph = coupling_graph
        self.district_model_filepath = None
        # Modelica can't handle spaces in project name or path
        if (len(str(root_dir).split()) > 1) or (len(str(project_name).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{root_dir}' for run path and {project_name} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")
        # reads borehole_pipe_arrangement from borefield.py
        self.borehole_pipe_arrangement = kwargs.get('borehole_pipe_arrangement')
        self.borefield_borehole_configuration_type = kwargs.get('borefield_borehole_configuration_type')
        self.borefield_id = kwargs.get('borefield_id')

    def to_modelica(self):
        """Generate modelica files for the models as well as the modelica file for
        the entire district system.
        """
        # scaffold the project
        self._scaffold.create()
        self.district_model_filepath = Path(self._scaffold.districts_path.files_dir) / 'DistrictEnergySystem.mo'

        # create the root package
        root_package = PackageParser.new_from_template(
            self._scaffold.project_path, self._scaffold.project_name, order=[])
        root_package.save()

        # generate model modelica files
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        # construct graph of visual components
        diagram = Diagram(self._coupling_graph)

        # Load system parameters
        sys_params_buildings = self.system_parameters.get_param('$.buildings')
        sys_params_district_system = self.system_parameters.get_param('$.district_system')
        sys_params_ghe_parameters = self.system_parameters.get_param('$.district_system.fifth_generation.ghe_parameters')
        sys_params_ghe_specific_params = self.system_parameters.get_param(
            "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params")
        sys_params_pipe = self.system_parameters.get_param("$.district_system.fifth_generation.ghe_parameters.pipe")

        # Flip matrix of sys_params_ghe_specific_params to create a list for each
        # parameter that collects parameter values for all borefields
        flipped_sys_params = flip_matrix(sys_params_ghe_specific_params)

        # number of unique borefields in system_params_ghe.json
        number_of_borefields = len(sys_params_ghe_specific_params)

        # process nominal mass flow rate
        if sys_params_ghe_parameters["design"]["flow_type"] == "system":
            design_flow_rate = [sys_params_ghe_parameters["design"]["flow_rate"]
                                / x for x in flipped_sys_params["borehole"]["number_of_boreholes"]]
        else:
            design_flow_rate = [sys_params_ghe_parameters["design"]["flow_rate"]] * number_of_borefields

        # process tube thickness
        if sys_params_pipe["outer_diameter"] and sys_params_pipe["inner_diameter"]:
            pipe_thickness = (sys_params_pipe["outer_diameter"] - sys_params_pipe["inner_diameter"]) / 2
        else:
            pipe_thickness = None

        # process shank spacing
        if sys_params_pipe["shank_spacing"] and sys_params_pipe["outer_diameter"]:
            pipe_shank_spacing = (sys_params_pipe["shank_spacing"] + sys_params_pipe["outer_diameter"]) / 2
        else:
            pipe_shank_spacing = None

        # process g-function file
        list_of_gfunctions = []
        for ghe_id_instance in flipped_sys_params["ghe_id"]:
            if Path(sys_params_ghe_parameters["ghe_dir"]).expanduser().is_absolute():
                list_of_gfunctions.append(
                    pd.read_csv(
                        Path(
                            sys_params_ghe_parameters["ghe_dir"])
                        / ghe_id_instance
                        / "Gfunction.csv",
                        header=0,
                        usecols=[
                            0,
                            2]))
            else:
                sys_param_dir = Path(self.system_parameters.filename).parent.resolve()
                try:
                    list_of_gfunctions.append(
                        pd.read_csv(
                            sys_param_dir
                            / sys_params_ghe_parameters["ghe_dir"]
                            / ghe_id_instance
                            / "Gfunction.csv",
                            header=0,
                            usecols=[
                                0,
                                2]))
                except FileNotFoundError:
                    raise SystemExit(
                        f'When using a relative path to your ghe_dir, your path \'{sys_params_ghe_parameters["ghe_dir"]}\' must be relative to the dir your sys-param file is in.')
        ghe_dir_gfunction_file_rows = [gfunction.shape[0] + 1 for gfunction in list_of_gfunctions]

        # create borefield package paths
        b_modelica_path = ModelicaPath(model.borefield_name, self._scaffold.plants_path.files_dir, True)

        list_of_gfunction_file_paths = process_gfunction(
            list_of_gfunctions,
            flipped_sys_params,
            sys_params_ghe_parameters,
            b_modelica_path,
            self._scaffold.project_name)

        district_template_params = {
            "district_within_path": '.'.join([self._scaffold.project_name, 'Districts']),
            "diagram": diagram,
            "couplings": [],
            "models": [],
            "is_ghe_district": self.system_parameters.get_param('$.district_system.fifth_generation.ghe_parameters')
        }
        common_template_params = {
            'globals': {
                'medium_w': 'MediumW',
                'delChiWatTemBui': 'delChiWatTemBui',
                'delChiWatTemDis': 'delChiWatTemDis',
                'delHeaWatTemBui': 'delHeaWatTemBui',
                'delHeaWatTemDis': 'delHeaWatTemDis',
            },
            'graph': self._coupling_graph,
            'sys_params': {
                'district_system': sys_params_district_system,
                'ghe_parameters': sys_params_ghe_parameters,
                # num_buildings counts the ports required for 5G systems
                "num_buildings": len(sys_params_buildings),
                "number_of_borefields": number_of_borefields,
                "borehole_pipe_arrangement": self.borehole_pipe_arrangement,
                "borefield_borehole_configuration_type": self.borefield_borehole_configuration_type,
                'flipped_sys_params': flipped_sys_params,
                "design_flow_rate": design_flow_rate,
                "pipe_thickness": pipe_thickness,
                "pipe_shank_spacing": pipe_shank_spacing,
                "ghe_dir_gfunction_file_rows": ghe_dir_gfunction_file_rows,
                "project_name": self._scaffold.project_name,
                "list_of_gfunction_file_paths": list_of_gfunction_file_paths,
                "borefield_name": model.borefield_name,
                "borefield_id": self.borefield_id
            }
        }

        # render each coupling
        load_num = 1
        for coupling in self._coupling_graph.couplings:
            template_context = {
                'diagram': diagram.to_dict(coupling.id, is_coupling=True),
            }
            template_context.update(**common_template_params)

            coupling_load = coupling.get_load()
            if coupling_load is not None:
                # read sys params file for the load
                building_sys_params = self.system_parameters.get_param_by_id(coupling_load.building_id, '$')
                template_context['sys_params']['building'] = building_sys_params
                # Note which load is being used, so ports connect properly in couplings/5G_templates/ConnectStatements
                template_context['sys_params']['load_num'] = load_num
                load_num += 1

            templated_result = coupling.render_templates(template_context)
            district_template_params['couplings'].append({
                'id': coupling.id,
                'component_definitions': templated_result['component_definitions'],
                'connect_statements': templated_result['connect_statements'],
                'coupling_definitions_template_path': templated_result['component_definitions_template_path'],
                'connect_statements_template_path': templated_result['connect_statements_template_path'],
            })

        # render each model instance
        for model in self._coupling_graph.models:
            template_params = {
                'model': model.to_dict(self._scaffold),
                'couplings': self._coupling_graph.couplings_by_type(model.id),
                'diagram': diagram.to_dict(model.id, is_coupling=False),
            }
            template_params.update(**common_template_params)

            if issubclass(type(model), LoadBase):
                building_sys_params = self.system_parameters.get_param_by_id(model.building_id, '$')
                template_params['sys_params']['building'] = building_sys_params

            templated_instance, instance_template_path = model.render_instance(template_params)
            district_template_params['models'].append({
                'id': model.id,
                'instance_template_path': instance_template_path,
                'instance': templated_instance
            })

        # render the full district file
        if 'fifth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem5G.mot', district_template_params)
            if "ghe_parameters" in common_template_params['sys_params']['district_system']['fifth_generation']:
                final_result = render_template('DistrictEnergySystem_ghe_partial.mot', district_template_params)
        elif 'fourth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem.mot', district_template_params)
        with open(self.district_model_filepath, 'w') as f:
            f.write(final_result)

        districts_package = PackageParser.new_from_template(self._scaffold.districts_path.files_dir, "Districts", [
            'DistrictEnergySystem'], within=f"{self._scaffold.project_name}")
        districts_package.save()

        root_package = PackageParser(self._scaffold.project_path)
        if 'Districts' not in root_package.order:
            root_package.add_model('Districts')
            root_package.save()
