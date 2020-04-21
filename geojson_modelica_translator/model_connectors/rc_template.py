import os

from jinja2 import Environment, FileSystemLoader


class RCTemplate:
    """This class will template the RC modelica model, with AirTerminal/WaterDistribution included."""
    def __init__(self, rc_folder):
        self.rc_folder = rc_folder

        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
        )

    def assemble_rc_water_distribution_and_air_terminal(self, rc_type):
        rc_template = self.template_env.get_template("RC_building.mot")
        rc_path = {}
        rc_path["office"] = [self.rc_folder]
        rc_path["floor"] = [self.rc_folder]
        rc_path["storage"] = [self.rc_folder]
        rc_path["meeting"] = [self.rc_folder]
        rc_path["restroom"] = [self.rc_folder]
        rc_path["iCT"] = [self.rc_folder]

        file_data = rc_template.render(rc_folder=rc_path,
                                       rc_folder_name=self.rc_folder)

        # write templated RC back to where building modelica files are: office/meeting/iCT, etc.
        if rc_type == "modelica_default":
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/example_geojson_13buildings/Loads")
        elif rc_type == "modelica_rc4":
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/geojson_13buildings/rc_order_4/Loads")
        else:
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/example_geojson_13buildings/Loads")

        path_rc_templated = os.path.abspath(tmp_path + "/" + self.rc_folder + "/BuildingRCZ6_Templated.mo")

        if os.path.exists(path_rc_templated):
            os.remove(path_rc_templated)

        with open(path_rc_templated, "w") as f:
            f.write(file_data)

        # add generated modelica to the package order to be recognized by Dymola
        os.remove(os.path.abspath(tmp_path + "/" + self.rc_folder + "/package.order"))
        modelica_model_list = []
        for file in os.listdir(os.path.abspath(tmp_path + "/" + self.rc_folder)):
            if file.endswith(".mo") and file.strip() != "package.mo":
                modelica_model_list.append(file.replace(".mo", " "))

        with open(os.path.abspath(tmp_path + "/" + self.rc_folder + "/package.order"), "w") as f:
            for each_modelica in modelica_model_list:
                f.write(each_modelica+"\n")
