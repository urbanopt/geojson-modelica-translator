# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import pytest

from geojson_modelica_translator.modelica.GMT_Lib.DHC._flow_sizing import (
    BOREHOLE_DESIGN_FLOW,
    MIN_BOREHOLES,
    borehole_count,
    flow_rate_from_load,
    source_pump_dp_nominal,
)


class TestFlowSizing:
    def test_flow_rate_from_load_oversizes(self):
        # 100 kW over a 5 K delta-T with the default 1.5x oversize factor.
        assert flow_rate_from_load(100_000, 5) == pytest.approx(1.5 * 100_000 / (1000 * 5 * 4.18))

    def test_source_pump_dp_has_floor(self):
        # Small flows are held at the borefield nominal pressure drop floor.
        assert source_pump_dp_nominal(1.0) == 35000
        # Larger flows scale linearly above the floor.
        assert source_pump_dp_nominal(100.0) == pytest.approx(120000)

    def test_borehole_count_reference_district(self):
        # The reference cooling-dominant district (source flow ~29.5 kg/s) keeps
        # the historically stable 300-borehole field.
        assert borehole_count(29.507) == 300

    def test_borehole_count_scales_with_load(self):
        # Quadrupling the load (and thus the source flow) roughly quadruples the
        # field so the per-borehole flow stays bounded.
        n = borehole_count(118.03)
        assert n == 1190
        assert 118.03 / n <= BOREHOLE_DESIGN_FLOW

    def test_borehole_count_bounds_per_borehole_flow(self):
        # Across a wide range of loads, the per-borehole flow never exceeds the
        # design value -- this is what keeps the borefield pressure drop (and the
        # storage pump head) inside the mover's operating envelope.
        for flow in [0.5, 5, 30, 118, 300, 632]:
            n = borehole_count(flow)
            assert flow / n <= BOREHOLE_DESIGN_FLOW

    def test_borehole_count_is_grid_aligned_and_floored(self):
        assert borehole_count(0.001) == MIN_BOREHOLES
        # Always a whole number of 10-wide grid rows.
        for flow in [3, 17, 41, 118]:
            assert borehole_count(flow) % 10 == 0

    def test_borehole_count_rejects_nonpositive_design_flow(self):
        with pytest.raises(ValueError, match="design_flow_per_borehole must be positive"):
            borehole_count(30, design_flow_per_borehole=0)
