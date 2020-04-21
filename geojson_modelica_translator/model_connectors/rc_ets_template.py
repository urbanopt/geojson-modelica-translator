import os

from jinja2 import Environment, FileSystemLoader


class RCETSTemplate:
    """This class will template the RC-ETS modelica model."""
    def __init__(self, rc_folder):
        self.rc_folder = rc_folder
        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
        )

    def connect_rc_ets(self, rc_type):
        """project_name, load_name, rc_name, ets_name"""
        rc_ets_template = self.template_env.get_template("CouplingRCZ6_ETS.mot")
        project_name = "example_geojson_13buildings"
        load_name = self.rc_folder
        rc_name = "BuildingRCZ6_Templated"
        ets_name = "CoolingIndirect"
        rc_ets_model_name = "CouplingRCZ6_ETS_Templated"
        file_data = rc_ets_template.render(project_name=project_name,
                                           load_name=load_name,
                                           rc_name=rc_name,
                                           ets_name=ets_name,
                                           rc_ets_model_name=rc_ets_model_name)
        if rc_type == "modelica_default":
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/example_geojson_13buildings/Loads")
        elif rc_type == "modelica_rc4":
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/geojson_13buildings/rc_order_4/Loads")
        else:
            tmp_path = os.path.abspath(
                os.path.join(__file__, "../../../") + "/tests/output/example_geojson_13buildings/Loads")

        path_rcets_templated = os.path.abspath(tmp_path + "/" + self.rc_folder + "/CouplingRCZ6_ETS_Templated.mo")

        if os.path.exists(path_rcets_templated):
            os.remove(path_rcets_templated)

        with open(path_rcets_templated, "w") as f:
            f.write(file_data)

        # add generated modelica to the package order to be recgonized by Dymola
        os.remove(os.path.abspath(tmp_path + "/" + self.rc_folder + "/package.order"))
        modelica_model_list = []
        for file in os.listdir(os.path.abspath(tmp_path+"/"+self.rc_folder)):
            if file.endswith(".mo") and file.strip() != "package.mo":
                modelica_model_list.append(file.replace(".mo", " "))

        with open(os.path.abspath(tmp_path + "/" + self.rc_folder + "/package.order"), "w") as f:
            for each_modelica in modelica_model_list:
                f.write(each_modelica+"\n")
