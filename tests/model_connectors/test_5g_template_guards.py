# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

"""Regression guards for 5G no-plant Modelica template rendering.

These tests render small Jinja template slices with minimal stubs and assert
that critical generated Modelica fragments stay present or absent for time-series
loads, fallback source temperatures, pressure references, and no-plant boundary
behavior.
"""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.load_connectors.time_series import TimeSeries
from geojson_modelica_translator.model_connectors.plants.no_plant_boundary import NoPlantBoundary
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters


def _render_template(template_path: Path, **context) -> str:
    env = Environment(loader=FileSystemLoader(template_path.parent), undefined=StrictUndefined)
    env.filters.update(ALL_CUSTOM_FILTERS)
    return env.get_template(template_path.name).render(context)


def _time_series_template_data(use_dry_cooling_coil=False):
    return {
        "load_resources_path": "Resources/Data/B1",
        "use_dry_cooling_coil": use_dry_cooling_coil,
        "cooling_terminal_model": "TestProject.Loads.FanCoil2PipeCoolingDry"
        if use_dry_cooling_coil
        else "Buildings.DHC.Loads.BaseClasses.Validation.BaseClasses.FanCoil2PipeCooling",
        "heat_cool_enable_threshold": 1e-2 if use_dry_cooling_coil else 1e-4,
        "service_water_start_temp": 293.15,
        "cop_heat_pump_heating": 2.5,
        "cop_heat_pump_cooling": 3.5,
        "cop_heat_pump_hot_water": 2.5,
        "chilled_water_supply_temp": 5,
        "heating_water_supply_temp": 50,
        "hot_water_supply_temp": 50,
        "ets_pump_head": 10000,
        "time_series": {"filename": "modelica.mos"},
        "nominal_values": {
            "has_liquid_heating": "true",
            "has_liquid_cooling": "true",
            "has_electric_heating": "false",
            "has_electric_cooling": "false",
            "hhw_supply_temp": 313.15,
            "chw_supply_temp": 280.15,
            "chw_return_temp": 285.15,
            "temp_setpoint_heating": 293.15,
            "temp_setpoint_cooling": 297.15,
            "max_electrical_load": 0,
        },
    }


class _GraphStub:
    def __init__(self, couplings=None, other_model=None):
        self._couplings = couplings or {}
        self._other_model = other_model or SimpleNamespace(id="Dis_NoPlant")

    def couplings_by_type(self, model_id):
        return self._couplings.get(model_id, SimpleNamespace())

    def get_other_model(self, coupling_id, network_id):
        return self._other_model

    def get_ghe_id(self, coupling_id):
        return "ghe-1"

    def get_source_id(self, coupling_id):
        return "src-1"


def test_time_series_building_defaults_to_wet_cooling_terminal():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "load_connectors"
        / "templates"
        / "TimeSeriesBuilding.mot"
    )

    rendered = _render_template(
        template_path,
        project_name="TestProject",
        model_name="B1",
        data=_time_series_template_data(use_dry_cooling_coil=False),
    )

    assert (
        "replaceable Buildings.DHC.Loads.BaseClasses.Validation.BaseClasses.FanCoil2PipeCooling terUniCoo" in rendered
    )
    assert "hexWetNtu(" in rendered
    assert "SHR(" in rendered
    assert "min=-1e-6" in rendered
    assert "max=1+1e-6" in rendered.replace(" ", "")
    assert "mLoaHea_flow_nominal=mLoaHea_flow_nominal/facMulHea" in rendered
    assert "mLoaCoo_flow_nominal=mLoaCoo_flow_nominal/facMulCoo" in rendered
    assert "FanCoil2PipeCoolingDry terUniCoo" not in rendered


def test_time_series_building_uses_dry_cooling_terminal_when_requested():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "load_connectors"
        / "templates"
        / "TimeSeriesBuilding.mot"
    )

    rendered = _render_template(
        template_path,
        project_name="TestProject",
        model_name="B1",
        data=_time_series_template_data(use_dry_cooling_coil=True),
    )

    assert "replaceable TestProject.Loads.FanCoil2PipeCoolingDry terUniCoo" in rendered
    assert "Buildings.DHC.Loads.BaseClasses.Validation.BaseClasses.FanCoil2PipeCooling terUniCoo" not in rendered
    assert "hexWetNtu(" not in rendered


