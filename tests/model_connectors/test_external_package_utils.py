"""Tests for loop-order template parameter helpers in external_package_utils.

This module verifies fallback behavior in
set_loop_order_data_in_template_params when no matching thermal connector
lengths are found. It ensures the function:

1. Produces deterministic zero-length defaults for lDis and lEnd.
2. Preserves loop-order metadata counts.
3. Sizes fallback lDis from the number of buildings in loop_order.
"""

from geojson_modelica_translator.external_package_utils import set_loop_order_data_in_template_params


def test_set_loop_order_data_handles_no_matching_pipe_lengths():
    template_params = {"globals": {}}
    feature_properties = [
        {
            "type": "Building",
            "id": "bldg-1",
        }
    ]
    loop_order = [{"list_bldg_ids_in_group": ["bldg-1"]}]

    result = set_loop_order_data_in_template_params(template_params, feature_properties, loop_order)

    assert result["globals"]["lDis"] == "fill(0, 0)"
    assert result["globals"]["lEnd"] == 0
    assert result["loop_order"]["number_of_loops"] == 1
    assert result["loop_order"]["number_of_sources"] == 0


def test_set_loop_order_data_fallback_ldis_size_uses_loop_order_buildings():
    template_params = {"globals": {}}
    feature_properties = [
        {
            "type": "Building",
            "id": "bldg-1",
        }
    ]
    loop_order = [{"list_bldg_ids_in_group": ["bldg-1", "bldg-2", "bldg-3"]}]

    result = set_loop_order_data_in_template_params(template_params, feature_properties, loop_order)

    assert result["globals"]["lDis"] == "fill(0, 2)"
    assert result["globals"]["lEnd"] == 0
