# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator
from tests.base_test_case import TestCaseBase

ROOT_DIR = Path(__file__).parent


class GeoJSONTranslatorTest(TestCaseBase):
    geojson_file = TestCaseBase.SHARED_DATA_DIR / "geojson_district" / "geojson.json"
    sys_params_file = TestCaseBase.SHARED_DATA_DIR / "geojson_district" / "system_params.json"

    def test_to_modelica_is_successful_when_inputs_are_valid(self):
        # -- Setup, Act
        project_name = "generate_package"
        _, output_dir = self.set_up(ROOT_DIR, project_name)
        gmt = GeoJsonModelicaTranslator(
            self.geojson_file,
            self.sys_params_file,
            output_dir,
            project_name,
        )

        gmt.to_modelica()

        # -- Assert
        assert (output_dir / project_name / "package.mo").exists()

    @pytest.mark.simulation
    @pytest.mark.skip("OMC Spawn - Failed to find spawn executable in Buildings Library")
    def test_successfully_creates_and_simulates_when_inputs_are_valid(self):
        # -- Setup
        project_name = "simulate_package"
        _, output_dir = self.set_up(ROOT_DIR, project_name)

        gmt = GeoJsonModelicaTranslator(
            self.geojson_file,
            self.sys_params_file,
            output_dir,
            project_name,
        )

        package = gmt.to_modelica()

        # -- Act
        success, results_dir = package.simulate()

        # -- Assert
        assert success, "simulation did not complete successfully"
        assert (results_dir / "stdout.log").exists()
