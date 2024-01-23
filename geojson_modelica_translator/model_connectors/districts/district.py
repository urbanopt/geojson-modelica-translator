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
    # only applies to dictionaries with three nested levels
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

                # applies to keys with a value that is not a dictionary
                # creates flipped matrix
                if not isinstance(value_lvl1, dict):
                    if i_dict == 0:
                        flipped_dictionary[key_lvl0][key_lvl1] = [value_lvl1]
                        continue
                    else:
                        flipped_dictionary[key_lvl0][key_lvl1].append(value_lvl1)
                        continue

                # applies to keys with a value that is a dictionary
                # creates empty dictionaries
                if not flipped_dictionary[key_lvl0].get(key_lvl1, None):
                    flipped_dictionary[key_lvl0][key_lvl1] = dict()

                # applies to keys with a value that is a dictionary
                # creates flipped matrix
                for key_lvl2, value_lvl2 in value_lvl1.items():
                    if i_dict == 0:
                        flipped_dictionary[key_lvl0][key_lvl1][key_lvl2] = [value_lvl2]
                    else:
                        flipped_dictionary[key_lvl0][key_lvl1][key_lvl2].append(value_lvl2)

    # returns dictionary with same key structure with a list of flipped values
    return (flipped_dictionary)


def process_gfunction(
        list_of_gfunctions,
        lst_length_of_boreholes,
        lst_number_of_boreholes,
        sys_params_ghe_parameters,
        b_modelica_path,
        project_name,
        list_of_ids):
    list_of_gfunction_file_paths = []
    for i_gfun, gfunction in enumerate(list_of_gfunctions):
        # convert the values to match Modelica gfunctions
        for i in range(len(gfunction)):
            gfunction[gfunction.columns[0]].iloc[i] = math.exp(gfunction[gfunction.columns[0]].iloc[i]) * lst_length_of_boreholes[i_gfun]**2 / (
                9 * sys_params_ghe_parameters["soil"]["conductivity"] / sys_params_ghe_parameters["soil"]["rho_cp"])
            gfunction[gfunction.columns[1]].iloc[i] = gfunction[gfunction.columns[1]].iloc[i] / \
                (lst_number_of_boreholes[i_gfun] * 2 * math.pi * lst_length_of_boreholes[i_gfun] * sys_params_ghe_parameters["soil"]["conductivity"])

        # add zeros to the first row
        new_row = pd.Series({gfunction.columns[0]: 0, gfunction.columns[1]: 0})
        gfunction = pd.concat([gfunction.iloc[:0], pd.DataFrame([new_row]), gfunction.iloc[0:]]).reset_index(drop=True)

        # add to dict and save MAT file to the borefield's resources folder
        data_dict = {'TStep': gfunction.values}
        gfun_suffix = list_of_ids[i_gfun]
        gfunction_path = os.path.join(b_modelica_path.resources_dir, "Gfunction_" + gfun_suffix + ".mat")
        sio.savemat(gfunction_path, data_dict)
        gfunction_file_path = b_modelica_path.resources_relative_dir + "/Gfunction_" + gfun_suffix + ".mat"

        gfunction_file_path = "modelica://" + project_name + "/Plants/" + gfunction_file_path

        list_of_gfunction_file_paths.append(gfunction_file_path)

    return (list_of_gfunction_file_paths)


def process_gfunction_file(self, dictionary_ghe_ids, sys_params_ghe_parameters):
    # process g-function file
    list_of_gfunctions = []
    for ghe_id_instance in dictionary_ghe_ids:
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

    return (ghe_dir_gfunction_file_rows, list_of_gfunctions)