def test_partial_heat_pump_cooling_relaxes_small_negative_runtime_values():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "energy_transfer_systems"
        / "templates"
        / "PartialHeatPumpCooling.mopt"
    )

    rendered = _render_template(template_path, project_name="TestProject")

    assert re.search(r"yPL\s*\(\s*min\s*=\s*-1e-6\s*\)", rendered)
    assert re.search(r"m1_flow\s*\(\s*min\s*=\s*-1e-6\s*,\s*max\s*=\s*1e5\s*\+\s*1e-6\s*\)", rendered)
    assert re.search(r"m2_flow\s*\(\s*min\s*=\s*-1e-6\s*,\s*max\s*=\s*1e5\s*\+\s*1e-6\s*\)", rendered)
    assert re.search(
        r"pumCon\s*\(\s*energyDynamics\s*=\s*Modelica\.Fluid\.Types\.Dynamics\.SteadyState",
        rendered,
    )


def test_time_series_building_with_ets_uses_larger_enable_threshold_for_dry_coil():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "load_connectors"
        / "templates"
        / "TimeSeriesBuildingWithETS.mot"
    )

    rendered = _render_template(
        template_path,
        project_name="TestProject",
        model_name="B1",
        data=_time_series_template_data(use_dry_cooling_coil=True),
    )

    assert "each uLow=0.01" in rendered
    assert "each uHigh=0.1" in rendered
    assert "final TSerWat_start=293.15" in rendered
    assert "ceil(\n          QHea_flow_nominal/(1.7E5))" in rendered
    assert "ceil(\n          abs(\n            QCoo_flow_nominal)/(1.5E5))" in rendered


def test_copy_mos_with_zero_start_inserts_zero_load_row_and_updates_count(tmp_path):
    source = tmp_path / "source.mos"
    target = tmp_path / "target.mos"
    source.write_text("#1\n# header\ndouble tab1(2,4)\n3600;-1;2;3\n7200;-4;5;6\n")

    TimeSeries._copy_mos_with_zero_start(source, target)

    assert target.read_text().splitlines() == [
        "#1",
        "# header",
        "double tab1(3,4)",
        "0;0;0;0",
        "3600;-1;2;3",
        "7200;-4;5;6",
    ]


def test_copy_mos_with_zero_start_leaves_existing_zero_start_unchanged(tmp_path):
    source = tmp_path / "source.mos"
    target = tmp_path / "target.mos"
    source.write_text("#1\ndouble tab1(2,4)\n0;-1;2;3\n3600;-4;5;6\n")

    TimeSeries._copy_mos_with_zero_start(source, target)

    assert target.read_text().splitlines() == [
        "#1",
        "double tab1(2,4)",
        "0;-1;2;3",
        "3600;-4;5;6",
    ]


def _time_series_for_cooling_coil_selection(time_series_parameters, fifth_generation=None):
    time_series = TimeSeries.__new__(TimeSeries)
    time_series.building_id = "B1"
    time_series.system_parameters = SystemParameters.loadd(
        {
            "buildings": [
                {
                    "geojson_id": "B1",
                    "load_model": "time_series",
                    "load_model_parameters": {"time_series": time_series_parameters},
                }
            ],
            "district_system": {
                "fifth_generation": fifth_generation
                or {
                    "soil": {"undisturbed_temp": 18.3},
                    "no_central_plant": {"distribution_temperature": 18.3},
                }
            },
        },
        validate_on_load=False,
    )
    return time_series


def test_no_plant_fifth_generation_defaults_to_dry_cooling_coil():
    time_series = _time_series_for_cooling_coil_selection({})

    assert time_series._use_dry_cooling_coil(is_no_plant_fifth_generation=True) is True


def test_no_plant_fifth_generation_allows_wet_cooling_coil_when_requested():
    time_series = _time_series_for_cooling_coil_selection({"use_wet_cooling_coil": True})

    assert time_series._use_dry_cooling_coil(is_no_plant_fifth_generation=True) is False


