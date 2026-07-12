"""Shared 5G district flow sizing helpers."""

import math

CP_WATER_KJ_PER_KG_K = 4.18
DEFAULT_HEATING_COP = 2.5
DEFAULT_COOLING_COP = 3.5
DEFAULT_SWH_COP = 2.5
MIN_SOURCE_PUMP_DP_NOMINAL = 35000
SOURCE_PUMP_DP_PER_KG_S = 1200

# Design mass flow rate per borehole (kg/s). The borehole count is sized so that
# the source-side flow divided across the field keeps the per-borehole flow at or
# below this value. This value reproduces the historically stable reference field
# (~300 boreholes for the reference district) while letting the field scale with
# load. Keeping per-borehole flow bounded is what keeps the borefield pressure
# drop bounded (see borehole_count).
BOREHOLE_DESIGN_FLOW = 0.1
# Boreholes are laid out on a 10-wide grid (see cooBor in the template), so the
# count is rounded up to a whole number of rows.
BOREHOLE_GRID_WIDTH = 10
MIN_BOREHOLES = 10


def flow_rate_from_load(load_watts: float, delta_t: float, oversize_factor: float = 1.5) -> float:
    """Return mass flow rate in kg/s for a heat flow in Watts."""
    return oversize_factor * load_watts / (1000 * delta_t * CP_WATER_KJ_PER_KG_K)


def cop_from_params(ets_parameters: dict, key: str, default: float) -> float:
    """Return a valid COP from ETS parameters, falling back to the Modelica defaults."""
    try:
        cop = float((ets_parameters or {}).get(key, default))
    except (TypeError, ValueError):
        return default
    if cop <= 1:
        return default
    return cop


def source_side_loads(
    peak_heating_load: float,
    peak_cooling_load: float,
    peak_swh_load: float,
    ets_parameters: dict,
) -> tuple[float, float, float]:
    """Return heating extraction, cooling rejection, and SWH extraction loads.

    The storage/GHX loop is sized from the heat that must be exchanged with the
    ambient district loop, not from the building load directly. For heat pumps:
    heating extracts Q_load * (1 - 1/COP) from the source side, cooling rejects
    |Q_load| * (1 + 1/COP) to the source side, and SWH follows the heating
    extraction relationship. MOS cooling peaks are negative, so use magnitude.
    """
    heating_cop = cop_from_params(ets_parameters, "cop_heat_pump_heating", DEFAULT_HEATING_COP)
    cooling_cop = cop_from_params(ets_parameters, "cop_heat_pump_cooling", DEFAULT_COOLING_COP)
    swh_cop = cop_from_params(ets_parameters, "cop_heat_pump_hot_water", DEFAULT_SWH_COP)

    heating_extraction_load = peak_heating_load * (1 - 1 / heating_cop)
    cooling_rejection_load = abs(peak_cooling_load) * (1 + 1 / cooling_cop)
    swh_extraction_load = peak_swh_load * (1 - 1 / swh_cop)

    return heating_extraction_load, cooling_rejection_load, swh_extraction_load


def source_pump_dp_nominal(source_flow_rate: float) -> float:
    """Return a storage/GHX pump pressure head that tracks the source flow.

    The GMT 5G template uses an internal borefield branch whose pressure drop
    grows as the source-side mass flow increases. When mSto_flow_nominal is
    sized from heating extraction or cooling rejection, the default pump head
    can be far too small and the Buildings mover trips its dpMax assertion at
    initialization. Until the template exposes detailed GHE hydraulics, use a
    conservative flow-based head with a floor at the borefield nominal pressure
    drop.
    """
    return max(MIN_SOURCE_PUMP_DP_NOMINAL, SOURCE_PUMP_DP_PER_KG_S * source_flow_rate)


def borehole_count(
    source_flow_rate: float,
    design_flow_per_borehole: float = BOREHOLE_DESIGN_FLOW,
) -> int:
    """Return the number of boreholes to use for the given source-side flow.

    The borefield used to be a hard-coded 300-borehole field regardless of the
    district load. That works for small, mild districts but is fragile for large
    loads: the storage pump pushes the whole (load-scaled) source flow through a
    fixed number of parallel boreholes, so the per-borehole flow grows with load
    and the borefield pressure drop grows roughly with its square. Past a point,
    the pressure the borefield demands exceeds the storage pump's ``dpMax`` and
    the Buildings mover trips its assertion at initialization, so the model
    cannot even start -- exactly the kind of brittleness seen when handing the
    GMT large loads.

    Sizing the field so that the per-borehole flow stays at or below a fixed
    design value keeps the borefield pressure drop bounded (and therefore keeps
    the storage pump inside its operating envelope) no matter how large the
    district is. Large fields are expected and fine -- real sites use thousands
    of boreholes -- so the count is only floored, never capped. Because the
    source flow already scales with the load, a flow-based count also scales the
    field's thermal capacity with the load, which helps long, extreme-weather
    runs where a fixed field would otherwise saturate.

    Args:
        source_flow_rate: nominal storage/GHX (source-side) mass flow rate (kg/s).
        design_flow_per_borehole: target maximum mass flow per borehole (kg/s).

    Returns:
        Number of boreholes, rounded up to a whole number of grid rows.
    """
    if design_flow_per_borehole <= 0:
        raise ValueError("design_flow_per_borehole must be positive")
    rows = math.ceil(source_flow_rate / design_flow_per_borehole / BOREHOLE_GRID_WIDTH)
    return max(MIN_BOREHOLES, rows * BOREHOLE_GRID_WIDTH)
