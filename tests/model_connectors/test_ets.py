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
import unittest

from geojson_modelica_translator.model_connectors.ets_template import (
    ETSTemplate
)


class ETSModelConnectorSingleBuildingTest(unittest.TestCase):
    def setUp(self):  # the first method/member must be setUp
        base_folder = os.path.join(os.getcwd(), "geojson_modelica_translator")
        dest_path = "/geojson/data/schemas/thermal_junction_properties.json"
        self.thermal_junction_properties_geojson = base_folder + dest_path
        dest_path = "/system_parameters/schema.json"
        self.system_parameters_geojson = base_folder + dest_path
        dest_path = "/modelica/CoolingIndirect.mo"
        self.ets_from_building_modelica = base_folder + dest_path

        self.ets = ETSTemplate(
            self.thermal_junction_properties_geojson,
            self.system_parameters_geojson,
            self.ets_from_building_modelica,
        )
        self.assertIsNotNone(self.ets)

        return self.ets

    def test_ets_thermal_junction(self):
        ets_general = self.ets.check_ets_thermal_junction()
        self.assertTrue(ets_general)

    def test_ets_system_parameters(self):
        self.assertIsNotNone(self.ets.check_ets_system_parameters())

    def test_ets_from_building_modelica(self):
        self.assertTrue(self.ets.check_ets_from_building_modelica())

    def test_ets_to_modelica(self):
        self.assertIsNotNone(self.ets.to_modelica())

    def test_ets_in_dymola(self):
        self.assertIsNotNone(self.ets.templated_ets_openloops_dymola())


if __name__ == "__main__":
    unittest.main()