def test_time_series_rejects_conflicting_cooling_coil_requests():
    time_series = _time_series_for_cooling_coil_selection({"use_dry_cooling_coil": True, "use_wet_cooling_coil": True})

    with pytest.raises(ValueError, match="Only one of use_dry_cooling_coil or use_wet_cooling_coil can be true"):
        time_series._use_dry_cooling_coil(is_no_plant_fifth_generation=True)


def test_time_series_unidirectional_series_skips_when_network_has_no_plant_couplings():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(couplings={"UniNet_1": SimpleNamespace()})
    loop_order = SimpleNamespace(number_of_loops=1, number_of_sources=0, data=[{"list_bldg_ids_in_group": ["bldg-1"]}])
    coupling = {"id": "CPL_1", "network": {"id": "UniNet_1"}, "load": {"id": "TimeSerLoa_bldg-1"}}

    rendered = _render_template(template_path, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "connect(UniNet_1.ports_bCon[1], TimeSerLoa_bldg-1.port_aSerAmb)" in rendered
    assert "connect(TimeSerLoa_bldg-1.port_bSerAmb, UniNet_1.ports_aCon[1])" in rendered
    assert "connect(UniNet_1.TOut, conPum.TMix[1:1])" in rendered
    assert "connect(TimeSerLoa_bldg-1.QCoo_flow, conPum.QCoo_flow[1])" in rendered
    assert "connect(THeaWatSupMinSet_CPL_1.y" in rendered


def test_unidirectional_series_ground_coupling_skips_when_distribution_has_no_plant_couplings():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "UnidirectionalSeries_GroundCoupling"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(couplings={"Dis_NoPlant": SimpleNamespace()})
    loop_order = SimpleNamespace(
        number_of_loops=1,
        data=[{"list_bldg_ids_in_group": ["bldg-1"], "list_ghe_ids_in_group": ["ghe-1"]}],
    )
    coupling = {"id": "CPL_2", "network": {"id": "GroCou_1"}}

    rendered = _render_template(template_path, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "connect(Dis_NoPlant.heatPortGro" not in rendered
    assert "annotation" in rendered


def test_ground_coupling_instance_omits_soidat_without_plant_couplings():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "networks"
        / "templates"
        / "GroundCoupling_Instance.mopt"
    )

    graph = _GraphStub(couplings={"GroCou_1": SimpleNamespace()})
    model = {"id": "GroCou_1", "modelica_type": "Networks.GroundCoupling"}
    sys_params = {
        "district_system": {
            "fifth_generation": {
                "horizontal_piping_parameters": {
                    "hydraulic_diameter": 0.2,
                    "diameter_ratio": 2.6,
                    "insulation_thickness": 0.05,
                }
            }
        }
    }

    rendered = _render_template(template_path, graph=graph, model=model, sys_params=sys_params)

    assert "soiDat=" not in rendered
    assert "len=cat(" in rendered


def test_unidirectional_series_instance_skips_loop_parameters_without_plant_couplings():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "networks"
        / "templates"
        / "UnidirectionalSeries_Instance.mopt"
    )

    graph = _GraphStub(couplings={"UniNet_1": SimpleNamespace()})
    model = {"id": "UniNet_1", "modelica_type": "Networks.UnidirectionalSeries"}
    loop_order = SimpleNamespace(
        number_of_loops=1,
        data=[{"list_bldg_ids_in_group": ["bldg-1"], "list_ghe_ids_in_group": ["ghe-1"]}],
    )
    sys_params = {"district_system": {"fifth_generation": {"ghe_parameters": {}}}}
    globals_ctx = {"medium_w": "MediumW"}

    rendered = _render_template(
        template_path,
        graph=graph,
        model=model,
        loop_order=loop_order,
        sys_params=sys_params,
        globals=globals_ctx,
    )

    assert "final nCon= 1" in rendered
    assert "final allowFlowReversal=allowFlowReversalSer" in rendered


