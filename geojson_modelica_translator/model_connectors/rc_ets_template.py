import os

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath
from jinja2 import Environment, FileSystemLoader

# import shutil


class RCETSConnector(model_connector_base):
    """This class will template the RC-ETS modelica model."""
    def __init__(self, system_parameters):
        super().__init__(system_parameters)

        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.template_env = Environment(loader=FileSystemLoader(searchpath=self.template_dir))

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.
        :param urbanopt_building: an urbanopt_building
        """

        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            number_stories = urbanopt_building.feature.properties["number_of_stories"]
            number_stories_above_ground = urbanopt_building.feature.properties["number_of_stories_above_ground"]
            self.buildings.append(
                {
                    "area": urbanopt_building.feature.properties["floor_area"] * 0.092936,  # ft2 -> m2
                    "building_id": urbanopt_building.feature.properties["id"],
                    "building_type": urbanopt_building.feature.properties["building_type"],
                    "floor_height": urbanopt_building.feature.properties["height"] * 0.3048,  # ft -> m
                    "num_stories": urbanopt_building.feature.properties["number_of_stories_above_ground"],
                    "num_stories_below_grade": number_stories - number_stories_above_ground,
                    "year_built": urbanopt_building.feature.properties["year_built"],
                }
            )

    def to_modelica(self, scaffold):
        """
        Create TimeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        curdir = os.getcwd()
        rc_building_template = self.template_env.get_template("BuildingRCZ6.mot")
        ets_template = self.template_env.get_template("CoolingIndirect.mot")
        rc_ets_coupling_template = self.template_env.get_template("CouplingRCZ6_ETS.mot")

        building_names = []
        try:
            for building in self.buildings:
                # create timeSeries building and save to the correct directory
                print(f"Creating RCZ6 for building: {building['building_id']}")

                # Path for building data
                building_names.append(f"B{building['building_id']}")
                b_modelica_path = ModelicaPath(
                    f"B{building['building_id']}", scaffold.loads_path.files_dir, True
                )
                # print("\n $$$$$$ Yanfei building-id: ", building['building_id'], "$$$$$$\n")

                # generate files with name:
                # BuildingRCZ6.mo, CoolingIndirect.mo and CouplingETS_RCBuilding.mo
                # They are created sequentially
                # ----> 1.0 BuildingRCZ6
                file_data = rc_building_template.render(
                    project_name=scaffold.project_name,
                    model_name=f"B{building['building_id']}"
                )
                with open(os.path.join(os.path.join(b_modelica_path.files_dir, "BuildingRCZ6.mo")), "w") as f:
                    f.write(file_data)

                # 2.0 ----> ETS,
                # read parameters of ETS from parameters.json file
                ets_model_type = self.system_parameters.get_param_by_building_id(
                    building["building_id"], "ets_model"
                )
                ets_data = None
                if ets_model_type == "Indirect Cooling":
                    ets_data = self.system_parameters.get_param_by_building_id(
                        building["building_id"],
                        "ets_model_parameters.indirect_cooling"
                    )
                else:
                    raise Exception("Only ETS Model of type 'Indirect Cooling' type enabled currently")

                file_data = ets_template.render(
                    project_name=scaffold.project_name,
                    model_name=f"B{building['building_id']}",
                    ets_data=ets_data,
                )

                with open(os.path.join(os.path.join(b_modelica_path.files_dir, "CoolingIndirect.mo")), "w") as f:
                    f.write(file_data)

                # 3.0 ----> CouplingETS_RCBuilding
                file_data = rc_ets_coupling_template.render(
                    project_name=scaffold.project_name,
                    model_name=f"B{building['building_id']}",
                    rc_name="BuildingRCZ6",
                    ets_name="CoolingIndirect",
                )
                with open(os.path.join(os.path.join(b_modelica_path.files_dir, "CouplingRCZ6_ETS.mo")),
                          "w") as f:
                    f.write(file_data)

        finally:
            os.chdir(curdir)

        # run post process to create the remaining project files for this building
        self.post_process(scaffold, building_names)

    def post_process(self, scaffold, building_names):
        """
        Cleanup the export of TimeSeries files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :return: None
        """
        for b in building_names:
            b_modelica_path = os.path.join(scaffold.loads_path.files_dir, b)
            new_package = PackageParser.new_from_template(
                b_modelica_path, b,
                ["BuildingRCZ6", "CoolingIndirect", "CouplingRCZ6_ETS"],
                within=f"{scaffold.project_name}.Loads"
            )
            new_package.save()

        # now create the Loads level package. This (for now) will create the package without considering any existing
        # files in the Loads directory.
        package = PackageParser.new_from_template(
            scaffold.loads_path.files_dir, "Loads", building_names, within=f"{scaffold.project_name}"
        )
        package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Loads"]
        )
        pp.save()
