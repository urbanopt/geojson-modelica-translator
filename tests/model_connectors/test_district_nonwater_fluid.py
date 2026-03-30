# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.external_package_utils import load_loop_order
from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.networks.design_data_series import DesignDataSeries
from geojson_modelica_translator.model_connectors.networks.ground_coupling import GroundCoupling
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class DistrictNonWaterFluidTest(TestCaseBase):
    """Test that non-water fluid types (e.g. PropyleneGlycol) are correctly propagated
    into the generated Modelica district and borefield models."""

    def setUp(self):
        super().setUp()

        project_name = "district_propylene_glycol"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, project_name)

        # load in the example geojson with multiple buildings (reuse existing test data)
        geojson_filename = Path(self.data_dir) / "time_series_ex2.json"
        self.gj = UrbanOptGeoJson(geojson_filename)

        # load system parameter data with PropyleneGlycol fluid
        sys_param_filename = Path(self.data_dir) / "system_params_ghe_propylene_glycol.json"
        sys_params = SystemParameters(sys_param_filename)

        # read the loop order and create building groups
        loop_order = load_loop_order(sys_param_filename)

        # create ambient water loop stub
        ambient_water_stub = NetworkDistributionPump(sys_params)

        # create ground coupling
        ground_coupling = GroundCoupling(sys_params)

        # create district data
        design_data = DesignDataSeries(sys_params)

        # create the couplings and graph
        all_couplings = []
        for loop in loop_order:
            ghe_id = loop["list_ghe_ids_in_group"][0]
            for ghe in sys_params.get_param("$.district_system.fifth_generation.ghe_parameters.borefields"):
                if ghe_id == ghe["ghe_id"]:
                    borefield = Borefield(sys_params, ghe)
            distribution = UnidirectionalSeries(sys_params)
            for bldg_id in loop["list_bldg_ids_in_group"]:
                for geojson_load in self.gj.buildings:
                    if bldg_id == geojson_load.id:
                        time_series_load = TimeSeries(sys_params, geojson_load)
                        all_couplings.append(Coupling(time_series_load, distribution, district_type="fifth_generation"))
                        all_couplings.append(
                            Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation")
                        )
                        all_couplings.append(Coupling(time_series_load, design_data, district_type="fifth_generation"))
            all_couplings.append(Coupling(distribution, borefield, district_type="fifth_generation"))
            all_couplings.append(Coupling(distribution, ground_coupling, district_type="fifth_generation"))
            all_couplings.append(Coupling(ground_coupling, borefield, district_type="fifth_generation"))
        all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="fifth_generation"))

        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            geojson_file=self.gj,
            coupling_graph=graph,
        )

        self.district.to_modelica()

    def test_build_district_system(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    def test_district_has_propylene_glycol_medium(self):
        """Verify the generated DistrictEnergySystem.mo uses PropyleneGlycolWater as the medium."""
        district_mo_file = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        mo_content = district_mo_file.read_text()

        # The district template should declare MediumW as PropyleneGlycolWater
        assert "PropyleneGlycolWater" in mo_content, (
            "DistrictEnergySystem.mo should contain PropyleneGlycolWater medium declaration"
        )
        # Should NOT default to plain Water
        assert "package MediumW=Buildings.Media.Water" not in mo_content, (
            "DistrictEnergySystem.mo should not use plain Water when PropyleneGlycol is specified"
        )
        # Verify concentration and temperature are set (0.2 concentration, 20°C -> 293.15 K)
        assert "X_a=0.2" in mo_content, "PropyleneGlycol concentration should be 0.2"
        assert "property_T=293.15" in mo_content, "PropyleneGlycol temperature should be 293.15 K"

    def test_borefield_instance_redeclares_medium(self):
        """Verify the borefield instance in the district model redeclares Medium to MediumW."""
        district_mo_file = Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        mo_content = district_mo_file.read_text()

        # The Borefield_Instance.mopt template should produce a redeclare of Medium = MediumW
        assert "redeclare final package Medium = MediumW" in mo_content, (
            "Borefield instance should redeclare Medium to use the district-level MediumW package"
        )
