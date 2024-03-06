# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import copy
import os
from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson, UrbanOptLoad
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district_5g import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


def add_bldg_ghe_group_num(connected_bldgs_and_ghes_by_order_in_loop, feature_type, group_key):
    # the expression fea_typ (feature_type) represents either bldgs or ghes (not both)
    # feature_type ("Building" or "District System")
    # group_key ("building_group" or "ghe_group")
    # creates copy of connected_bldgs_and_ghes_by_order_in_loop, but with only feature_type features
    connected_fea_typ_by_order_in_loop = copy.deepcopy(connected_bldgs_and_ghes_by_order_in_loop)
    for key_connected_bldg_ghe, value_connected_bldg_ghe in connected_bldgs_and_ghes_by_order_in_loop.items():
        if value_connected_bldg_ghe["type"] != feature_type:
            connected_fea_typ_by_order_in_loop.pop(key_connected_bldg_ghe)

    # add group_key to connected_fea_typ_by_order_in_loop dictionary (building groups are separated by ghe,
    # and ghe groups are separated by buildings)
    fea_typ_group_counter = 0
    list_of_sorted_keys_connected_bldgs_ghes = sorted(connected_bldgs_and_ghes_by_order_in_loop.keys())
    list_of_sorted_keys_connected_fea_typ = sorted(connected_fea_typ_by_order_in_loop.keys())
    for idx_connected_fea_typ_1, key_connected_fea_typ_1 in enumerate(list_of_sorted_keys_connected_fea_typ):
        # if first and last feature in the loop is of the same feature_type (e.g., "District System"),
        # this will not give them the same group number, instead the group number will keep counting up for each group
        #  after the first group (i.e., group number for the last group will be higher than for the first group)
        if idx_connected_fea_typ_1 == 0:
            connected_bldgs_and_ghes_by_order_in_loop[key_connected_fea_typ_1][group_key] = fea_typ_group_counter
        else:
            previous_key_connected_fea_typ = list_of_sorted_keys_connected_fea_typ[idx_connected_fea_typ_1 - 1]
            if key_connected_fea_typ_1 - previous_key_connected_fea_typ != 1:
                fea_typ_group_counter += 1
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_fea_typ_1][group_key] = fea_typ_group_counter
            else:
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_fea_typ_1][group_key] = fea_typ_group_counter

    # if first and last feature in the loop is of the same feature_type (e.g., "District System"),
    # this will reset the group number of the last feature to match that of the first feature
    # wrapping mean that first and last feature in the loop is of the same feature_type
    boolean_group_is_wrapping = False
    for connected_fea_typ_2 in list_of_sorted_keys_connected_fea_typ:
        # this is true when first feature in the loop is of the feature_type (e.g., "District System")
        if (
            connected_fea_typ_2 == 0
            and connected_bldgs_and_ghes_by_order_in_loop[list_of_sorted_keys_connected_bldgs_ghes[-1]]["type"]
            == feature_type
        ):
            # this is true when last feature in the loop is of the feature_type (e.g., "District System")
            # if (
            #     connected_bldgs_and_ghes_by_order_in_loop[list_of_sorted_keys_connected_bldgs_ghes[-1]]["type"]
            #     == feature_type
            # ):
            group_key_to_reset = connected_bldgs_and_ghes_by_order_in_loop[
                list_of_sorted_keys_connected_bldgs_ghes[-1]
            ][group_key]
            fea_typ_group_counter -= 1
            boolean_group_is_wrapping = True

        if (
            boolean_group_is_wrapping
            and connected_bldgs_and_ghes_by_order_in_loop[connected_fea_typ_2][group_key] == group_key_to_reset
        ):
            connected_bldgs_and_ghes_by_order_in_loop[connected_fea_typ_2][group_key] = 0

    num_of_fea_typ_groups = fea_typ_group_counter + 1
    return (num_of_fea_typ_groups, boolean_group_is_wrapping)


