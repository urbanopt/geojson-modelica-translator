# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
#
# Tests for the optional steam losses in 1st-generation (steam) districts:
# steam leaks, supply-main heat loss, condensate discharge (no / partial condensate return)
# and make-up water (Networks.SteamLossAndMakeup, instance "losMak").

import json
import re
from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import Network2Pipe
from geojson_modelica_translator.model_connectors.plants.steam_boiler import SteamPlant
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


def _build_steam_district(test_case, project_name, sys_params_file):
    data_dir, output_dir = test_case.set_up(Path(__file__).parent, project_name)
    gj = UrbanOptGeoJson(Path(data_dir) / "time_series_ex2.json")
    sys_params = SystemParameters(Path(data_dir) / sys_params_file)
    graph = CouplingGraph([Coupling(Network2Pipe(sys_params), SteamPlant(sys_params))])
    district = District(
        root_dir=output_dir,
        project_name=project_name,
        system_parameters=sys_params,
        coupling_graph=graph,
        geojson_file=gj,
    )
    district.to_modelica()
    return district


class SteamNoLossesTest(TestCaseBase):
    """Without loss parameters the generated model must be unchanged (no losMak)."""

    def setUp(self):
        super().setUp()
        self.district = _build_steam_district(self, "steam_no_losses", "time_series_sys_params_steam_3buildings.json")

    def test_no_loss_component(self):
        district_mo = (Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo").read_text()
        assert "Networks.SteamLossAndMakeup losMak(" not in district_mo
        assert "losMak.port" not in district_mo
        assert "connect(pla.port_bSerHea, dis.port_aDisSup);" in district_mo
        assert "connect(dis.port_bDisRet, pla.port_aSerHea);" in district_mo
        assert not (Path(self.district._scaffold.networks_path.files_dir) / "SteamLossAndMakeup.mo").exists()


class SteamLossesTest(TestCaseBase):
    """Leak, heat loss and partial condensate return."""

    def setUp(self):
        super().setUp()
        self.district = _build_steam_district(self, "steam_losses", "time_series_sys_params_steam_losses.json")
        self.district_mo = (
            Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"
        ).read_text()

    def test_loss_component_is_instantiated_with_parameters(self):
        mo = "".join(self.district_mo.split())
        assert "Networks.SteamLossAndMakeuplosMak(" in mo
        assert "finalmLea_flow_nominal=0.01*mDis_flow_nominal" in mo
        assert "finalQLos_flow_nominal=0.05*QDis_flow_nominal" in mo
        assert "finalfRet=0.94" in mo
        assert "finalTMak=273.15+12.0" in mo
        assert "finalpSte=pSat" in mo

    def test_plant_and_network_are_connected_through_loss_component(self):
        mo = self.district_mo
        assert "connect(pla.port_bSerHea, losMak.port_aSte);" in mo
        assert "connect(losMak.port_bSte, dis.port_aDisSup);" in mo
        assert "connect(dis.port_bDisRet, losMak.port_aWat);" in mo
        assert "connect(losMak.port_bWat, pla.port_aSerHea);" in mo
        # the direct plant <-> network connections are replaced
        assert "connect(pla.port_bSerHea, dis.port_aDisSup);" not in mo
        assert "connect(dis.port_bDisRet, pla.port_aSerHea);" not in mo

    def test_loss_model_is_in_networks_package(self):
        networks_dir = Path(self.district._scaffold.networks_path.files_dir)
        model = networks_dir / "SteamLossAndMakeup.mo"
        assert model.exists()
        text = model.read_text()
        assert text.startswith("within steam_losses.Networks;")
        assert "model SteamLossAndMakeup" in text
        assert "SteamLossAndMakeup" in (networks_dir / "package.order").read_text()


class SteamNoCondensateReturnTest(TestCaseBase):
    """No condensate return enables the component even without other losses."""

    def setUp(self):
        super().setUp()
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, "steam_no_return")

    def test_no_return_case(self):
        district = _build_steam_district(
            self, "steam_no_return", "time_series_sys_params_steam_no_condensate_return.json"
        )
        mo = "".join(
            (Path(district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo").read_text().split()
        )
        assert "finalfRet=0.0" in mo

    def test_invalid_fraction_raises(self):
        params = json.loads((Path(self.data_dir) / "time_series_sys_params_steam_losses.json").read_text())
        params["district_system"]["first_generation"]["central_steam_plant_parameters"][
            "condensate_return_fraction"
        ] = 1.5
        sys_params = SystemParameters.loadd(params, validate_on_load=False)
        graph = CouplingGraph([Coupling(Network2Pipe(sys_params), SteamPlant(sys_params))])
        district = District(self.output_dir, "steam_invalid", sys_params, graph)
        with pytest.raises(ValueError, match="condensate_return_fraction"):
            district._first_generation_steam_losses("$.district_system.first_generation.central_steam_plant_parameters")


class SteamGeoJsonModelicaTranslatorTest(TestCaseBase):
    """GeoJsonModelicaTranslator builds 1G districts (previously failed with no couplings)."""

    def test_translator_builds_steam_district(self):
        data_dir, output_dir = self.set_up(Path(__file__).parent, "steam_gmt_translator")
        gmt = GeoJsonModelicaTranslator(
            Path(data_dir) / "time_series_ex2.json",
            Path(data_dir) / "time_series_sys_params_steam_losses.json",
            output_dir,
            "steam_gmt_translator",
        )
        gmt.to_modelica()
        district_mo = (output_dir / "steam_gmt_translator" / "Districts" / "DistrictEnergySystem.mo").read_text()
        assert "Plants.SteamBoiler pla" in district_mo
        assert "Networks.SteamLossAndMakeup losMak" in district_mo


class SteamLossesSimulationTest(TestCaseBase):
    def setUp(self):
        super().setUp()
        self.district = _build_steam_district(self, "steam_losses_sim", "time_series_sys_params_steam_losses.json")

    @pytest.mark.simulation
    def test_simulate_steam_losses_one_day(self):
        """Simulate one day with losses and check the mass and loss bookkeeping."""
        reader_module = pytest.importorskip("buildingspy.io.outputfile")
        name = f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem"
        success, results_path = ModelicaRunner().run_in_docker(
            "compile_and_run",
            name,
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=0,
            stop_time=86400,
            step_size=3600,
        )
        assert success is True
        mat = next(Path(results_path).glob("*_res.mat"))
        r = reader_module.Reader(str(mat), "dymola")

        def last(var):
            return r.values(var)[1][-1]

        # make-up water replaces exactly the leaked steam plus the discharged condensate
        assert last("losMak.VMak") * 1000 == pytest.approx(last("losMak.mLea") + last("losMak.VDum") * 1000, rel=1e-3)
        # constant losses, ramped in from 3600 s over 3600 s
        effective_seconds = 86400 - 3600 - 3600 / 2
        q_nominal = last("losMak.QLos_flow_nominal")
        assert last("losMak.ELos") == pytest.approx(q_nominal * effective_seconds, rel=1e-2)
        assert last("losMak.mLea") == pytest.approx(last("losMak.mLea_flow_nominal") * effective_seconds, rel=1e-2)
        # condensate is discharged (fRet = 0.94) and make-up water is used
        assert last("losMak.VDum") > 0
        # discharged condensate is not mixed with make-up water, so it leaves near the building condensate temperature
        assert last("losMak.TDum") > last("losMak.TSewMax")
        # tempering water cools the discharge to TSewMax with city water at TMak
        assert last("losMak.VTem") > 0
        assert last("losMak.VWat") == pytest.approx(last("losMak.VMak") + last("losMak.VTem"), rel=1e-3)
        assert re.fullmatch(r"0\.94\d*", f"{last('losMak.fRet')}")
