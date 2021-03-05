"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the load to be translated. This is simply a helper method.

        :param urbanopt_building: an urbanopt_building (also known as a geojson_load)
        :param mapper: placeholder object for mapping between urbanopt_building and load_connector building.
        """

        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            # Only look at buildings in the sys-param file, not necessarily the entire feature file
            for building in self.system_parameters.get_default('$.buildings.custom', []):
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
                            f"\nNo floor_height found in geojson feature file for building {self.building_id}. \
                            Using default value of {floor_height}.")

                    # UO SDK defaults to current year, however TEASER only supports up to Year 2015
                    # https://github.com/urbanopt/TEASER/blob/master/teaser/data/input/inputdata/TypeBuildingElements.json#L818
                    try:
                        year_built = urbanopt_building.feature.properties["year_built"]
                        if urbanopt_building.feature.properties["year_built"] > 2015:
                            year_built = 2015
                    except KeyError:
                        year_built = 2015
                        print(
                            f"No 'year_built' found in geojson feature file for building {self.building_id}. \
                            Using default value of {year_built}.")

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
                        print(f"Geojson feature file is missing data for building {self.building_id}. \
                        This may be caused by referencing a detailed osm in the feature file.")
                else:
                    print(
                        f"Building {urbanopt_building.feature.properties['id']} is missing from either \
                            geojson feature file or system parameters file")
                    continue

        else:
            raise SystemExit(f"Mapper {mapper} has been used")

    @property
    def building_name(self):
        return f"B{self.building_id}"