def add_bldg_ghe_group_in_out(connected_bldgs_and_ghes_by_order_in_loop, feature_type):
    # the expression fea_typ (feature_type) represents either bldgs or ghes (not both)
    # feature_type ("Building" or "District System")
    # add group in and out to each feature (e.g., "building_group_in" and "building_group_out") to
    # connected_bldgs_and_ghes_by_order_in_loop dictionary
    # (building groups are separated by ghe, and ghe groups are separated by buildings)
    if feature_type == "District System":
        group_in_key = "building_group_in"
        group_out_key = "building_group_out"
        key_to_return_group_num = "building_group"
    elif feature_type == "Building":
        group_in_key = "ghe_group_in"
        group_out_key = "ghe_group_out"
        key_to_return_group_num = "ghe_group"
    list_of_sorted_keys_connected_bldgs_ghes = sorted(connected_bldgs_and_ghes_by_order_in_loop.keys())
    for idx_connected_bldg_ghe, key_connected_bldg_ghe in enumerate(list_of_sorted_keys_connected_bldgs_ghes):
        if connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["type"] == feature_type:
            previous_key_connected_bldg_ghe = list_of_sorted_keys_connected_bldgs_ghes[idx_connected_bldg_ghe - 1]
            # if the key of the "Building" or "District System" is the last
            if idx_connected_bldg_ghe == len(list_of_sorted_keys_connected_bldgs_ghes) - 1:
                adjusted_key_next_blg_ghe = (idx_connected_bldg_ghe + 1) - len(list_of_sorted_keys_connected_bldgs_ghes)
            else:
                adjusted_key_next_blg_ghe = idx_connected_bldg_ghe + 1
            next_key_connected_bldg_ghe = list_of_sorted_keys_connected_bldgs_ghes[adjusted_key_next_blg_ghe]

            if connected_bldgs_and_ghes_by_order_in_loop[previous_key_connected_bldg_ghe]["type"] == feature_type:
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe][group_in_key] = None
            else:
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe][group_in_key] = (
                    connected_bldgs_and_ghes_by_order_in_loop[previous_key_connected_bldg_ghe][key_to_return_group_num]
                )

            if connected_bldgs_and_ghes_by_order_in_loop[next_key_connected_bldg_ghe]["type"] == feature_type:
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe][group_out_key] = None
            else:
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe][group_out_key] = (
                    connected_bldgs_and_ghes_by_order_in_loop[next_key_connected_bldg_ghe][key_to_return_group_num]
                )


