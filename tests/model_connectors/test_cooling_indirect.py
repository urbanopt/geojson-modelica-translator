# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.energy_transfer_systems.cooling_indirect import CoolingIndirect
from geojson_modelica_translator.scaffold import Scaffold
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class CoolingIndirectTest(TestCaseBase):
    def test_cooling_indirect(self):
        project_name = "cooling_indirect"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with a single office building
        filename = Path(self.data_dir) / "time_series_ex1.json"
        self.gj = UrbanOptGeoJson(filename)
        # scaffold the project ourselves
        scaffold = Scaffold(self.output_dir, project_name)
        scaffold.create()

        # load system parameter data
        filename = Path(self.data_dir) / "time_series_system_params_ets.json"
        sys_params = SystemParameters(filename)

        # now test the connector (independent of the larger geojson translator)
        geojson_id = self.gj.buildings[0].feature.properties["id"]
        self.cooling_indirect = CoolingIndirect(sys_params, geojson_id)
        self.cooling_indirect.to_modelica(scaffold)

        root_path = Path(scaffold.substations_path.files_dir).resolve()
        model_filepath = root_path / f"CoolingIndirect_{geojson_id}.mo"
        assert Path(model_filepath).exists(), f"File does not exist: {model_filepath}"
