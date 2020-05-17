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
import shutil
import unittest

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.ets_template import (
    ETSConnector
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class ETSModelConnectorSingleBuildingTest(unittest.TestCase):

    def setUp(self):  # the first method/member must be setUp
        self.data_dir = os.path.join(os.path.dirname(__file__), "data/")
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output/')

        project_name = "ets_test"
        if os.path.exists(os.path.join(self.output_dir, project_name)):
            shutil.rmtree(os.path.join(self.output_dir, project_name))

        # load in the example geojson with a single offie building
        filename = os.path.join(self.data_dir, "spawn_geojson_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        self.gj.scaffold_directory(self.output_dir, project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "spawn_system_params_ex1.json")
        sys_params = SystemParameters(filename)
        # get building id from geojson instance, and add to dict
        building_id = sys_params.get_param("buildings.custom")[0]["geojson_id"]
        self.building = {}
        self.building["building_id"] = building_id
        # now test the ETSConnector,
        # independent of the generic geojson translator
        self.ets = ETSConnector(sys_params)

    def test_ets_init(self):
        self.assertIsNotNone(self.ets)
        print("\n Yanfei: ", self.ets.system_parameters.get_param("buildings.custom")[0]["load_model"])
        self.assertEqual(self.ets.system_parameters.get_param("buildings.custom")[0]["load_model"], "Spawn")

    def test_to_modelica(self):
        ets_templated = self.ets.to_modelica(self.gj.scaffold, self.building)
        self.assertIsNotNone(ets_templated)