def dict_bldg_ghe_group_by_num(
    connected_bldgs_and_ghes_by_order_in_loop,
    num_of_fea_typ_groups,
    num_fea_typ_in_group_key,
    feature_type,
    group_key,
    lst_fea_typ_ids_in_group_key,
    boolean_group_is_wrapping,
    group_in_key,
):
    # the expression fea_typ (feature_type) represents either bldgs or ghes (not both)
    # feature_type ("Building" or "District System")
    # num_fea_typ_in_group_key ("num_bldgs_in_group" or "num_ghes_in_group")
    # group_key ("building_group" or "ghe_group")
    # lst_fea_typ_ids_in_group_key ("lst_bldg_ids_in_group" or "lst_ghe_ids_in_group")
    # boolean_group_is_wrapping (boolean_bldg_group_is_wrapping or boolean_ghe_group_is_wrapping)
    # dictionary of building groups by group number
    fea_typ_groups_by_num = {}
    # group_in_key ("building_group_in" or "ghe_group_in")
    group_out_key = group_in_key[:-3] + "_out"
    boolean_separate_first_fea_typ_ids_wrapping = True
    # this is a temporary list needed when a group is wrapping, it includes the ids of the first in loop features
    # of the wrapping group.
    # this list gets appended to the end of the list that has the ids of the last in loop features
    # of the wrapping group
    # this ensures correct order of features
    lst_first_in_loop_fea_typ_ids_wrapping = []
    list_of_sorted_keys_connected_bldgs_ghes = sorted(connected_bldgs_and_ghes_by_order_in_loop.keys())
    for num_of_fea_typ_group in range(num_of_fea_typ_groups):
        lst_fea_typ_ids_in_group = []
        fea_typ_groups_by_num[num_of_fea_typ_group] = {num_fea_typ_in_group_key: None}
        for key_connected_bldg_ghe in list_of_sorted_keys_connected_bldgs_ghes:
            if connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["type"] == feature_type:
                if connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe][group_key] == num_of_fea_typ_group:
                    if boolean_group_is_wrapping:
                        if boolean_separate_first_fea_typ_ids_wrapping:
                            lst_first_in_loop_fea_typ_ids_wrapping.append(
                                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["id"]
                            )
                        else:
                            lst_fea_typ_ids_in_group.append(
                                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["id"]
                            )
                    else:
                        lst_fea_typ_ids_in_group.append(
                            connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["id"]
                        )
            elif boolean_group_is_wrapping:
                boolean_separate_first_fea_typ_ids_wrapping = False
            else:
                pass

        if num_of_fea_typ_group == 0 and boolean_group_is_wrapping:
            fea_typ_groups_by_num[num_of_fea_typ_group][lst_fea_typ_ids_in_group_key] = (
                lst_fea_typ_ids_in_group + lst_first_in_loop_fea_typ_ids_wrapping
            )
        else:
            fea_typ_groups_by_num[num_of_fea_typ_group][lst_fea_typ_ids_in_group_key] = lst_fea_typ_ids_in_group

        fea_typ_groups_by_num[num_of_fea_typ_group][num_fea_typ_in_group_key] = len(
            fea_typ_groups_by_num[num_of_fea_typ_group][lst_fea_typ_ids_in_group_key]
        )

        # add group in and out to group (e.g., "building_group_in" and "building_group_out")
        for key_connected_bldg_ghe in list_of_sorted_keys_connected_bldgs_ghes:
            # this is true when the feature is the first in the group
            if (
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["id"]
                == fea_typ_groups_by_num[num_of_fea_typ_group][lst_fea_typ_ids_in_group_key][0]
            ):
                fea_typ_groups_by_num[num_of_fea_typ_group][group_in_key] = connected_bldgs_and_ghes_by_order_in_loop[
                    key_connected_bldg_ghe
                ][group_in_key]
            # this is true when the feature is the last in the group
            if (
                connected_bldgs_and_ghes_by_order_in_loop[key_connected_bldg_ghe]["id"]
                == fea_typ_groups_by_num[num_of_fea_typ_group][lst_fea_typ_ids_in_group_key][-1]
            ):
                fea_typ_groups_by_num[num_of_fea_typ_group][group_out_key] = connected_bldgs_and_ghes_by_order_in_loop[
                    key_connected_bldg_ghe
                ][group_out_key]

    return fea_typ_groups_by_num


