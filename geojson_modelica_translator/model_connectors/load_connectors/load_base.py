"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""
from pathlib import Path

from geojson_modelica_translator.model_connectors.model_base import ModelBase
from geojson_modelica_translator.utils import convert_c_to_k


class LoadBase(ModelBase):
    """
    Base class of the load connectors.
    """
    simple_gmt_type = 'load'

    def __init__(self, system_parameters, geojson_load):
        """
        Base class for load connectors.

        :param system_parameters: SystemParameter object, the entire system parameter file which will be used to
                                  generate this load.
        :param geojson_load: dict, the GeoJSON portion of the load to be added (a single feature).
                             This is now a required field.
        """
        super().__init__(system_parameters, Path(__file__).parent / 'templates')

        # previously geojson_load could be None, prevent that now.
        if geojson_load is None:
            raise SystemExit('Error initializing LoadBase with empty GeoJSON')

        # we have to resolve some naming/object issues, there is a GeoJSON load, an URBANopt Building, and then the
        # building object. Ideally we have only one, but we need to investigate that. The UOBuilding allows for
        # access such as building.feature.properties.
        self.building_id = geojson_load.feature.properties["id"]
        self.building = self.add_building(geojson_load)

        # This ets_template_data gets added to building_template_data when the template is run
        # First if statement is for cases of no sys-param file provided
        # Second if statement is for cases of a sys-param file not including ets data
        # TODO: Decide if we're requiring sys-param file, and if all loads have an ets.
        # test_base.py and test_time_series.py test these cases
        if system_parameters is not None:
            if self.system_parameters.get_param_by_building_id(
                    self.building_id, "ets_model_parameters.indirect") is not None:
                self.ets_template_data = {
                    "heat_flow_nominal": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heat_flow_nominal"
                    ),
                    "heat_exchanger_efficiency": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heat_exchanger_efficiency"
                    ),
                    "nominal_mass_flow_district": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.nominal_mass_flow_district"
                    ),
                    "nominal_mass_flow_building": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.nominal_mass_flow_building"
                    ),
                    "valve_pressure_drop": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.valve_pressure_drop"
                    ),
                    "heat_exchanger_secondary_pressure_drop": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heat_exchanger_secondary_pressure_drop"
                    ),
                    "heat_exchanger_primary_pressure_drop": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heat_exchanger_primary_pressure_drop"
                    ),
                    "cooling_supply_water_temperature_building": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.cooling_supply_water_temperature_building"
                    )),
                    "heating_supply_water_temperature_building": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heating_supply_water_temperature_building"
                    )),
                    "delta_temp_chw_building": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.delta_temp_chw_building"
                    ),
                    "delta_temp_chw_district": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.delta_temp_chw_district"
                    ),
                    "delta_temp_hw_building": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.delta_temp_hw_building"
                    ),
                    "delta_temp_hw_district": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.delta_temp_hw_district"
                    ),
                    "cooling_controller_y_max": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.cooling_controller_y_max"
                    ),
                    "cooling_controller_y_min": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.cooling_controller_y_min"
                    ),
                    "heating_controller_y_max": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heating_controller_y_max"
                    ),
                    "heating_controller_y_min": self.system_parameters.get_param_by_building_id(
                        self.building_id, "ets_model_parameters.indirect.heating_controller_y_min"
                    )
                }
            else:
                # If no ets, use default values from gmt/system_parameters/schema.json
                # TODO: If we end up having a bunch of these, we should probably pull the values from the schema
                # itself, instead of duplicating them here in hardcode.
                self.ets_template_data = {}
                self.ets_template_data['delta_temp_chw_building'] = 5

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the load to be translated. This is simply a helper method.

        :param urbanopt_building: an urbanopt_building (also known as a geojson_load)
        :param mapper: placeholder object for mapping between urbanopt_building and load_connector building.
        """

        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            if self.system_parameters:
                for building in self.system_parameters.get_default('$.buildings.custom', []):
                    # Only look at buildings in the sys-param file, not necessarily the entire feature file
                    if urbanopt_building.feature.properties["id"] == building["geojson_id"]:
                        try:
                            self.building_id = urbanopt_building.feature.properties["id"]
                            building_type = urbanopt_building.feature.properties["building_type"]
                            number_stories = urbanopt_building.feature.properties["number_of_stories"]
                            building_floor_area_m2 = self.ft2_to_m2(urbanopt_building.feature.properties["floor_area"])
                        except KeyError as ke:
                            raise SystemExit(f'\nMissing property {ke} for building {self.building_id} in geojson feature file')

                        try:
                            number_stories_above_ground = urbanopt_building.feature.properties["number_of_stories_above_ground"]
                        except KeyError:
                            number_stories_above_ground = number_stories
                            print(f"\nAssuming all building levels are above ground for building_id: {self.building_id}")

                        try:
                            floor_height = urbanopt_building.feature.properties["floor_height"]
                        except KeyError:
                            floor_height = 3  # Default height in meters from sdk
                            print(
                                f"No floor_height found in geojson feature file for building {self.building_id}. "
                                f"Using default value of {floor_height}.")

                        # UO SDK defaults to current year, however TEASER only supports up to Year 2015
                        # https://github.com/urbanopt/TEASER/blob/master/teaser/data/input/inputdata/TypeBuildingElements.json#L818
                        try:
                            year_built = urbanopt_building.feature.properties["year_built"]
                            if urbanopt_building.feature.properties["year_built"] > 2015:
                                year_built = 2015
                        except KeyError:
                            year_built = 2015
                            print(
                                f"No year_built found in geojson feature file for building {self.building_id}. "
                                f"Using default value of {year_built}.")

                        try:
                            return {
                                "building_id": self.building_id,
                                "area": building_floor_area_m2,
                                "building_type": building_type,
                                "floor_height": floor_height,
                                "num_stories": number_stories,
                                "num_stories_below_grade": number_stories - number_stories_above_ground,
                                "year_built": year_built,
                            }
                        except UnboundLocalError:
                            print(
                                f"Geojson feature file is missing data for building {self.building_id}. "
                                "This may be caused by referencing a detailed osm in the feature file.")
                    else:
                        continue

        else:
            raise SystemExit(f"Mapper {mapper} has been used")

    @property
    def building_name(self):
        # teaser will prepend a "B" if the name is numeric, so accounting for that
        if self.building_id[0].isnumeric():
            return f"B{self.building_id}"

        return self.building_id
