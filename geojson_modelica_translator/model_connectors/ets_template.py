import json
import os

from jinja2 import FileSystemLoader, Environment


class ETS_Template():
    '''This class will template the ETS modelica model.'''

    def __init__(self, thermal_junction_properties_geojson, system_parameters_geojson, ets_from_building_modelica):
        super().__init__()
        '''
        thermal_junction_properties_geojson contains the ETS at brief and at higher level;
        system_parameters_geojson contains the ETS with details                          ;
        ets_from_building_modelica contains the modelica model of ETS                    ;
        '''
        self.thermal_junction_properties_geojson = thermal_junction_properties_geojson
        self.system_parameters_geojson = system_parameters_geojson
        self.ets_from_building_modelica = ets_from_building_modelica

        # get the path of modelica-buildings library
        directory_up_1_levels = os.path.abspath((os.path.join(__file__, "../../")))
        dest_path = "/modelica/buildingslibrary/Buildings/Applications/DHC/EnergyTransferStations/"
        self.directory_modelica_building = os.path.join(directory_up_1_levels + dest_path)

        # go up two levels of directory, to get the path of tests folder for ets
        directory_up_2_levels = os.path.abspath(os.path.join(__file__, "../../.."))
        self.directory_ets_templated = os.path.join(directory_up_2_levels + "/tests/output/ets/")
        if not os.path.exists(self.directory_ets_templated):
            os.mkdir(self.directory_ets_templated)
        else:
            print("test/ets folder is already there!!!\n")
            pass

        # here comes the Jinja2 function: Environment()
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        )

    def check_ets_thermal_junction(self):
        '''check if ETS info are in thermal-junction-geojson file'''
        with open(self.thermal_junction_properties_geojson, 'r') as f:
            data = json.load(f)

        ets_general = False
        for key, value in data.items():
            if key == 'definitions':
                # three levels down to get the ETS signal
                junctions = data["definitions"]["ThermalJunctionType"]["enum"]
                if 'ETS' in junctions:
                    ets_general = True
                    print("ETS is there!!!")
            else:
                pass

        return ets_general

    def check_system_parameters(self):
        '''check detailed parameters of ETS'''
        with open(self.system_parameters_geojson, 'r') as f:
            data = json.load(f)

        ets_details = False
        for key, value in data.items():
            # four levels down to get the details
            ets_details = data["definitions"]["building_def"]["properties"]["ets"]
            print(ets_details)
            if ets_details:
                print("ETS details are here!!!")

        return ets_details

    def check_ets_from_building_modelica(self):
        '''check if ETS-indirectCooling are in modelica building library'''
        ets_modelica_available = os.path.isfile(self.ets_from_building_modelica)

        return ets_modelica_available

    def to_modelica(self):
        '''convert ETS json to modelica'''
        # NL: This code doesn't appear to be used... review
        # ets_modelica = ""
        # if self.check_ets_from_building_modelica():
        #     with open(self.ets_from_building_modelica) as f:
        #         ets_modelica = f.read()
        # else:
        #     pass

        # Here come the Jinja2 function: get_template()
        ets_template = self.template_env.get_template('CoolingIndirect.mot')

        ets_data = {
            "ModelName": "ets_cooling_indirect_templated",
            "Q_Flow_Nominal": [8000],
            "Eta_Efficiency": [0.666],
            "NominalFlow_District": [0.666],
            "NominalFlow_Building": [0.666],
            "PressureDrop_Valve": [888],
            "PressureDrop_HX_Secondary": [999],
            "PressureDrop_HX_Primary": [999],
            "SWT_District": [5],
            "SWT_Building": [7]
        }
        # Here comes the Jina2 function: render()
        file_data = ets_template.render(
            ets_data=ets_data
        )

        # write templated ETS back to modelica file , to the tests folder for Dymola test
        if os.path.exists(os.path.join(self.directory_ets_templated, 'ets_cooling_indirect_templated.mo')):
            os.remove(os.path.join(self.directory_ets_templated, 'ets_cooling_indirect_templated.mo'))
        with open(os.path.join(self.directory_ets_templated, 'ets_cooling_indirect_templated.mo'), 'w') as f:
            f.write(file_data)

        # write templated ETS back to building-modelica folder for Dymola test
        if os.path.exists(os.path.join(self.directory_modelica_building, 'ets_cooling_indirect_templated.mo')):
            os.remove(os.path.join(self.directory_modelica_building, 'ets_cooling_indirect_templated.mo'))
        with open(os.path.join(self.directory_modelica_building, 'ets_cooling_indirect_templated.mo'), 'w') as f:
            f.write(file_data)

        return file_data

    # TODO: do not capitalize Dymola
    def templated_ets_openloops_Dymola(self):
        '''after we creating the templated ets, we need to test it in Dymola under open loops.
        Here we refactor the example file: CoolingIndirectOpenLoops, to test our templated ets model.
        '''
        # if os.path.exists(self.directory_modelica_building + "/Examples/CoolingIndirectOpenLoops.mo"):
        #     print("file exists!")
        # else:
        #     print("CoolingIndirectOpenLoops.mo not exist")

        file = open(self.directory_modelica_building + "/Examples/CoolingIndirectOpenLoops.mo", "r")
        cooling_indirect_filename = "/Examples/CoolingIndirectOpenLoops_Templated.mo"

        # if the modelica example file is existed, delete it first
        if os.path.exists(self.directory_modelica_building + cooling_indirect_filename):
            os.remove(self.directory_modelica_building + cooling_indirect_filename)

        # create the modelica example file for Dymola test
        # TODO: Replace this with the ModelicaFile Class -- extend ModelicaFile class if does not support.
        repl_dict = {}
        from_str = "model CoolingIndirectOpenLoops"
        to_str = "model CoolingIndirectOpenLoops_Templated\n"
        repl_dict[from_str] = to_str
        from_str = "Buildings.Applications.DHC.EnergyTransferStations.CoolingIndirect coo("
        to_str = "Buildings.Applications.DHC.EnergyTransferStations.ets_cooling_indirect_templated coo("
        repl_dict[from_str] = to_str
        from_str = "end CoolingIndirectOpenLoops;"
        to_str = "end CoolingIndirectOpenLoops_Templated;"
        repl_dict[from_str] = to_str

        with open(self.directory_modelica_building + cooling_indirect_filename, "w") as examplefile:
            for f in file:
                fx = f
                for from_str, to_str in enumerate(repl_dict):
                    if f.string() == from_str:
                        fx = f.replace(from_str, to_str)

                examplefile.write(fx)

        return examplefile

    def connect(self):
        '''connect ETS-modelica to building-modelica (specifically TEASER modelica).
        This function will be modified in future'''

        pass
