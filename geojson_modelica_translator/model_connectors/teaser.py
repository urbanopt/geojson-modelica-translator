"""
****************************************************************************************************
:copyright (c) 2019 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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


import os
from teaser.project import Project

from geojson_modelica_translator.model_connectors.base import Base as model_connector_base


class TeaserConnector(model_connector_base):
    def __init__(self):
        super().__init__(self)

    def mappings(self):
        """
        :return:
        """
        pass

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.

        :param urbanopt_building: an urbanopt_building
        :return:
        """
        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            self.buildings.append({
                "area": urbanopt_building.feature.properties['floor_area'] * 0.092936,  # ft2 -> m2
                "building_id": urbanopt_building.feature.properties['id'],
                "building_type": urbanopt_building.feature.properties['building_type'],
                "floor_height": urbanopt_building.feature.properties['height'] * 0.3048,  # ft -> m
                "num_stories": urbanopt_building.feature.properties['number_of_stories_above_ground'],
                "num_stories_below_grade": urbanopt_building.feature.properties['number_of_stories'] -
                                           urbanopt_building.feature.properties['number_of_stories_above_ground'],
                "year_built": urbanopt_building.feature.properties['year_built']
            })

    def lookup_building_type(self, building_type):
        if 'office' in building_type.lower():
            return 'office'
        else:
            # TODO: define these mappings 'office', 'institute', 'institute4', institute8'
            return 'office'

    def to_modelica(self, root_building_dir):
        """
        :param root_building_dir: str, root directory where building model will be exported
        :return:
        """
        # Teaser changes the current dir, so make sure to reset it back to where we started
        curdir = os.getcwd()
        try:
            prj = Project(load_data=True)
            # prj.name = self.building_id

            for building in self.buildings:
                prj.add_non_residential(
                    method='bmvbs',
                    usage=self.lookup_building_type(building['building_type']),
                    name=building['building_id'],
                    year_of_construction=building['year_built'],
                    number_of_floors=building['num_stories'],
                    height_of_floors=building['floor_height'],
                    net_leased_area=building['area'],
                    office_layout=1,
                    window_layout=1,
                    with_ahu=False,
                    construction_type="heavy"
                )

                prj.used_library_calc = 'IBPSA'
                prj.number_of_elements_calc = 4
                prj.merge_windows_calc = False
                # prj.weather_file_path = utilities.get_full_path(
                #     os.path.join(
                #         "data",
                #         "input",
                #         "inputdata",
                #         "weatherdata",
                #         "DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos"))
            prj.calc_all_buildings()

            prj.export_ibpsa(
                library="Buildings",
                # internal_id=prj.buildings[-1].internal_id,  # export the last building added only
                path=root_building_dir
            )
        finally:
            os.chdir(curdir)

        # TODO: Determine if we need to move the files to the correct places
        # There are two projects that are exported based on the self.building_id, a Project
        # and a Building. We only care about the buildings for now.

    def to_citygml(self, project, root_directory, filename='citygml.xml'):
        """
        Export a single project Teaser project to citygml. Note that you much pass in a full Teaser project
        to be converted since, at the moment, there is no member variable holding the Teaser project.

        :param project: Teaser Project, project to convert to CityGML.
        :param root_directory: str, root directory where building model will be exported
        :param filename (optional): str, filename to save to
        :return: None
        """
        project.save_citygml(filename, root_directory)