def test_unidirectional_series_borefield_adds_supply_pressure_reference():
    comp_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "UnidirectionalSeries_Borefield"
        / "ComponentDefinitions.mopt"
    )
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "UnidirectionalSeries_Borefield"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub()
    loop_order = SimpleNamespace(
        number_of_loops=1,
        data=[{"list_bldg_ids_in_group": ["bldg-1"], "list_ghe_ids_in_group": ["ghe-1"]}],
    )
    coupling = SimpleNamespace(
        id="CPL_GHE",
        network=SimpleNamespace(id="UniNet_1"),
        plant=SimpleNamespace(id="borFie_1"),
    )
    sys_params = {"district_system": {"fifth_generation": {"soil": {"undisturbed_temp": 18.3}}}}
    globals_ctx = {"medium_w": "MediumW"}

    rendered_comp = _render_template(
        comp_template,
        graph=graph,
        loop_order=loop_order,
        coupling=coupling,
        sys_params=sys_params,
        globals=globals_ctx,
    )
    rendered_conn = _render_template(conn_template, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "Buildings.Fluid.Sources.Boundary_pT supGheRef_CPL_GHE" in rendered_comp
    assert "p=101325" in rendered_comp
    assert "T=18.3 + 273.15" in rendered_comp
    assert "connect(pumDis.port_b, TDisSup_CPL_GHE.port_a)" in rendered_conn
    assert "connect(supGheRef_CPL_GHE.ports[1], pumDis.port_b)" in rendered_conn


def test_network_distribution_pump_uses_single_fallback_source_when_no_sources_present():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "networks"
        / "templates"
        / "NetworkDistributionPump_Instance.mopt"
    )

    loop_order = SimpleNamespace(number_of_sources=0)
    sys_params = {
        "district_system": {
            "fifth_generation": {
                "central_pump_parameters": {"pump_design_head": 200000},
                "no_central_plant": {"distribution_temperature": 18.3},
                "soil": {"undisturbed_temp": 18.3},
            }
        }
    }
    globals_ctx = {"medium_w": "MediumW"}

    rendered = _render_template(
        template_path,
        loop_order=loop_order,
        sys_params=sys_params,
        globals=globals_ctx,
    )

    assert "nSou=1" in rendered
    # Distribution mass-flow command is low-pass filtered to damp step-load
    # transients (prevents the pump forcing flow through transiently-closed
    # ETS valves, which spikes head past dpMax at relaxed solver tolerances).
    assert "Modelica.Blocks.Continuous.FirstOrder filDis" in rendered
    assert "initType=Modelica.Blocks.Types.Init.SteadyState" in rendered


def test_time_series_unidirectional_series_renders_fallback_tsouout_for_no_source_case():
    comp_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ComponentDefinitions.mopt"
    )
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(couplings={"UniNet_1": SimpleNamespace()})
    loop_order = SimpleNamespace(
        number_of_loops=1,
        number_of_sources=0,
        data=[{"list_bldg_ids_in_group": ["bldg-1"]}],
    )
    coupling = {"id": "CPL_1", "network": {"id": "UniNet_1"}, "load": {"id": "TimeSerLoa_bldg-1"}}
    sys_params = {
        "building": {
            "fifth_gen_ets_parameters": {
                "chilled_water_supply_temp": 5,
                "heating_water_supply_temp": 50,
                "hot_water_supply_temp": 50,
            }
        },
        "district_system": {
            "fifth_generation": {
                "soil": {"undisturbed_temp": 18.3},
                "no_central_plant": {"distribution_temperature": 18.3},
            }
        },
    }

    rendered_comp = _render_template(
        comp_template, graph=graph, loop_order=loop_order, coupling=coupling, sys_params=sys_params
    )
    rendered_conn = _render_template(
        conn_template, graph=graph, loop_order=loop_order, coupling=coupling, sys_params=sys_params
    )

    assert "TSouIn_fallback_UniNet_1" in rendered_comp
    assert "TSouOut_fallback_UniNet_1" in rendered_comp
    assert "connect(TSouIn_fallback_UniNet_1.y, conPum.TSouIn[1])" in rendered_conn
    assert "connect(TSouOut_fallback_UniNet_1.y, conPum.TSouOut[1])" in rendered_conn
    assert "bound_heatPort_UniNet_1_p1" not in rendered_comp


