# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator, _parse_couplings
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants.no_plant_boundary import NoPlantBoundary
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase

ROOT_DIR = Path(__file__).parent


class GeoJSONTranslatorTest(TestCaseBase):
    geojson_file = TestCaseBase.SHARED_DATA_DIR / "geojson_district" / "geojson.json"
    sys_params_file = TestCaseBase.SHARED_DATA_DIR / "geojson_district" / "system_params.json"
    no_plant_geojson_file = Path(__file__).parents[1] / "model_connectors" / "data" / "time_series_ex1.json"
    no_plant_sys_params_file = (
        Path(__file__).parents[1] / "model_connectors" / "data" / "time_series_5g_no_plant_sys_params.json"
    )

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

    def test_parse_couplings_adds_no_plant_boundary_for_no_source_fifth_generation_loop(self):
        geojson = UrbanOptGeoJson(self.no_plant_geojson_file)
        sys_params = SystemParameters(self.no_plant_sys_params_file)

        couplings = _parse_couplings(geojson, sys_params, "fifth_generation")

        no_plant_couplings = [
            coupling
            for coupling in couplings
            if isinstance(coupling.model_a, UnidirectionalSeries) and isinstance(coupling.model_b, NoPlantBoundary)
        ]
        assert len(no_plant_couplings) == 1
        no_plant_coupling = no_plant_couplings[0]
        assert no_plant_coupling.district_type == "fifth_generation"
        assert "UnidirectionalSeries_NoPlantBoundary" in no_plant_coupling.component_definitions_template_path

    def test_to_modelica_is_successful_for_no_plant_fifth_generation_inputs(self):
        project_name = "generate_no_plant_5g_package"
        _, output_dir = self.set_up(ROOT_DIR, project_name)
        gmt = GeoJsonModelicaTranslator(
            self.no_plant_geojson_file,
            self.no_plant_sys_params_file,
            output_dir,
            project_name,
        )

        gmt.to_modelica()

        assert (output_dir / project_name / "package.mo").exists()
        district_model = output_dir / project_name / "Districts" / "DistrictEnergySystem.mo"
        district_text = district_model.read_text()
        assert "/5G_templates/UnidirectionalSeries_NoPlantBoundary/ComponentDefinitions.mopt" in district_text
        assert "bound_heatPort_" in district_text
        assert "TSouIn_fallback_" in district_text
        assert "TSouOut_fallback_" in district_text

    def test_to_modelica_respects_gmt_max_buildings_for_no_plant_fifth_generation(self):
        project_name = "generate_no_plant_5g_package_limited"
        _, output_dir = self.set_up(ROOT_DIR, project_name)
        prev_max_buildings = os.environ.get("GMT_MAX_BUILDINGS")
        os.environ["GMT_MAX_BUILDINGS"] = "1"
        try:
            gmt = GeoJsonModelicaTranslator(
                self.no_plant_geojson_file,
                self.no_plant_sys_params_file,
                output_dir,
                project_name,
            )

            gmt.to_modelica()
        finally:
            if prev_max_buildings is None:
                os.environ.pop("GMT_MAX_BUILDINGS", None)
            else:
                os.environ["GMT_MAX_BUILDINGS"] = prev_max_buildings

        district_model = output_dir / project_name / "Districts" / "DistrictEnergySystem.mo"
        assert district_model.exists()
        assert district_model.read_text().count("Begin Model Instance for TimeSerLoa_B") == 1

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
