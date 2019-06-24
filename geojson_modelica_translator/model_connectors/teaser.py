
import os
from teaser.project import Project

from geojson_modelica_translator.model_connectors.base import Base as model_connector_base


class TeaserConnector(model_connector_base):
    def __init__(self, urbanopt_building):
        super().__init__(urbanopt_building)

    def mappings(self):
        """
        :return:
        """
        pass

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
            prj.name = self.building_id
            prj.add_non_residential(
                method='bmvbs',
                usage=self.lookup_building_type(self.building_type),
                name=self.building_id,
                year_of_construction=self.year_built,
                number_of_floors=self.num_stories,
                height_of_floors=self.floor_height,
                net_leased_area=self.area,
                office_layout=1,
                window_layout=1,
                with_ahu=False,
                construction_type="heavy"
            )

            prj.used_library_calc = 'IBPSA'
            prj.number_of_elements_calc = 2
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
                library="BuildingSystems",
                internal_id=prj.buildings[-1].internal_id,  # export the last building added only
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
        project.save_citygml(filename, root_building_dir)
