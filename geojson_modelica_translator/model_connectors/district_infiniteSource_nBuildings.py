# import json
import os

from jinja2 import Environment, FileSystemLoader


class DistrictInfiniteSourceNBuildingsTemplate:
    """This class will generate a district model with infinite source for
    arbitrary number of buildings connected with ETS"""
    def __init__(self, nBuilding):
        super().__init__()

        self.nBuilding = nBuilding
        directory_up_one_level = os.path.abspath(os.path.join(__file__, "../../"))
        self.directory_district_nBuildings = os.path.join(
            directory_up_one_level + "/tests/output/district_nBuildings/"
        )

        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            )
        )

    def to_modelica(self):
        """ generate district model with arbitrary number of buildings connected to ETS"""

        district_template = self.template_env.get_template("District_InfiniteSource_nBuildings.mot")

        # setup the data to be applied in template
        district_data = {}
        district_data['rc_buildings_count'] = self.nBuilding

        # Here comes the Jina2 function: render()
        templated_model = district_template.render(distric_data=district_data)

        # write templated ETS back to modelica file , to the tests folder for Dymola test
        path_templated = os.path.join(self.directory_district_nBuildings,
                                      "district_infinite_source_nRCBuildings_templated.mo")

        if os.path.exists(path_templated):
            os.remove(path_templated)
        with open(path_templated, "w") as f:
            f.write(templated_model)

        return templated_model
