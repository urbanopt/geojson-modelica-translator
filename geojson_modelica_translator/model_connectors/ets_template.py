"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import json
import os

from jinja2 import Environment, FileSystemLoader


class ETSTemplate:
    """This class will template the ETS modelica model."""

    def __init__(self, thermal_junction_properties_geojson, system_parameters_geojson):
        """
        thermal_junction_properties_geojson contains the ETS at brief and at higher level;
        system_parameters_geojson contains the ETS with details                          ;
        ets_from_building_modelica contains the modelica model of ETS                    ;
        """
        super().__init__()

        self.thermal_junction_properties_geojson = thermal_junction_properties_geojson

        self.system_parameters_geojson = system_parameters_geojson

        # go up two levels of directory, to get the path of tests folder for ets
        # TODO: we shouldn't be writing to the test directory in this file, only in tests.
        directory_up_two_levels = os.path.abspath(os.path.join(__file__, "../../.."))
        self.directory_ets_templated = os.path.join(
            directory_up_two_levels + "/tests/output/ets"
        )

        if not os.path.isdir(self.directory_ets_templated):
            os.mkdir(self.directory_ets_templated)
        else:
            pass

        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
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
        ets_parameters = data["ets"]["default"]
        # print ("est_parameters are: ", type(ets_parameters) )
        return ets_parameters

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
        project_name = "Building"
        model_name = "ets_cooling_indirect_templated"
        # Here comes the Jina2 function: render()
        file_data = ets_template.render(project_name=project_name, model_name=model_name, ets_data=ets_data)

        # write templated ETS back to modelica file , to the tests folder for Dymola test
        path_ets_templated = os.path.join(self.directory_ets_templated, "ets_cooling_indirect_templated.mo")

        if os.path.exists(path_ets_templated):
            os.remove(path_ets_templated)
        with open(path_ets_templated, "w") as f:
            f.write(file_data)

        # write templated ETS back to building-modelica folder for Dymola test
        path_writtenback = os.path.join(os.path.abspath(os.path.join(__file__, "../..")) + "/modelica/")

        if os.path.exists(os.path.join(path_writtenback, "ets_cooling_indirect_templated.mo")):
            os.remove(os.path.join(path_writtenback, "ets_cooling_indirect_templated.mo"))
        with open(os.path.join(path_writtenback, "ets_cooling_indirect_templated.mo"), "w") as f:
            f.write(file_data)

        return file_data