class DistrictSystemTest(TestCaseBase):
    def setUp(self):
        super().setUp()

        project_name = "district_multiple_ghe"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with multiple buildings
        filename = os.path.join(self.data_dir, "network.geojson")

        self.gj = UrbanOptGeoJson(filename)

        # start code block 1
        # a function that manipulates the geojson dictionary might simplify this code
        # (e.g., features by id, "ThermalConnector" by startFeatureId, etc)
        # this needs 1) validation like buildings validation within urbanopt_geojson.py, and
        # 2) checking if code belongs here or in another python module.
        # if code belongs in another python module, it needs to be put there
        # separating features by type
        self.gj.district_systems = []
        self.gj.thermal_connectors = []
        self.gj.thermal_junctions = []
        # list of features that has a type "Building" or "District System"
        # this is created because these features are the ones that get connected in the loop
        lst_bldgs_and_ghes = []
        for feature in self.gj.data.features:
            if feature["properties"]["type"] == "Building":
                lst_bldgs_and_ghes.append(feature)
            elif feature["properties"]["type"] == "District System":
                district_system_temp = UrbanOptLoad(feature)
                self.gj.district_systems.append(district_system_temp)
                lst_bldgs_and_ghes.append(feature)
            elif feature["properties"]["type"] == "ThermalConnector":
                thermal_connector_temp = UrbanOptLoad(feature)
                self.gj.thermal_connectors.append(thermal_connector_temp)
            elif feature["properties"]["type"] == "ThermalJunction":
                thermal_junction_temp = UrbanOptLoad(feature)
                self.gj.thermal_junctions.append(thermal_junction_temp)

        # returns properties of the first "Building" or "District System" in the loop
        for thermal_junction_1 in self.gj.thermal_junctions:
            # if this is true, then the thermal_junction_1 has "is_ghe_start_loop" true
            if (
                "is_ghe_start_loop" in thermal_junction_1.feature["properties"]
                and thermal_junction_1.feature["properties"]["is_ghe_start_loop"]
            ):
                # returns the id of the first feature (i.e., connected to the thermal juntion)
                if "DSId" in thermal_junction_1.feature["properties"]:
                    start_bldg_or_ghe_id = thermal_junction_1.feature["properties"]["DSId"]
                elif "buildingId" in thermal_junction_1.feature["properties"]:
                    start_bldg_or_ghe_id = thermal_junction_1.feature["properties"]["buildingId"]

        # creats dictioary of "Building" and "District System" features
        # returns "Building" and "District System" data using order of feature in the loop
        # (highest-level key of dictionary is order in loop)
        connected_bldgs_and_ghes_by_order_in_loop = {}
        for feature_bldg_or_ghe_idx, feature_bldg_or_ghe in enumerate(lst_bldgs_and_ghes):
            # creating an empty nested dictionary
            connected_bldgs_and_ghes_by_order_in_loop[feature_bldg_or_ghe_idx] = {
                "id": None,
                "type": None,
                "id_ThermalConnector_out": None,
            }
            # filling the data for the first "Building" and "District System" in the loop
            if feature_bldg_or_ghe["properties"]["id"] == start_bldg_or_ghe_id:
                connected_bldgs_and_ghes_by_order_in_loop[0]["id"] = start_bldg_or_ghe_id
                connected_bldgs_and_ghes_by_order_in_loop[0]["type"] = feature_bldg_or_ghe["properties"]["type"]

        # return first thermal connector id
        # (continues filling the data for the first "Building" and "District System" in the loop)
        for thermal_connector_1 in self.gj.thermal_connectors:
            if thermal_connector_1.feature["properties"]["startFeatureId"] == start_bldg_or_ghe_id:
                connected_bldgs_and_ghes_by_order_in_loop[0]["id_ThermalConnector_out"] = thermal_connector_1.feature[
                    "properties"
                ]["id"]

        # returns "Building" and "District System" type using feature id (temporary dictionary)
        bldg_and_ghe_by_id = {}
        for bldg_and_ghe in lst_bldgs_and_ghes:
            bldg_and_ghe_by_id[bldg_and_ghe["properties"]["id"]] = bldg_and_ghe["properties"]["type"]

        # returns "ThermalConnector" id using startFeatureId (temporary dictionary)
        thermal_connectors_by_start_feature_id = {}
        # returns "ThermalConnector" endFeatureId using id (temporary dictionary)
        thermal_connectors_by_id = {}
        # organizing the thermal connectors according to loop order
        for thermal_connector_2 in self.gj.thermal_connectors:
            thermal_connector_id = thermal_connector_2.feature["properties"]["id"]
            thermal_connector_start_feature_id = thermal_connector_2.feature["properties"]["startFeatureId"]
            thermal_connector_end_feature_id = thermal_connector_2.feature["properties"]["endFeatureId"]
            # filling the data in the nested dictionary
            thermal_connectors_by_start_feature_id[thermal_connector_start_feature_id] = {"id": thermal_connector_id}
            # filling the data in the nested dictionary
            thermal_connectors_by_id[thermal_connector_id] = {"endFeatureId": thermal_connector_end_feature_id}

        # fills "Building" and "District System" data in connected_bldgs_and_ghes_by_order_in_loop dictionary
        # (highest-level key of dictionary is order in loop)
        for num_in_loop in range(len(lst_bldgs_and_ghes)):
            if num_in_loop == 0:
                pass
            else:
                # id of "ThermalConnector" connected to previous "Building" or "District System" in the loop
                previous_thermal_connector_id = connected_bldgs_and_ghes_by_order_in_loop[num_in_loop - 1][
                    "id_ThermalConnector_out"
                ]
                # id of next "Building" of "District System" in the loop
                next_bldg_or_ghe_in_loop = thermal_connectors_by_id[previous_thermal_connector_id]["endFeatureId"]
                # id of "ThermalConnector" connected to next "Building" or "District System" in the loop
                next_thermal_connector_in_loop = thermal_connectors_by_start_feature_id[next_bldg_or_ghe_in_loop]["id"]
                # filling the data in the nested dictionary
                connected_bldgs_and_ghes_by_order_in_loop[num_in_loop]["id"] = next_bldg_or_ghe_in_loop
                connected_bldgs_and_ghes_by_order_in_loop[num_in_loop]["type"] = bldg_and_ghe_by_id[
                    next_bldg_or_ghe_in_loop
                ]
                connected_bldgs_and_ghes_by_order_in_loop[num_in_loop]["id_ThermalConnector_out"] = (
                    next_thermal_connector_in_loop
                )

        # end code block 1

        # start code block 2

        # does three things:
        # 1) add group number in connected_bldgs_and_ghes_by_order_in_loop ("building_group" or "ghe_group")
        # 2) returns number of groups for each feature_type ("Building" or "District System")
        # 3) returns if group is wrapping, i.e., that first and last feature in the loop is of the same feature_type
        # ("Building" or "District System")
        num_of_bldg_groups, boolean_bldg_group_is_wrapping = add_bldg_ghe_group_num(
            connected_bldgs_and_ghes_by_order_in_loop, "Building", "building_group"
        )
        num_of_ghe_groups, boolean_ghe_group_is_wrapping = add_bldg_ghe_group_num(
            connected_bldgs_and_ghes_by_order_in_loop, "District System", "ghe_group"
        )

        # add group in and out to each feature (e.g., "building_group_in" and "building_group_out") to
        # connected_bldgs_and_ghes_by_order_in_loop dictionary
        # (building groups are separated by ghe, and ghe groups are separated by buildings)
        add_bldg_ghe_group_in_out(connected_bldgs_and_ghes_by_order_in_loop, "District System")
        add_bldg_ghe_group_in_out(connected_bldgs_and_ghes_by_order_in_loop, "Building")

        # end code block 2

        # start code block 3

        # does three things:
        # 1) creates dictionary of feature_type ("Building" or "District System") by group number
        # 2) adds num_fea_typ_in_group_key (e.g., "num_bldgs_in_group") to each group
        # 3) adds lst_fea_typ_ids_in_group_key (e.g., "lst_bldg_ids_in_group") to each group
        bldg_groups_by_num = dict_bldg_ghe_group_by_num(
            connected_bldgs_and_ghes_by_order_in_loop,
            num_of_bldg_groups,
            "num_bldgs_in_group",
            "Building",
            "building_group",
            "lst_bldg_ids_in_group",
            boolean_bldg_group_is_wrapping,
            "ghe_group_in",
        )
        ghe_groups_by_num = dict_bldg_ghe_group_by_num(
            connected_bldgs_and_ghes_by_order_in_loop,
            num_of_ghe_groups,
            "num_ghes_in_group",
            "District System",
            "ghe_group",
            "lst_ghe_ids_in_group",
            boolean_ghe_group_is_wrapping,
            "building_group_in",
        )

        # end code block 3

        # load system parameter data
        filename = os.path.join(self.data_dir, "system_params_ghe.json")
        sys_params = SystemParameters(filename)

        # create borefield
        borefield = Borefield(sys_params)

        # create ambient water stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create the couplings and graph
        # create the couplings and graph for the "time series of the buildings" separately
        # only needed to create time series loads:
        # modelica://district_multiple_ghe/Loads/Resources/Data/[building_geojson_id]/*.mos
        # TODO: check if *.mos files can be created another way
        all_couplings = []
        all_couplings_time_series = []
        for geojson_load in self.gj.buildings:
            time_series_load = TimeSeries(sys_params, geojson_load)
            all_couplings_time_series.append(Coupling(time_series_load, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(borefield, ambient_water_stub, district_type="5G"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="5G"))

        graph = CouplingGraph(all_couplings)
        graph_time_series = CouplingGraph(all_couplings_time_series)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            coupling_graph=graph,
            coupling_graph_time_series=graph_time_series,
            num_of_bldg_groups=num_of_bldg_groups,
            bldg_groups_by_num=bldg_groups_by_num,
            num_of_ghe_groups=num_of_ghe_groups,
            ghe_groups_by_num=ghe_groups_by_num,
            borefield_borehole_configuration_type=borefield.borehole_configuration_type,
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation()
    def test_simulate_district_system(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            run_path=self.district._scaffold.project_path,
            file_to_load=self.district._scaffold.package_path,
        )
