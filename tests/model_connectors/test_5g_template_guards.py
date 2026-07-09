from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.plants.no_plant_boundary import NoPlantBoundary
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters


def _render_template(template_path: Path, **context) -> str:
    env = Environment(loader=FileSystemLoader(template_path.parent), undefined=StrictUndefined)
    env.filters.update(ALL_CUSTOM_FILTERS)
    return env.get_template(template_path.name).render(context)


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
        "district_system": {"fifth_generation": {"soil": {"undisturbed_temp": 18.3}}},
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


def test_time_series_unidirectional_series_uses_soil_undisturbed_temp_for_no_plant_fallbacks():
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
        "district_system": {"fifth_generation": {"soil": {"undisturbed_temp": 16.7}}},
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


def test_unidirectional_series_no_plant_boundary_uses_soil_undisturbed_temp():
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
    sys_params = {"district_system": {"fifth_generation": {"soil": {"undisturbed_temp": 16.7}}}}
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
    assert "bound_heatPort_CPL_NOPL(" in rendered_comp
    assert "T=273.15 + 16.7)" in rendered_comp
    assert "connect(TNoPlant_CPL_NOPL.y, heaNoPlant_CPL_NOPL.TSet)" in rendered_conn
    assert "connect(TNoPlant_CPL_NOPL.y, cooNoPlant_CPL_NOPL.TSet)" in rendered_conn
    assert "connect(bound_heatPort_CPL_NOPL.port, UniNet_1.heatPortGro[3])" in rendered_conn


def test_no_plant_boundary_requires_soil_undisturbed_temp():
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

    with pytest.raises(ValueError, match=r"soil\.undisturbed_temp"):
        NoPlantBoundary(sys_params)
