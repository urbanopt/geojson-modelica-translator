from ..context import geojson_modelica_translator  # noqa - Do not remove this line

import unittest
from geojson_modelica_translator.model_connectors.ets_template import ETS_Template
import os


class ETS_ModelConnectorSingleBuildingTest(unittest.TestCase):
    def setUp(self):  # the first method/member must be setUp
        folder_base = os.getcwd()
        self.thermal_junction_properties_geojson = folder_base + "/geojson_modelica_translator/geojson/data/schemas/thermal_junction_properties.json"
        self.system_parameters_geojson = folder_base + "/geojson_modelica_translator/system_parameters/schema.json"
        self.ets_from_building_modelica = folder_base + "/geojson_modelica_translator/modelica/buildingslibrary/Buildings/Applications/DHC/EnergyTransferStations/CoolingIndirect.mo"

        self.ets = ETS_Template(self.thermal_junction_properties_geojson, self.system_parameters_geojson, self.ets_from_building_modelica)
        self.assertIsNotNone(self.ets)

        return self.ets

    def test_ets_thermal_junction(self):
        ets_general = self.ets.check_ets_thermal_junction()
        #print ("yanfei: ", ets_general)
        self.assertTrue(ets_general)

    def test_ets_system_parameters(self):
        self.assertTrue(self.ets.check_system_parameters())

    def test_ets_from_building_modelica(self):
        self.assertTrue(self.ets.check_ets_from_building_modelica())

    def test_ets_to_modelica(self):
        self.assertIsNotNone(self.ets.to_modelica())

    def test_ets_in_Dymola(self):
        self.assertIsNotNone(self.ets.templated_ets_openloops_Dymola())


if __name__ == '__main__':
    unittest.main()
