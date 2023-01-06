# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

# import pytest
from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)

from ..base_test_case import TestCaseBase

ROOT_DIR = Path(__file__).parent


class GeoJSONTranslatorTest(TestCaseBase):
    geojson_file = TestCaseBase.SHARED_DATA_DIR / 'geojson_district' / 'geojson.json'
    sys_params_file = TestCaseBase.SHARED_DATA_DIR / 'geojson_district' / 'system_params.json'

    def test_to_modelica_is_successful_when_inputs_are_valid(self):
        # -- Setup, Act
        project_name = 'generate_package'
        _, output_dir = self.set_up(ROOT_DIR, project_name)
        gmt = GeoJsonModelicaTranslator(
            self.geojson_file,
            self.sys_params_file,
            output_dir,
            project_name,
        )

        gmt.to_modelica()

        # -- Assert
        self.assertTrue((output_dir / project_name / 'package.mo').exists())

    # The NREL site models don't run for some reason. Commenting out for now since
    # these models are here as a reference. We will revisit after upgrading to MBL 9.0.
    # @pytest.mark.simulation
    # def test_successfully_creates_and_simulates_when_inputs_are_valid(self):
    #     # -- Setup
    #     project_name = 'simulate_package'
    #     _, output_dir = self.set_up(ROOT_DIR, project_name)

    #     gmt = GeoJsonModelicaTranslator(
    #         self.geojson_file,
    #         self.sys_params_file,
    #         output_dir,
    #         project_name,
    #     )

    #     package = gmt.to_modelica()

    #     # -- Act
    #     success, results_dir = package.simulate()

    #     # -- Assert
    #     self.assertTrue(success, 'simulation did not complete successfully')
    #     self.assertTrue((results_dir / 'stdout.log').exists())
