import json
import os

from jinja2 import Environment, FileSystemLoader

# TODO: Class name should be upper camel case, not a mix of camel and snake case.


class ETSTemplate:
    """This class will template the ETS modelica model."""

    def __init__(
        self,
        thermal_junction_properties_geojson,
        system_parameters_geojson,
        ets_from_building_modelica,
    ):
        super().__init__()
        """
        thermal_junction_properties_geojson contains the ETS at brief and at higher level;
        system_parameters_geojson contains the ETS with details                          ;
        ets_from_building_modelica contains the modelica model of ETS                    ;
        """
        self.thermal_junction_properties_geojson = thermal_junction_properties_geojson
        self.thermal_junction_properties_geojson = self.thermal_junction_properties_geojson.replace(
            "\\", "/"
        )

        self.system_parameters_geojson = system_parameters_geojson
        if "\\" in self.system_parameters_geojson:
            self.system_parameters_geojson = self.system_parameters_geojson.replace(
                "\\", "/"
            )

        self.ets_from_building_modelica = ets_from_building_modelica
        if "\\" in self.ets_from_building_modelica:
            self.ets_from_building_modelica = self.ets_from_building_modelica.replace(
                "\\", "/"
            )

        # get the path of modelica-buildings library
        directory_up_one_levels = os.path.abspath((os.path.join(__file__, "../../")))
        dest_path = "/modelica/buildingslibrary/Buildings/Applications/DHC/EnergyTransferStations/"
        self.directory_modelica_building = os.path.join(
            directory_up_one_levels + dest_path
        )
        if "\\" in self.directory_modelica_building:
            self.directory_modelica_building = self.directory_modelica_building.replace(
                "\\", "/"
            )

        # go up two levels of directory, to get the path of tests folder for ets
        directory_up_two_levels = os.path.abspath(os.path.join(__file__, "../../.."))
        self.directory_ets_templated = os.path.join(
            directory_up_two_levels + "/tests/output_ets"
        )
        if "\\" in self.directory_ets_templated:
            self.directory_ets_templated = self.directory_ets_templated.replace(
                "\\", "/"
            )

        if not os.path.isdir(self.directory_ets_templated):
            os.mkdir(self.directory_ets_templated)
        else:
            pass

        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "templates"
                )
            )
        )

    def check_ets_thermal_junction(self):
        """check if ETS info are in thermal-junction-geojson file"""
        with open(self.thermal_junction_properties_geojson, "r") as f:
            data = json.load(f)

        ets_general = False
        for key, value in data.items():
            if key == "definitions":
                # three levels down to get the ETS signal
                junctions = data["definitions"]["ThermalJunctionType"]["enum"]
                if "ETS" in junctions:
                    ets_general = True
            else:
                pass

        return ets_general

    def check_ets_system_parameters(self):
        """check detailed parameters of ETS"""
        with open(self.system_parameters_geojson, "r") as f:
            data = json.load(f)

        ets_parameters = False
        # four levels down to get the ets model description
        # ets_overall = data["definitions"]["building_def"]["properties"]["ets"]
        # three levels down to get the parameters
        ets_parameters = data["definitions"]["ets_parameters"]["properties"]
        # print ("est_parameters are: ", type(ets_parameters) )
        return ets_parameters

    def check_ets_from_building_modelica(self):
        """check if ETS-indirectCooling are in modelica building library"""
        ets_modelica_available = os.path.isfile(self.ets_from_building_modelica)

        return ets_modelica_available

    def to_modelica(self):
        """convert ETS json to modelica"""
        # Here come the Jinja2 function: get_template(), which reads into templated ets model.
        # CoolingIndirect.mot was manually created as a starting point, by adding stuff following Jinja2 syntax.
        # it has all the necessary parameters which need to be changed through templating.
        ets_template = self.template_env.get_template("CoolingIndirect.mot")

        # TODO: Seems like the ets_data below should allow defaults from
        #  the system parameters JSON file, correct?
        # ets model parameters are from the schema.json file, default values only.
        ets_data = self.check_ets_system_parameters()

        # Here comes the Jina2 function: render()
        file_data = ets_template.render(ets_data=ets_data)

        # write templated ETS back to modelica file , to the tests folder for Dymola test
        if os.path.exists(
            os.path.join(
                self.directory_ets_templated, "ets_cooling_indirect_templated.mo"
            )
        ):
            os.remove(
                os.path.join(
                    self.directory_ets_templated, "ets_cooling_indirect_templated.mo"
                )
            )
        with open(
            os.path.join(
                self.directory_ets_templated, "ets_cooling_indirect_templated.mo"
            ),
            "w",
        ) as f:
            f.write(file_data)

        # write templated ETS back to building-modelica folder for Dymola test
        if os.path.exists(
            os.path.join(
                self.directory_modelica_building, "ets_cooling_indirect_templated.mo"
            )
        ):
            os.remove(
                os.path.join(
                    self.directory_modelica_building,
                    "ets_cooling_indirect_templated.mo",
                )
            )
        with open(
            os.path.join(
                self.directory_modelica_building, "ets_cooling_indirect_templated.mo"
            ),
            "w",
        ) as f:
            f.write(file_data)

        return file_data

    def templated_ets_openloops_dymola(self):
        """after we creating the templated ets, we need to test it in Dymola under open loops.
        Here we refactor the example file: CoolingIndirectOpenLoops,
        to test our templated ets model.
        """
        file = open(
            self.directory_modelica_building + "/Examples/CoolingIndirectOpenLoops.mo",
            "r",
        )
        cooling_indirect_filename = "/Examples/CoolingIndirectOpenLoops_Templated.mo"

        # if the modelica example file is existed, delete it first
        if os.path.exists(self.directory_modelica_building + cooling_indirect_filename):
            os.remove(self.directory_modelica_building + cooling_indirect_filename)

        # create the modelica example file for Dymola test
        # TODO: Replace this with the ModelicaFile Class --
        #  extend ModelicaFile class if does not support.
        # Theoretically it is doable using extend clause from Modelica.
        # But we need to change the original ETS model first, in order to extend.
        # This is Michael Wetter suggested approach.
        # if so, we don't need to template modelica models, but we need to connect the modelica components
        repl_dict = {}
        from_str = "model CoolingIndirectOpenLoops"
        to_str = "model CoolingIndirectOpenLoops_Templated\n"
        repl_dict[from_str] = to_str
        from_str = (
            "Buildings.Applications.DHC.EnergyTransferStations.CoolingIndirect coo("
        )
        to_str = "Buildings.Applications.DHC.EnergyTransferStations.ets_cooling_indirect_templated coo("
        repl_dict[from_str] = to_str
        from_str = "end CoolingIndirectOpenLoops;"
        to_str = "end CoolingIndirectOpenLoops_Templated;"
        repl_dict[from_str] = to_str

        with open(
            self.directory_modelica_building + cooling_indirect_filename, "w"
        ) as examplefile:
            for f in file:
                fx = f
                for from_str, to_str in repl_dict.items():
                    # TODO: f.string() causes errors, check code
                    if fx.strip() == from_str.strip():
                        fx = f.replace(from_str, to_str)

                examplefile.write(fx)

        return examplefile

    def connect(self):
        """connect ETS-modelica to building-modelica (specifically TEASER modelica).
        This function will be modified in future"""
