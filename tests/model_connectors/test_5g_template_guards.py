from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS


def _render_template(template_path: Path, **context) -> str:
    env = Environment(loader=FileSystemLoader(template_path.parent), undefined=StrictUndefined)
    env.filters.update(ALL_CUSTOM_FILTERS)
    return env.get_template(template_path.name).render(context)


class _GraphStub:
    def __init__(self, couplings=None):
        self._couplings = couplings or {}

    def couplings_by_type(self, model_id):
        return self._couplings.get(model_id, SimpleNamespace())

    def get_other_model(self, coupling_id, network_id):
        return SimpleNamespace(id="Dis_NoPlant")

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
    loop_order = SimpleNamespace(number_of_loops=1, data=[{"list_bldg_ids_in_group": ["bldg-1"]}])
    coupling = {"id": "CPL_1", "network": {"id": "UniNet_1"}, "load": {"id": "TimeSerLoa_bldg-1"}}

    rendered = _render_template(template_path, graph=graph, loop_order=loop_order, coupling=coupling)

    assert "connect(UniNet_1.ports_bCon" not in rendered
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

    assert "final nCon=" not in rendered
    assert "final allowFlowReversal=allowFlowReversalSer" in rendered
