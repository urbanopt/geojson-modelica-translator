import os
import unittest

from geojson_modelica_translator.model_connectors.ets_template import ETS_Template
from ..context import geojson_modelica_translator  # noqa - Do not remove this line


# TODO: do not mix upper camel case and snake case. Spell out ETS or use ETSModelConnector...
class ETS_ModelConnectorSingleBuildingTest(unittest.TestCase):
    def setUp(self):  # the first method/member must be setUp
        base_folder = os.path.join(os.getcwd(), 'geojson_modelica_translator')
        dest_path = "geojson/data/schemas/thermal_junction_properties.json"
        self.thermal_junction_properties_geojson = base_folder + dest_path
        dest_path = "system_parameters/schema.json"
        self.system_parameters_geojson = base_folder + dest_path
        dest_path = "modelica/buildingslibrary/Buildings/Applications/DHC/EnergyTransferStations/CoolingIndirect.mo"
        self.ets_from_building_modelica = base_folder + dest_path

        self.ets = ETS_Template(
            self.thermal_junction_properties_geojson,
            self.system_parameters_geojson,
            self.ets_from_building_modelica
        )
        self.assertIsNotNone(self.ets)

        return self.ets

    def test_ets_thermal_junction(self):
        ets_general = self.ets.check_ets_thermal_junction()
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