def move_bldg_ghe_grp_diagram_extent_or_points(
        self,
        dictionary,
        value_key,
        annotation_key,
        connection_boolean,
        delta_x_coo,
        num_of_bldg_ghe_group,
        component_type,
        adj_ghe_num_grp_for_diagram_only=None):
    # component_type ("District System" or "Building" or "diagram") (may also be "district_loop" but for now it is not used)
    if component_type == "District System":
        adj_ghe_num_grp_for_diagram_only = adj_ghe_num_grp_for_diagram_only
    elif component_type == "Building" or component_type == "district_loop" or component_type == "diagram":
        adj_ghe_num_grp_for_diagram_only = num_of_bldg_ghe_group
    for key, value in dictionary.items():
        for idx, point in enumerate(value[value_key]):
            point_x = point[0] + (delta_x_coo * adj_ghe_num_grp_for_diagram_only)
            point_y = point[1]
            if idx == 0:
                if "points_no_change" in dictionary[key].keys() and component_type + "_extent" == "diagram_extent":
                    point_value = "{" + str(point_x) + "," + str(point_y) + "}}"
                    point_value = value["points_no_change"] + point_value
                else:
                    point_value = "{{" + str(point_x) + "," + str(point_y) + "},{"
            elif idx == len(value[value_key]) - 1:
                if connection_boolean:
                    if "points_no_change" in dictionary[key].keys():
                        point_value = point_value + str(point_x) + "," + str(point_y) + "}" + value["points_no_change"] + value["color"]
                    else:
                        point_value = point_value + str(point_x) + "," + str(point_y) + "}}" + value["color"]
                else:
                    point_value = point_value + str(point_x) + "," + str(point_y) + "}}"
            else:
                point_value = point_value + str(point_x) + "," + str(point_y) + "},{"

        if component_type == "Building":
            self.bldg_groups_by_num[num_of_bldg_ghe_group][annotation_key][key] = {value_key: point_value}
        elif component_type == "District System":
            self.ghe_groups_by_num[num_of_bldg_ghe_group][annotation_key][key] = {value_key: point_value}
        elif component_type == "diagram":
            self.diagram_single_component_dict[component_type][annotation_key][key] = {value_key: point_value}


def move_bldg_ghe_grp_diagram_origin(
        self,
        dictionary,
        value_key,
        annotation_key,
        connection_boolean,
        delta_x_coo,
        num_of_bldg_ghe_group,
        component_type,
        origin_adjust_boolean=False,
        adj_ghe_num_grp_for_diagram_only=None):
    # component_type ("District System" or "district_loop") (may also be "Building" or "diagram" but for now they are not used)
    if component_type == "District System":
        adj_ghe_num_grp_for_diagram_only = adj_ghe_num_grp_for_diagram_only
    elif component_type == "Building" or component_type == "district_loop" or component_type == "diagram":
        adj_ghe_num_grp_for_diagram_only = num_of_bldg_ghe_group
    for key, value in dictionary.items():
        for idx, point in enumerate(value[value_key]):
            point_x = point[0]
            point_y = point[1]
            rotation_adjusted = dictionary[key]["rotation"]
            if idx == 0:
                point_value = "{{" + str(point_x) + "," + str(point_y) + "},{"
            else:
                point_y_org = value["origin"][1]
                if origin_adjust_boolean:
                    point_x_org = value["origin"][0] + (delta_x_coo * adj_ghe_num_grp_for_diagram_only)
                else:
                    point_x_org = value["origin"][0]
                point_value = point_value + str(point_x) + "," + str(point_y) + "}},rotation=" + \
                    str(rotation_adjusted) + ",origin={" + str(point_x_org) + "," + str(point_y_org) + "}"

            if component_type == "District System":
                self.ghe_groups_by_num[num_of_bldg_ghe_group][annotation_key][key] = {value_key: point_value}
            elif component_type == "district_loop":
                self.diagram_single_component_dict[component_type][annotation_key][key] = {value_key: point_value}