def test_time_series_unidirectional_series_uses_no_central_plant_temperature_for_no_plant_fallbacks():
    comp_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ComponentDefinitions.mopt"
    )
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(couplings={"UniNet_1": SimpleNamespace()})
    loop_order = SimpleNamespace(
        number_of_loops=1,
        number_of_sources=0,
        data=[{"list_bldg_ids_in_group": ["bldg-1"]}],
    )
    coupling = {"id": "CPL_1", "network": {"id": "UniNet_1"}, "load": {"id": "TimeSerLoa_bldg-1"}}
    sys_params = {
        "building": {
            "fifth_gen_ets_parameters": {
                "chilled_water_supply_temp": 5,
                "heating_water_supply_temp": 50,
                "hot_water_supply_temp": 50,
            }
        },
        "district_system": {
            "fifth_generation": {
                "soil": {"undisturbed_temp": 18.3},
                "no_central_plant": {"distribution_temperature": 16.7},
            }
        },
    }

    rendered_comp = _render_template(
        comp_template, graph=graph, loop_order=loop_order, coupling=coupling, sys_params=sys_params
    )
    rendered_conn = _render_template(
        conn_template, graph=graph, loop_order=loop_order, coupling=coupling, sys_params=sys_params
    )

    assert "TSouIn_fallback_UniNet_1(k=16.7 + 273.15)" in rendered_comp
    assert "TSouOut_fallback_UniNet_1(k=16.7 + 1 + 273.15)" in rendered_comp
    assert "TChiWatSupSet_CPL_1(k=5 + 273.15)" in rendered_comp
    assert "THeaWatSupMaxSet_CPL_1(k=50 +" in rendered_comp
    assert "THotWatSupSet_CPL_1(k=50 + 273.15)" in rendered_comp
    # original direct pump-to-network and network-return-to-pump connections present
    assert "connect(pumDis.port_b, UniNet_1.port_aDisSup)" in rendered_conn
    assert "connect(UniNet_1.port_bDisSup, pumDis.port_a)" in rendered_conn


def test_time_series_unidirectional_series_connects_explicit_no_plant_pressure_reference():
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "TimeSeries_UnidirectionalSeries"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(
        couplings={"UniNet_1": SimpleNamespace(plant_couplings=[{"id": "CPL_NOPL"}])},
        other_model=SimpleNamespace(id="noPla_1"),
    )
    loop_order = SimpleNamespace(
        number_of_loops=1,
        number_of_sources=0,
        data=[{"list_bldg_ids_in_group": ["bldg-1"]}],
    )
    coupling = {"id": "CPL_1", "network": {"id": "UniNet_1"}, "load": {"id": "TimeSerLoa_bldg-1"}}

    rendered = _render_template(conn_template, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "connect(pumDis.port_b, heaNoPlant_CPL_NOPL.port_a)" in rendered
    assert "connect(supNoPlant_CPL_NOPL.ports[1], pumDis.port_b)" in rendered
    assert "connect(cooNoPlant_CPL_NOPL.port_b, UniNet_1.port_aDisSup)" in rendered
    assert "connect(UniNet_1.port_bDisSup, pumDis.port_a)" in rendered


def test_network_distribution_pump_connect_keeps_base_connections_when_no_sources():
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "NetworkDistributionPump_NetworkDistributionPump"
        / "ConnectStatements.mopt"
    )

    loop_order = SimpleNamespace(number_of_sources=0)

    rendered = _render_template(conn_template, loop_order=loop_order)

    # No extra bypass connections for no-source case in this template
    assert "connect(expVes.ports[1], pumDis.port_a)" in rendered
    assert "connect(conPum.y, gai.u)" in rendered
    # Mass-flow command is routed through the low-pass filter before the pump
    assert "connect(gai.y, filDis.u)" in rendered
    assert "connect(filDis.y, pumDis.m_flow_in)" in rendered


def test_unidirectional_series_instance_treats_explicit_no_plant_boundary_like_no_plant_case():
    template_path = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "networks"
        / "templates"
        / "UnidirectionalSeries_Instance.mopt"
    )

    graph = _GraphStub(
        couplings={"UniNet_1": SimpleNamespace(plant_couplings=[{"id": "CPL_NOPL"}])},
        other_model=SimpleNamespace(id="noPla_1"),
    )
    model = {"id": "UniNet_1", "modelica_type": "Networks.UnidirectionalSeries"}
    loop_order = SimpleNamespace(
        number_of_loops=1,
        data=[{"list_bldg_ids_in_group": ["bldg-1"], "list_ghe_ids_in_group": ["ghe-1"]}],
    )
    sys_params = {"district_system": {"fifth_generation": {"ghe_parameters": {}}}}
    globals_ctx = {"medium_w": "MediumW"}

    rendered = _render_template(
        template_path,
        graph=graph,
        model=model,
        loop_order=loop_order,
        sys_params=sys_params,
        globals=globals_ctx,
    )

    assert "final nCon= 1" in rendered
    assert "final allowFlowReversal=allowFlowReversalSer" in rendered


