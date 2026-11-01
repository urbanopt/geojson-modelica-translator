# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
#
# The minimum (standby) steam building load is applied as a floor on the space heating column of
# the copied load file, not as an offset added to every hour.

import filecmp
from pathlib import Path

import pytest

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings.coupling import Coupling
from geojson_modelica_translator.model_connectors.couplings.graph import CouplingGraph
from geojson_modelica_translator.model_connectors.districts.district import District
from geojson_modelica_translator.model_connectors.load_connectors.steam_building import write_steam_load_file
from geojson_modelica_translator.model_connectors.networks.network_2_pipe import Network2Pipe
from geojson_modelica_translator.model_connectors.plants.steam_boiler import SteamPlant
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase

MOS_HEADER = (
    "#1\n"
    "#First column: Seconds in the year (loads are hourly)\n"
    "#Peak space heating load = 1000.0 Watts\n"
    "double tab1(4,4)\n"
)


def _write(path: Path, separator: str, heating: list[float]) -> Path:
    rows = [separator.join([str(3600 * i), "-5.0", repr(q), "7.0"]) for i, q in enumerate(heating)]
    path.write_text(MOS_HEADER + "\n".join(rows) + "\n")
    return path


def _heating_column(path: Path) -> list[float]:
    values = []
    for line in path.read_text().splitlines():
        if not line or line[0] in "#d":
            continue
        fields = line.replace(";", ",").split(",") if ("," in line or ";" in line) else line.split()
        values.append(float(fields[2]))
    return values


@pytest.mark.parametrize("separator", [";", ",", " "])
def test_floor_raises_only_low_hours(tmp_path, separator):
    src = _write(tmp_path / "in.mos", separator, [0.0, 10.0, 500.0, 1000.0])
    stats = write_steam_load_file(str(src), str(tmp_path / "out.mos"), 0.02)
    assert _heating_column(tmp_path / "out.mos") == [20.0, 20.0, 500.0, 1000.0]
    assert stats["peak"] == 1000.0
    assert stats["minimum_load"] == pytest.approx(20.0)
    assert stats["hours_raised"] == 2
    assert stats["heating_energy_original"] == pytest.approx(1510.0)
    assert stats["heating_energy_with_minimum"] == pytest.approx(1540.0)
    # other columns and the header are unchanged
    out = (tmp_path / "out.mos").read_text()
    assert out.startswith(MOS_HEADER)
    assert out.count("-5.0") == 4
    assert out.count("7.0") == 4


def test_zero_fraction_copies_file_unchanged(tmp_path):
    src = _write(tmp_path / "in.mos", ";", [0.0, 10.0, 500.0, 1000.0])
    stats = write_steam_load_file(str(src), str(tmp_path / "out.mos"), 0.0)
    assert stats["hours_raised"] == 0
    assert filecmp.cmp(src, tmp_path / "out.mos", shallow=False)


def test_invalid_fraction_raises(tmp_path):
    src = _write(tmp_path / "in.mos", ";", [0.0, 1000.0])
    with pytest.raises(ValueError, match="minimum_load_fraction"):
        write_steam_load_file(str(src), str(tmp_path / "out.mos"), 1.5)


class SteamStandbyFloorDistrictTest(TestCaseBase):
    def setUp(self):
        super().setUp()
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, "steam_standby_floor")
        gj = UrbanOptGeoJson(Path(self.data_dir) / "time_series_ex2.json")
        self.sys_params = SystemParameters(Path(self.data_dir) / "time_series_sys_params_steam_3buildings.json")
        graph = CouplingGraph([Coupling(Network2Pipe(self.sys_params), SteamPlant(self.sys_params))])
        self.district = District(
            root_dir=self.output_dir,
            project_name="steam_standby_floor",
            system_parameters=self.sys_params,
            coupling_graph=graph,
            geojson_file=gj,
        )
        self.district.to_modelica()

    def test_building_model_has_no_load_offset(self):
        loads_path = Path(self.district._scaffold.loads_path.files_dir)
        for building_mo in loads_path.glob("*/building.mo"):
            text = building_mo.read_text()
            assert "offset" not in text
            assert "parameter Real minimum_load_fraction=0.02" in text

    def test_copied_load_file_is_floored(self):
        loads_path = Path(self.district._scaffold.loads_path.files_dir)
        copied = list(loads_path.glob("*/Resources/**/*.mos")) + list(
            Path(self.district._scaffold.project_path).glob("Loads/Resources/**/*.mos")
        )
        assert copied, "the building load file should be copied into the package"
        for mos in copied:
            heating = _heating_column(mos)
            peak = None
            for line in mos.read_text().splitlines():
                if line.startswith("#Peak space heating load"):
                    peak = float(line.split("=")[1].split()[0])
            assert peak is not None
            assert min(heating) >= 0.02 * peak * (1 - 1e-9)

    def test_district_limits_solver_step(self):
        district_mo = (Path(self.district._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo").read_text()
        assert 'maxStepSize="900"' in district_mo
