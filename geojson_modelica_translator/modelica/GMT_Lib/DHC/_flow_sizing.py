"""Shared 5G district flow sizing helpers."""

CP_WATER_KJ_PER_KG_K = 4.18
DEFAULT_HEATING_COP = 2.5
DEFAULT_COOLING_COP = 3.5
DEFAULT_SWH_COP = 2.5
MIN_SOURCE_PUMP_DP_NOMINAL = 35000
SOURCE_PUMP_DP_PER_KG_S = 1200


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
