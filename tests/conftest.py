# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

# -*- coding: utf-8 -*-
"""Shared pytest configuration."""

from pathlib import Path

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Keep tests that share files on the same xdist worker.

    Resource-intensive tests use one group so they remain serial even if a
    developer invokes pytest with xdist directly. Other tests are grouped by
    module, except translator tests, which share a common output directory.
    """
    tests_root = Path(__file__).parent
    shared_waste_heat_paths = {
        Path("management/test_uo_des.py"),
        Path("model_connectors/test_waste_heat_district.py"),
    }

    for item in items:
        if any(item.get_closest_marker(marker) for marker in ("simulation", "compilation", "dymola")):
            group = "resource-intensive"
        else:
            relative_path = item.path.relative_to(tests_root)
            if relative_path.parts[0] == "geojson_modelica_translator":
                group = "geojson-modelica-translator"
            elif relative_path in shared_waste_heat_paths:
                group = "shared-waste-heat"
            else:
                group = str(relative_path)

        item.add_marker(pytest.mark.xdist_group(name=group))
