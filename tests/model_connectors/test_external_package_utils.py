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