class District:
    """
    Class for modeling entire district energy systems
    """

    def __init__(self, root_dir, project_name, system_parameters, coupling_graph, **kwargs):
        self._scaffold = Scaffold(root_dir, project_name)
        self.system_parameters = system_parameters
        self._coupling_graph = coupling_graph
        self.district_model_dirpath = None
        # Modelica can't handle spaces in project name or path
        if (len(str(root_dir).split()) > 1) or (len(str(project_name).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{root_dir}' for run path and {project_name} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")
        # reads variables from test_borefield.py
        self.borehole_pipe_arrangement = kwargs.get('borehole_pipe_arrangement')
        self.borefield_borehole_configuration_type = kwargs.get('borefield_borehole_configuration_type')
        self.borefield_id = kwargs.get('borefield_id')
        # reads variables from test_district_multiple_ghe.py
        self.coupling_graph_time_series = kwargs.get('coupling_graph_time_series')
        self.num_of_bldg_groups = kwargs.get('num_of_bldg_groups')
        self.bldg_groups_by_num = kwargs.get('bldg_groups_by_num')
        self.num_of_ghe_groups = kwargs.get('num_of_ghe_groups')
        self.ghe_groups_by_num = kwargs.get('ghe_groups_by_num')

    def to_modelica(self):
        """Generate modelica files for the models as well as the modelica file for
        the entire district system.
        """
        # scaffold the project
        self._scaffold.create()
        self.district_model_dirpath = Path(self._scaffold.districts_path.files_dir)

        # create the root package
        root_package = PackageParser.new_from_template(
            self._scaffold.project_path, self._scaffold.project_name, order=[])
        root_package.save()

        # generate model modelica files
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        # generate model_time_series modelica files
        # only needed to create time series loads modelica://district_multiple_ghe/Loads/Resources/Data/[building_geojson_id]/*.mos
        # check if *.mos files can be created another way
        # "time series of the buildings" removed from self._coupling_graph
        # the if statement avoids error when running test_borefield.py
        if self._scaffold.project_name == "district_multiple_ghe":
            for model_time_series in self.coupling_graph_time_series.models:
                model_time_series.to_modelica(self._scaffold)

        # construct graph of visual components
        diagram = Diagram(self._coupling_graph)

        # Load system parameters
        sys_params_buildings = self.system_parameters.get_param('$.buildings')
        sys_params_district_system = self.system_parameters.get_param('$.district_system')
        sys_params_ghe_parameters = self.system_parameters.get_param('$.district_system.fifth_generation.ghe_parameters')
        sys_params_ghe_specific_params = self.system_parameters.get_param(
            "$.district_system.fifth_generation.ghe_parameters.ghe_specific_params")
        sys_params_pipe = self.system_parameters.get_param("$.district_system.fifth_generation.ghe_parameters.pipe")

        if self._scaffold.project_name == "district_multiple_ghe":

            for num_of_bldg_group in range(self.num_of_bldg_groups):
                list_of_time_series_file_paths = []
                sys_params_bldgs_grp = []
                for bldg_id_in_grp in self.bldg_groups_by_num[num_of_bldg_group]["lst_bldg_ids_in_group"]:
                    for sys_params_bldg in sys_params_buildings:
                        if sys_params_bldg["geojson_id"] == bldg_id_in_grp:
                            sys_params_bldgs_grp.append(sys_params_bldg)

                # Flip matrix of sys_params_buildings to create a list for each
                # parameter that collects parameter values for all buildings in building_group
                flipped_sys_params_buildings = flip_matrix(sys_params_bldgs_grp)
                for i_idx, i_value in enumerate(flipped_sys_params_buildings["load_model_parameters"]["time_series"]["filepath"]):
                    path_time_series = Path(i_value)
                    mos_file_path_split = os.path.split(path_time_series)
                    time_series_file_path = "modelica://" + self._scaffold.project_name + "/Loads/Resources/Data/B" + \
                        flipped_sys_params_buildings["geojson_id"][i_idx] + "/" + mos_file_path_split[1]
                    list_of_time_series_file_paths.append(time_series_file_path)

                self.bldg_groups_by_num[num_of_bldg_group]["list_of_time_series_file_paths"] = list_of_time_series_file_paths

        if self._scaffold.project_name == "district_multiple_ghe":
            # creates lists of ghe system parameters of interest (e.g., "length_of_boreholes") by group number
            # E.g., if there are two ghes within one group, the list of ghe system parameters will contain two values of "length_of_boreholes"
            # order of ghes within list is maintained, i.e., item one in any list
            # within the self.ghe_groups_by_num[num_of_ghe_group] belongs to the same
            # ghe
            for num_of_ghe_group in range(self.num_of_ghe_groups):
                self.ghe_groups_by_num[num_of_ghe_group]["lst_length_of_boreholes_in_group"] = []
                self.ghe_groups_by_num[num_of_ghe_group]["lst_number_of_boreholes_in_group"] = []
                self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_buried_depth_in_group"] = []
                self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_diameter_in_group"] = []
                # iterates on list of ghe ids in one ghe group at a time
                for ghe_id_in_grp in self.ghe_groups_by_num[num_of_ghe_group]["lst_ghe_ids_in_group"]:
                    # iterates on all ghes within system paramaters file
                    for sys_params_of_ghe in sys_params_ghe_specific_params:
                        # if this is true, then this is the instance of ghe of interest, thus, we collect its parameters
                        if ghe_id_in_grp == sys_params_of_ghe["ghe_id"]:
                            self.ghe_groups_by_num[num_of_ghe_group]["lst_length_of_boreholes_in_group"].append(
                                sys_params_of_ghe["borehole"]["length_of_boreholes"])
                            self.ghe_groups_by_num[num_of_ghe_group]["lst_number_of_boreholes_in_group"].append(
                                sys_params_of_ghe["borehole"]["number_of_boreholes"])
                            self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_buried_depth_in_group"].append(
                                sys_params_of_ghe["borehole"]["buried_depth"])
                            self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_diameter_in_group"].append(
                                sys_params_of_ghe["borehole"]["diameter"])

        # Flip matrix of sys_params_ghe_specific_params to create a list for each
        # parameter that collects parameter values for all borefields
        flipped_sys_params = flip_matrix(sys_params_ghe_specific_params)

        # number of unique buildings in system_params_ghe.json
        number_of_buildings = len(sys_params_buildings)

        if self._scaffold.project_name == "district_multiple_ghe":
            for num_of_ghe_group in range(self.num_of_ghe_groups):

                self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_design_flow_rate_in_group"] = []

                # number of unique borefields in system_params_ghe.json
                number_of_borefields_in_grp = self.ghe_groups_by_num[num_of_ghe_group]["num_ghes_in_group"]

                # process nominal mass flow rate
                if sys_params_ghe_parameters["design"]["flow_type"] == "system":
                    self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_design_flow_rate_in_group"] = [
                        sys_params_ghe_parameters["design"]["flow_rate"] / x for x in self.ghe_groups_by_num[num_of_ghe_group]["lst_number_of_boreholes_in_group"]]
                else:
                    self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_design_flow_rate_in_group"] = [
                        sys_params_ghe_parameters["design"]["flow_rate"]] * number_of_borefields_in_grp
        else:

            # number of unique borefields in system_params_ghe.json
            number_of_borefields = len(sys_params_ghe_specific_params)

            # process nominal mass flow rate
            if sys_params_ghe_parameters["design"]["flow_type"] == "system":
                design_flow_rate = [sys_params_ghe_parameters["design"]["flow_rate"]
                                    / x for x in flipped_sys_params["borehole"]["number_of_boreholes"]]
            else:
                design_flow_rate = [sys_params_ghe_parameters["design"]["flow_rate"]] * number_of_borefields

        if self._scaffold.project_name == "district_multiple_ghe":
            # calculate sum of design_flow_rate in all borfields in system
            borefield_design_flow_rate_temp = []
            for num_of_ghe_group in range(self.num_of_ghe_groups):
                for idx_ghe_in_group, borehole_design_flow_rate_in_group in enumerate(
                        self.ghe_groups_by_num[num_of_ghe_group]["lst_borehole_design_flow_rate_in_group"]):
                    borefield_design_flow_rate_temp.append(
                        borehole_design_flow_rate_in_group
                        * self.ghe_groups_by_num[num_of_ghe_group]["lst_number_of_boreholes_in_group"][idx_ghe_in_group])
            sum_design_flow_rate_all_borfields = sum(borefield_design_flow_rate_temp)

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

        if self._scaffold.project_name == "district_multiple_ghe":
            for num_of_ghe_group in range(self.num_of_ghe_groups):
                lst_ghe_ids_in_group = self.ghe_groups_by_num[num_of_ghe_group]["lst_ghe_ids_in_group"]
                # returns number of rows in Gfunction.csv and the pd.read_csv of Gfunction.csv
                self.ghe_groups_by_num[num_of_ghe_group]["ghe_dir_gfunction_file_rows"], self.ghe_groups_by_num[num_of_ghe_group]["list_of_gfunctions"] = process_gfunction_file(
                    self, lst_ghe_ids_in_group, sys_params_ghe_parameters)

        ghe_dir_gfunction_file_rows, list_of_gfunctions = process_gfunction_file(
            self, flipped_sys_params["ghe_id"], sys_params_ghe_parameters)

        # start code block 1

        # diagram parameters for some components/connections (maybe temporary, check if diagram.py can be used instead of this)
        if self._scaffold.project_name == "district_multiple_ghe":
            # value to adjust components/connections x coordinate
            bldg_delta_x_coo = 160
            ghe_delta_x_coo = 160

            # adjusting diagram for some components (placement with extent)
            # diagram parameters if there is only one building group
            diagram_bldg_components_dict = {
                "dis": {"extent_coo": [[-20, -60], [20, -40]]},
                "bui": {"extent_coo": [[-10, 110], [10, 130]]},
                "THeaWatSupMaxSet": {"extent_coo": [[-120, 180], [-100, 200]]},
                "TChiWatSupSet": {"extent_coo": [[-120, 140], [-100, 160]]},
                "THeaWatSupMinSet": {"extent_coo": [[-120, 220], [-100, 240]]},
                "THotWatSupSet": {"extent_coo": [[-120, 100], [-100, 120]]},
                "TColWat": {"extent_coo": [[-120, 60], [-100, 80]]},
                "datDes": {"extent_coo": [[-120, 260], [-100, 280]]},
                "TDisWatSup": {"extent_coo": [[-60, -60], [-40, -40]]}
            }

            diagram_ghe_components_dict = {
                "borFieUTubDat": {"extent_coo": [[-110, -150], [-90, -130]]},
                "borFieUTub": {"extent_coo": [[-70, -110], [-50, -90]]},
                "TUTubIn": {"extent_coo": [[-110, -110], [-90, -90]]}
            }

            diagram_components_dict = {
                "diagram_extent": {"extent_coo": [[160, 300]], "points_no_change": "{{-320,-200},"},
            }

            # adjusting diagram for some connections
            # diagram parameters if there is only one building group
            diagram_bldg_connections_dict = {
                "THeaWatSupMaxSet_buiGrp": {"points": [[-104, 58], [-46, 58], [-46, 7], [-12, 7]], "color": ",color={0,0,127}"},
                "THeaWatSupMinSet_buiGrp": {"points": [[-104, 94], [-40, 94], [-40, 9], [-12, 9]], "color": ",color={0,0,127}"},
                "TChiWatSupSet_buiGrp": {"points": [[-104, 22], [-54, 22], [-54, 5], [-12, 5]], "color": ",color={0,0,127}"},
                "THotWatSupSet_buiGrp": {"points": [[-104, -18], [-46, -18], [-46, 3], [-12, 3]], "color": ",color={0,0,127}"},
                "TColWat_buiGrp": {"points": [[-104, -56], [-8, -56], [-8, -12]], "color": ",color={0,0,127}"},
                "buiGrp_disGrp": {"points": [[10, 0], [28, 0], [28, -22], [12, -22], [12, -32]], "color": ",color={0,127,255}"},
                "disGrp_buiGrp": {"points": [[-12, -40], [-12, -20], [-30, -20], [-30, 120], [-10, 120]], "color": ",color={0,127,255}"},
                "bou_pumDis": {"points": [[120, -110], [90, -110], [90, -150]], "color": ",color={0,127,255}"},
                "disGrp_TDisWatRet": {"points": [[20, -50], [40, -50]], "color": ",color={0,127,255}"},
                "TDisWatRet_pumDis": {"points": [[60, -50], [90, -50], [90, -150]], "color": ",color={0,127,255}"},
                "pumDis_disStoGrp": {"points": [[90, -160], [90, -190]], "points_no_change": ",{-180,-190},{-180,-50},{-120,-50}}", "color": ",color={0,127,255}"},
                "disStoGrp_TDisWatSup": {"points": [[-80, -50], [-60, -50]], "color": ",color={0,127,255}"},
                "TDisWatSup_disGrp": {"points": [[-40, -50], [-20, -50]], "color": ",color={0,127,255}"},
                "disGrp_disStoGrp": {"points": [[20, -50], [40, -50]], "color": ",color={0,127,255}"},
            }

            diagram_ghe_connections_dict = {
                "disStoGrp_pumStoGrp": {"points": [[-112, -60], [-112, -80], [-160, -80], [-160, -100], [-150, -100]], "color": ",color={0,127,255}"},
                "pumStoGrp_TUTubInGrp": {"points": [[-130, -100], [-110, -100]], "color": ",color={0,127,255}"},
                "TUTubInGrp_borFieUTubGrp": {"points": [[-90, -100], [-70, -100]], "color": ",color={0,127,255}"},
                "borFieUTubGrp_disStoGrp": {"points": [[-50, -100], [-40, -100], [-40, -80], [-88, -80], [-88, -60]], "color": ",color={0,127,255}"},
                "gai_pumStoGrp": {"points": [[-140, -110], [-140, -160]], "points_no_change": ",{-220,-160}}", "color": ",color={0,0,127}"},
            }

            # adjusting diagram for some components (placement with rotation and origin)
            # diagram parameters if there is only one building group
            diagram_district_loop_components_origin_dict = {
                "bou": {"extent_coo": [[-10, -10], [10, 10]], "rotation": 180, "origin": [130, -110]},
                "pumDis": {"extent_coo": [[10, -10], [-10, 10]], "rotation": 90, "origin": [90, -160]},
                "TDisWatRet": {"extent_coo": [[10, 10], [-10, -10]], "rotation": 180, "origin": [50, -50]},
            }

            diagram_ghe_components_origin_dict = {
                "pumSto": {"extent_coo": [[10, -10], [-10, 10]], "rotation": 180, "origin": [-140, -100]},
                "disSto": {"extent_coo": [[20, -10], [-20, 10]], "rotation": 180, "origin": [-100, -50]},
            }

            self.diagram_single_component_dict = {"district_loop": {"Placement": dict()}, "diagram": {"Placement": dict()}}

            for num_of_bldg_group in range(self.num_of_bldg_groups):
                self.bldg_groups_by_num[num_of_bldg_group]["Placement"] = dict()
                self.bldg_groups_by_num[num_of_bldg_group]["Line"] = dict()

                # adjusting diagram for some components (placement with extent)
                move_bldg_ghe_grp_diagram_extent_or_points(
                    self,
                    diagram_bldg_components_dict,
                    "extent_coo",
                    "Placement",
                    False,
                    bldg_delta_x_coo,
                    num_of_bldg_group,
                    "Building")

                # adjusting diagram for some connections
                move_bldg_ghe_grp_diagram_extent_or_points(
                    self,
                    diagram_bldg_connections_dict,
                    "points",
                    "Line",
                    True,
                    bldg_delta_x_coo,
                    num_of_bldg_group,
                    "Building")

                # adjusting diagram for some district loop components (placement with rotation and origin)
                # these are components that are not within a "Building" or "District System" group
                if num_of_bldg_group == self.num_of_bldg_groups - 1:
                    move_bldg_ghe_grp_diagram_origin(
                        self,
                        diagram_district_loop_components_origin_dict,
                        "extent_coo",
                        "Placement",
                        False,
                        bldg_delta_x_coo,
                        num_of_bldg_group,
                        "district_loop",
                        True)
                    move_bldg_ghe_grp_diagram_extent_or_points(
                        self,
                        diagram_components_dict,
                        "extent_coo",
                        "Placement",
                        False,
                        bldg_delta_x_coo,
                        num_of_bldg_group,
                        "diagram")

            for num_of_ghe_group in range(self.num_of_ghe_groups):
                self.ghe_groups_by_num[num_of_ghe_group]["Placement"] = dict()
                self.ghe_groups_by_num[num_of_ghe_group]["Line"] = dict()

                # this allows putting the ghe in the correct Placement in the diagram (only needed for ghe)
                adj_ghe_num_grp_for_diagram_only = self.ghe_groups_by_num[num_of_ghe_group]["building_group_out"]

                # adjusting diagram for some components (placement with extent)
                move_bldg_ghe_grp_diagram_extent_or_points(
                    self,
                    diagram_ghe_components_dict,
                    "extent_coo",
                    "Placement",
                    False,
                    ghe_delta_x_coo,
                    num_of_ghe_group,
                    "District System",
                    adj_ghe_num_grp_for_diagram_only)

                # adjusting diagram for some connections
                move_bldg_ghe_grp_diagram_extent_or_points(
                    self,
                    diagram_ghe_connections_dict,
                    "points",
                    "Line",
                    True,
                    ghe_delta_x_coo,
                    num_of_ghe_group,
                    "District System",
                    adj_ghe_num_grp_for_diagram_only)

                # adjusting diagram for some components (placement with rotation and origin)
                move_bldg_ghe_grp_diagram_origin(
                    self,
                    diagram_ghe_components_origin_dict,
                    "extent_coo",
                    "Placement",
                    False,
                    ghe_delta_x_coo,
                    num_of_ghe_group,
                    "District System",
                    True,
                    adj_ghe_num_grp_for_diagram_only)

        # end code block 1

        # create borefield package paths
        b_modelica_path = ModelicaPath(model.borefield_name, self._scaffold.plants_path.files_dir, True)

        if self._scaffold.project_name == "district_multiple_ghe":

            for num_of_ghe_group in range(self.num_of_ghe_groups):
                self.ghe_groups_by_num[num_of_ghe_group]["list_of_gfunction_file_paths"] = process_gfunction(
                    self.ghe_groups_by_num[num_of_ghe_group]["list_of_gfunctions"],
                    self.ghe_groups_by_num[num_of_ghe_group]["lst_length_of_boreholes_in_group"],
                    self.ghe_groups_by_num[num_of_ghe_group]["lst_number_of_boreholes_in_group"],
                    sys_params_ghe_parameters,
                    b_modelica_path,
                    self._scaffold.project_name,
                    self.ghe_groups_by_num[num_of_ghe_group]["lst_ghe_ids_in_group"])

        else:
            list_of_gfunction_file_paths = process_gfunction(
                list_of_gfunctions,
                flipped_sys_params["borehole"]["length_of_boreholes"],
                flipped_sys_params["borehole"]["number_of_boreholes"],
                sys_params_ghe_parameters,
                b_modelica_path,
                self._scaffold.project_name,
                flipped_sys_params["ghe_id"])

        district_template_params = {
            "district_within_path": '.'.join([self._scaffold.project_name, 'Districts']),
            "diagram": diagram,
            "couplings": [],
            "models": [],
            "is_ghe_district": self.system_parameters.get_param('$.district_system.fifth_generation.ghe_parameters'),
            "project_name": self._scaffold.project_name
        }

        if self._scaffold.project_name == "district_multiple_ghe":
            district_template_params["list_instance_template_files_of_models"] = []
            district_template_params["num_buildings"] = number_of_buildings
            district_template_params["list_of_time_series_file_paths"] = list_of_time_series_file_paths
            district_template_params["num_of_bldg_groups"] = self.num_of_bldg_groups
            district_template_params["bldg_groups_by_num"] = self.bldg_groups_by_num
            district_template_params["num_of_ghe_groups"] = self.num_of_ghe_groups
            district_template_params["ghe_groups_by_num"] = self.ghe_groups_by_num
            district_template_params["diagram_single_component_dict"] = self.diagram_single_component_dict
            district_template_params["sum_design_flow_rate_all_borfields"] = sum_design_flow_rate_all_borfields

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
                "num_buildings": number_of_buildings,
                "borehole_pipe_arrangement": self.borehole_pipe_arrangement,
                "borefield_borehole_configuration_type": self.borefield_borehole_configuration_type,
                'flipped_sys_params': flipped_sys_params,
                "pipe_thickness": pipe_thickness,
                "pipe_shank_spacing": pipe_shank_spacing,
                "ghe_dir_gfunction_file_rows": ghe_dir_gfunction_file_rows,
                "project_name": self._scaffold.project_name,
                "borefield_name": model.borefield_name,
                "borefield_id": self.borefield_id
            }
        }

        if self._scaffold.project_name == "district_multiple_ghe":
            common_template_params["sys_params"]["num_of_bldg_groups"] = self.num_of_bldg_groups
            common_template_params["sys_params"]["bldg_groups_by_num"] = self.bldg_groups_by_num
            common_template_params["sys_params"]["num_of_ghe_groups"] = self.num_of_ghe_groups
            common_template_params["sys_params"]["ghe_groups_by_num"] = self.ghe_groups_by_num
            common_template_params["sys_params"]["diagram_single_component_dict"] = self.diagram_single_component_dict
        else:
            common_template_params["sys_params"]["number_of_borefields"] = number_of_borefields
            common_template_params["sys_params"]["design_flow_rate"] = design_flow_rate
            common_template_params["sys_params"]["list_of_gfunction_file_paths"] = list_of_gfunction_file_paths

        list_of_updated_couplings = []

        if self._scaffold.project_name == "district_multiple_ghe":
            # add one of the time series couplings to be rendered
            couplings_with_one_time_series = [self.coupling_graph_time_series.couplings[0]]
            for i in self._coupling_graph.couplings:
                couplings_with_one_time_series.append(i)
            for j in couplings_with_one_time_series:
                list_of_updated_couplings.append(j)
        else:
            for j in self._coupling_graph.couplings:
                list_of_updated_couplings.append(j)

        # render each coupling
        load_num = 1
        for coupling in list_of_updated_couplings:
            ######################
            # !!!!important!!!! the following if statement is most probably wrong, however, it is used as a temporary solution
            # this is a coupling despite what it say, this is a work around needed to create arrays of time series for buildings
            ######################
            if self._scaffold.project_name == "district_multiple_ghe":
                template_context = {
                    'diagram': diagram.to_dict(coupling.id, is_coupling=False),
                }
            else:
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

        if self._scaffold.project_name == "district_multiple_ghe":
            for model_i in district_template_params['models']:
                instance_template_path_split = os.path.split(model_i["instance_template_path"])
                district_template_params["list_instance_template_files_of_models"].append(instance_template_path_split[1])

        district_package_order = ['DistrictEnergySystem']

        # render the full district file
        if 'fifth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem5G.mot', district_template_params)
            # write an additional mofile for ghe systems
            if self._scaffold.project_name == "district_multiple_ghe":
                partial_district_template = 'DistrictEnergySystem_ghe_partial.mot'
                # PartialSeries is the Modelica name of the partial model template
                district_package_order.append('DistrictEnergySystem_ghe_partial')
                mofile_name = partial_district_template.rstrip('t')
                district_mofile = render_template(partial_district_template, district_template_params)
                with open(f'{self.district_model_dirpath}/{mofile_name}', 'w') as f:
                    f.write(district_mofile)
        elif 'fourth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem.mot', district_template_params)
        with open(f'{self.district_model_dirpath}/DistrictEnergySystem.mo', 'w') as f:
            f.write(final_result)

        # PartialSeries is the Modelica name of the partial model
        districts_package = PackageParser.new_from_template(
            self._scaffold.districts_path.files_dir,
            "Districts",
            district_package_order,
            within=f"{self._scaffold.project_name}"
        )
        districts_package.save()

        root_package = PackageParser(self._scaffold.project_path)
        if 'Districts' not in root_package.order:
            root_package.add_model('Districts')
            root_package.save()
