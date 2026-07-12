# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import re
import unittest
from pathlib import Path
from shutil import rmtree

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.modelica.GMT_Lib.DHC.DHC_5G_WH_GHX_HPTrio_VariableDist import (
    DHC5GWasteHeatGHXwithHPTrioVariableDist,
)
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from geojson_modelica_translator.utils import linecount

PARENT_DIR = Path(__file__).parent
GMT_LIB_PATH = PARENT_DIR.parent.parent / "geojson_modelica_translator" / "modelica" / "GMT_Lib"
DES_PARAMS = PARENT_DIR.parent / "data_shared" / "system_params_des_5g.json"

env = Environment(
    loader=FileSystemLoader(GMT_LIB_PATH),
    undefined=StrictUndefined,
    variable_start_string="{$",
    variable_end_string="$}",
)


class GmtLibDesHpTrioTest(unittest.TestCase):
    def test_dhc_5g_wh_ghx_hptrio_variabledist_build(self):
        # -- Setup
        package_output_dir = PARENT_DIR / "output"
        package_name = "DES_5G_HPTrio_VariableDist_Build"
        if (package_output_dir / package_name).exists():
            rmtree(package_output_dir / package_name)
        sys_params = SystemParameters(DES_PARAMS)

        # -- Act
        cpv = DHC5GWasteHeatGHXwithHPTrioVariableDist(sys_params)
        cpv.build_from_template(package_output_dir, package_name)

        # -- Assert
        # Did the mofile get created?
        assert linecount(package_output_dir / package_name / "Districts" / "district.mo") > 20
        with open(package_output_dir / package_name / "Districts" / "district.mo") as f:
            district_mo = f.read()
            # The test loads are cooling-dominant, and cooling peaks are stored as negative loads.
            assert "mPumDis_flow_nominal=22.95," in district_mo
            assert "mSto_flow_nominal=29.507," in district_mo
        with open(package_output_dir / package_name / "Districts" / "PartialSeries.mo") as f:
            partial_series_mo = f.read()
            dp_nominal_match = re.search(r"dp_nominal=([-+]?\d*\.?\d+)\)", partial_series_mo)
            assert dp_nominal_match is not None
            assert float(dp_nominal_match.group(1)) == pytest.approx(35409.0)
            # The borefield is autosized from the source flow so the per-borehole
            # flow (and thus the borefield pressure drop) stays bounded as loads
            # grow. The reference cooling-dominant district resolves to 300 boreholes.
            nbor_match = re.search(r"nBor = (\d+)", partial_series_mo)
            assert nbor_match is not None
            assert int(nbor_match.group(1)) == 300

    @pytest.mark.simulation
    def test_dhc_5g_wh_ghx_hptrio_variabledist_simulation(self):
        # -- Setup
        package_output_dir = PARENT_DIR / "output"
        package_name = "DES_5G_HPTrio_VariableDist_OM"
        if (package_output_dir / package_name).exists():
            rmtree(package_output_dir / package_name)
        sys_params = SystemParameters(DES_PARAMS)

        # -- Act
        cpv = DHC5GWasteHeatGHXwithHPTrioVariableDist(sys_params)
        cpv.build_from_template(package_output_dir, package_name)

        # -- Assert
        # Did the mofile get created?
        assert linecount(package_output_dir / package_name / "Districts" / "district.mo") > 20

        # Test to make sure that a zero SWH peak is set to a minimum value.
        # Otherwise, Modelica will error out.
        with open(package_output_dir / package_name / "Resources" / "Data" / "Districts" / "8" / "B11.mos") as f:
            assert "#Peak water heating load = 7714.5 Watts" in f.read()

        # # -- Act - with simulation
        runner = ModelicaRunner()
        # step_size=300 (5-min output) keeps the result file small and the run fast:
        # without it OpenModelica inherits the annual experiment-annotation interval count
        # (105120), oversampling a short run to ~0.8 s spacing and writing a >2 GB .mat.
        # Combined with the annotation Tolerance=1e-4, a 1-day run drops from ~12 min to ~20 s.
        success, _ = runner.run_in_docker(
            "compile_and_run",
            f"{package_name}.Districts.district",
            file_to_load=package_output_dir / package_name / "package.mo",
            run_path=package_output_dir / package_name,
            start_time=0,
            stop_time=86400,
            step_size=900,
        )

        assert success is True
