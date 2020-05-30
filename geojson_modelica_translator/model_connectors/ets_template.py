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

import os

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.utils import ModelicaPath
from jinja2 import Environment, FileSystemLoader


class ETSConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        """This class will template the ETS modelica model. It will be used for sizing ETS models."""
        # here comes the Jinja2 function: Environment()
        # it loads all the "*.mot" files into an environment by Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            )
        )

    def to_modelica(self, scaffold, building):
        # Here come the Jinja2 function: get_template(), which reads into templated ets model.
        # CoolingIndirect.mot was manually created as a starting point, by adding stuff following Jinja2 syntax.
        # it has all the necessary parameters which need to be changed through templating.

        # building is a dict, containing the building geojson properties,
        # "buidling_id" is needed here within "building" dict.

        ets_template = self.template_env.get_template("CoolingIndirect.mot")
        b_modelica_path = ModelicaPath(
            f"B{building['building_id']}", scaffold.loads_path.files_dir, True
        )
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

        file_data_ets = ets_template.render(
            project_name=scaffold.project_name,
            model_name=f"B{building['building_id']}",
            ets_data=ets_data,
        )
        with open(os.path.join(os.path.join(b_modelica_path.files_dir, "CoolingIndirect.mo")), "w") as f:
            f.write(file_data_ets)

        return file_data_ets
