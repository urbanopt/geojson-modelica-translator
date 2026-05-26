"""Tests for loop-order helpers in external_package_utils.

This module verifies fallback behavior in
set_loop_order_data_in_template_params when no matching thermal connector
lengths are found. It ensures the function:

1. Produces deterministic zero-length defaults for lDis and lEnd.
2. Preserves loop-order metadata counts.
3. Sizes fallback lDis from the number of buildings in loop_order.
"""

import json
from pathlib import Path

from geojson_modelica_translator.external_package_utils import (
    load_loop_order,
    normalize_package_order,
    normalize_package_orders_recursively,
    set_loop_order_data_in_template_params,
)


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


def test_load_loop_order_writes_default_for_missing_file(tmp_path: Path):
    sys_params_path = tmp_path / "sys_params_5g.json"
    sys_params = {
        "district_system": {
            "fifth_generation": {
                "ghe_parameters": {"borefields": [{"ghe_id": "ghe-1"}]},
                "heat_source_parameters": [{"heat_source_id": "hs-1"}],
            }
        },
        "buildings": [{"geojson_id": "bldg-1"}, {"geojson_id": "bldg-2"}],
    }
    sys_params_path.write_text(json.dumps(sys_params, indent=2))

    loop_order = load_loop_order(sys_params_path)

    assert loop_order == [
        {
            "list_bldg_ids_in_group": ["bldg-1", "bldg-2"],
            "list_ghe_ids_in_group": ["ghe-1"],
            "list_source_ids_in_group": ["hs-1"],
        }
    ]
    assert (tmp_path / "_loop_order.json").exists()


def test_load_loop_order_raises_for_non_5g_when_missing(tmp_path: Path):
    sys_params_path = tmp_path / "sys_params_4g.json"
    sys_params = {
        "district_system": {"fourth_generation": {}},
        "buildings": [{"geojson_id": "bldg-1"}],
    }
    sys_params_path.write_text(json.dumps(sys_params, indent=2))

    try:
        load_loop_order(sys_params_path)
        raise AssertionError("Expected FileNotFoundError for missing loop order in non-5G params")
    except FileNotFoundError:
        pass


def test_normalize_package_order_appends_missing_models_and_subpackages(tmp_path: Path):
    package_dir = tmp_path / "Networks"
    package_dir.mkdir()
    (package_dir / "package.mo").write_text("within Demo; package Networks end Networks;\n")
    (package_dir / "Existing.mo").write_text("within Demo.Networks; model Existing end Existing;\n")
    (package_dir / "Missing.mo").write_text("within Demo.Networks; model Missing end Missing;\n")
    nested = package_dir / "SubPkg"
    nested.mkdir()
    (nested / "package.mo").write_text("within Demo.Networks; package SubPkg end SubPkg;\n")
    (package_dir / "package.order").write_text("Existing\n")

    normalize_package_order(package_dir)

    order = (package_dir / "package.order").read_text().splitlines()
    assert order[0] == "Existing"
    assert "Missing" in order
    assert "SubPkg" in order


def test_normalize_package_orders_recursively_updates_nested_packages(tmp_path: Path):
    root = tmp_path / "Demo"
    loads_dir = root / "Loads" / "B1"
    loads_dir.mkdir(parents=True)
    (loads_dir / "package.mo").write_text("within Demo.Loads; package B1 end B1;\n")
    (loads_dir / "TimeSeriesBuilding.mo").write_text(
        "within Demo.Loads.B1; model TimeSeriesBuilding end TimeSeriesBuilding;\n"
    )
    (loads_dir / "building.mo").write_text("within Demo.Loads.B1; model building end building;\n")
    (loads_dir / "package.order").write_text("building\n")

    normalize_package_orders_recursively(root)

    order = (loads_dir / "package.order").read_text().splitlines()
    assert "building" in order
    assert "TimeSeriesBuilding" in order