def test_unidirectional_series_no_plant_boundary_uses_no_central_plant_temperature():
    comp_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "UnidirectionalSeries_NoPlantBoundary"
        / "ComponentDefinitions.mopt"
    )
    conn_template = (
        Path(__file__).parents[2]
        / "geojson_modelica_translator"
        / "model_connectors"
        / "couplings"
        / "5G_templates"
        / "UnidirectionalSeries_NoPlantBoundary"
        / "ConnectStatements.mopt"
    )

    graph = _GraphStub(couplings={"UniNet_1": SimpleNamespace(plant_couplings=[{"id": "CPL_NOPL"}])})
    loop_order = SimpleNamespace(number_of_loops=1, data=[{"list_bldg_ids_in_group": ["bldg-1", "bldg-2"]}])
    coupling = {"id": "CPL_NOPL", "network": {"id": "UniNet_1"}}
    sys_params = {
        "district_system": {
            "fifth_generation": {
                "soil": {"undisturbed_temp": 16.7},
                "no_central_plant": {"distribution_temperature": 17.2},
                "central_pump_parameters": {"pump_design_head": 200000},
            }
        }
    }
    globals_ctx = {"medium_w": "MediumW"}

    rendered_comp = _render_template(
        comp_template,
        graph=graph,
        loop_order=loop_order,
        coupling=coupling,
        sys_params=sys_params,
        globals=globals_ctx,
    )
    rendered_conn = _render_template(conn_template, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "TNoPlant_CPL_NOPL(" in rendered_comp
    assert "heaNoPlant_CPL_NOPL(" in rendered_comp
    assert "cooNoPlant_CPL_NOPL(" in rendered_comp
    assert "supNoPlant_CPL_NOPL(" in rendered_comp
    assert "p=101325" in rendered_comp
    assert "qIdePlaRev_CPL_NOPL=max(" in rendered_comp
    assert "heaNoPlant_CPL_NOPL.port_a.h_outflow - heaNoPlant_CPL_NOPL.port_b.h_outflow" in rendered_comp
    assert "pIdePlaHea_CPL_NOPL=max(" in rendered_comp
    assert "-qIdePlaRev_CPL_NOPL" in rendered_comp
    assert "pIdePlaCoo_CPL_NOPL=max(" in rendered_comp
    assert "qIdePlaRev_CPL_NOPL" in rendered_comp
    assert "etaIdePumDis_CPL_NOPL" in rendered_comp
    assert "rhoIdePumDis_CPL_NOPL" in rendered_comp
    assert "pIdePumDis_CPL_NOPL=max(" in rendered_comp
    assert "*200000/etaIdePumDis_CPL_NOPL" in rendered_comp
    assert "bound_heatPort_CPL_NOPL(" in rendered_comp
    assert "k=17.2 + 273.15" in rendered_comp
    assert "T=17.2 + 273.15" in rendered_comp
    assert "T=273.15 + 16.7)" in rendered_comp
    assert "connect(TNoPlant_CPL_NOPL.y, heaNoPlant_CPL_NOPL.TSet)" in rendered_conn
    assert "connect(TNoPlant_CPL_NOPL.y, cooNoPlant_CPL_NOPL.TSet)" in rendered_conn
    assert "connect(bound_heatPort_CPL_NOPL.port, UniNet_1.heatPortGro[3])" in rendered_conn


def test_no_plant_boundary_requires_distribution_temperature():
    sys_params = SystemParameters.loadd(
        {
            "buildings": [],
            "district_system": {
                "fifth_generation": {
                    "horizontal_piping_parameters": {"pressure_drop_per_meter": 300},
                }
            },
        },
        validate_on_load=False,
    )

    with pytest.raises(ValueError, match=r"no_central_plant\.distribution_temperature"):
        NoPlantBoundary(sys_params)
