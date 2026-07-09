# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
from pathlib import Path

from geojson_modelica_translator.external_package_utils import load_loop_order
from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings import Coupling, CouplingGraph
from geojson_modelica_translator.model_connectors.districts import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems import CoolingIndirect, HeatingIndirect
from geojson_modelica_translator.model_connectors.load_connectors import Spawn, Teaser, TimeSeries, TimeSeriesMFT
from geojson_modelica_translator.model_connectors.networks import Network2Pipe
from geojson_modelica_translator.model_connectors.networks.design_data_series import DesignDataSeries
from geojson_modelica_translator.model_connectors.networks.ground_coupling import GroundCoupling
from geojson_modelica_translator.model_connectors.networks.network_distribution_pump import NetworkDistributionPump
from geojson_modelica_translator.model_connectors.networks.unidirectional_series import UnidirectionalSeries
from geojson_modelica_translator.model_connectors.plants import CoolingPlant
from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.model_connectors.plants.chp import HeatingPlantWithOptionalCHP
from geojson_modelica_translator.model_connectors.plants.no_plant_boundary import NoPlantBoundary
from geojson_modelica_translator.model_connectors.plants.waste_heat import WasteHeat
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters

_log = logging.getLogger(__name__)


# map the system parameter "load_model" to Python class
LOAD_MODEL_TO_CLASS = {
    "spawn": Spawn,
    "rc": Teaser,
    "time_series": TimeSeries,
    "time_series_massflow_temperature": TimeSeriesMFT,
}


def _parse_fourth_generation_couplings(geojson: UrbanOptGeoJson, sys_params: SystemParameters) -> list[Coupling]:
    # 4G implementation assumes that all generated district energy system models will have:
    #   - one heating plant
    #   - one cooling plant
    #   - one heating distribution network
    #   - one cooling distribution network
    #   - one heating and cooling ETS per load
    # NOTE: loads can be of any type/combination
    all_couplings = []
    cooling_network = Network2Pipe(sys_params)
    cooling_plant = CoolingPlant(sys_params)
    heating_network = Network2Pipe(sys_params)
    heating_plant = HeatingPlantWithOptionalCHP(sys_params)
    all_couplings += [
        Coupling(cooling_plant, cooling_network),
        Coupling(heating_plant, heating_network),
    ]
    for building in geojson.buildings:
        load_model_type = sys_params.get_param_by_id(building.id, "load_model")
        load_class = LOAD_MODEL_TO_CLASS[load_model_type]
        load = load_class(sys_params, building)

        cooling_indirect = CoolingIndirect(sys_params, building.id)
        all_couplings.append(Coupling(load, cooling_indirect))
        all_couplings.append(Coupling(cooling_indirect, cooling_network))

        heating_indirect = HeatingIndirect(sys_params, building.id)
        all_couplings.append(Coupling(load, heating_indirect))
        all_couplings.append(Coupling(heating_indirect, heating_network))

    return all_couplings


def _find_borefield(sys_params: SystemParameters, ghe_id: str) -> Borefield:
    for ghe in sys_params.get_param("$.district_system.fifth_generation.ghe_parameters.borefields"):
        if ghe_id == ghe["ghe_id"]:
            return Borefield(sys_params, ghe)
    raise KeyError(f"No GHE found in system parameters for ID {ghe_id}")


def _find_waste_heat(sys_params: SystemParameters, source_id: str) -> WasteHeat:
    for heat_source in sys_params.get_param("$.district_system.fifth_generation.heat_source_parameters"):
        if source_id == heat_source["heat_source_id"]:
            return WasteHeat(sys_params, heat_source)
    raise KeyError(f"No waste heat source found in system parameters for ID {source_id}")


def _loop_component_keys(loop: dict) -> tuple[str | None, str | None]:
    keys = list(loop.keys())
    next1_key = keys[1] if len(keys) > 1 else None
    next2_key = keys[2] if len(keys) > 2 else None
    return next1_key, next2_key


def _add_fifth_generation_load_couplings(
    all_couplings: list[Coupling],
    geojson: UrbanOptGeoJson,
    sys_params: SystemParameters,
    loop: dict,
    distribution: UnidirectionalSeries,
    ambient_water_stub: NetworkDistributionPump,
    design_data: DesignDataSeries,
) -> None:
    for bldg_id in loop["list_bldg_ids_in_group"]:
        for geojson_load in geojson.buildings:
            if bldg_id == geojson_load.id:
                time_series_load = TimeSeries(sys_params, geojson_load)
                all_couplings.append(Coupling(time_series_load, distribution, district_type="fifth_generation"))
                all_couplings.append(Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation"))
                all_couplings.append(Coupling(time_series_load, design_data, district_type="fifth_generation"))


def _add_borefield_couplings(
    all_couplings: list[Coupling],
    sys_params: SystemParameters,
    distribution: UnidirectionalSeries,
    ground_coupling: GroundCoupling,
    ghe_id: str,
) -> Borefield:
    borefield = _find_borefield(sys_params, ghe_id)
    all_couplings.append(Coupling(ground_coupling, borefield, district_type="fifth_generation"))
    all_couplings.append(Coupling(distribution, borefield, district_type="fifth_generation"))
    return borefield


def _add_waste_heat_coupling(
    all_couplings: list[Coupling],
    sys_params: SystemParameters,
    distribution: UnidirectionalSeries,
    source_id: str,
) -> WasteHeat:
    waste_heat = _find_waste_heat(sys_params, source_id)
    all_couplings.append(Coupling(distribution, waste_heat, district_type="fifth_generation"))
    return waste_heat


def _add_fifth_generation_plant_couplings(
    all_couplings: list[Coupling],
    sys_params: SystemParameters,
    loop: dict,
    distribution: UnidirectionalSeries,
    ground_coupling: GroundCoupling | None,
) -> bool:
    next1_key, next2_key = _loop_component_keys(loop)

    if next1_key == "list_ghe_ids_in_group" and ground_coupling is not None:
        borefield = _add_borefield_couplings(
            all_couplings, sys_params, distribution, ground_coupling, loop["list_ghe_ids_in_group"][0]
        )
        if next2_key == "list_source_ids_in_group":
            waste_heat = _add_waste_heat_coupling(
                all_couplings, sys_params, distribution, loop["list_source_ids_in_group"][0]
            )
            all_couplings.append(Coupling(borefield, waste_heat, district_type="fifth_generation"))
        return True

    if next1_key == "list_source_ids_in_group":
        waste_heat = _add_waste_heat_coupling(
            all_couplings, sys_params, distribution, loop["list_source_ids_in_group"][0]
        )
        if next2_key == "list_ghe_ids_in_group" and ground_coupling is not None:
            borefield = _add_borefield_couplings(
                all_couplings, sys_params, distribution, ground_coupling, loop["list_ghe_ids_in_group"][0]
            )
            all_couplings.append(Coupling(waste_heat, borefield, district_type="fifth_generation"))
        return True

    return False


def _parse_fifth_generation_couplings(geojson: UrbanOptGeoJson, sys_params: SystemParameters) -> list[Coupling]:
    all_couplings = []
    ambient_water_stub = NetworkDistributionPump(sys_params)
    design_data = DesignDataSeries(sys_params)
    loop_order = load_loop_order(sys_params.filename)
    has_ghe_parameters = bool(sys_params.get_param("$.district_system.fifth_generation.ghe_parameters"))
    ground_coupling = GroundCoupling(sys_params) if has_ghe_parameters else None

    for loop in loop_order:
        distribution = UnidirectionalSeries(sys_params)
        _add_fifth_generation_load_couplings(
            all_couplings, geojson, sys_params, loop, distribution, ambient_water_stub, design_data
        )
        if ground_coupling is not None:
            all_couplings.append(Coupling(distribution, ground_coupling, district_type="fifth_generation"))

        has_real_loop_plant = _add_fifth_generation_plant_couplings(
            all_couplings, sys_params, loop, distribution, ground_coupling
        )
        if not has_real_loop_plant:
            no_plant_boundary = NoPlantBoundary(sys_params)
            all_couplings.append(Coupling(distribution, no_plant_boundary, district_type="fifth_generation"))
    all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="fifth_generation"))

    return all_couplings


def _parse_couplings(
    geojson: UrbanOptGeoJson, sys_params: SystemParameters, sys_param_district_type: str
) -> list[Coupling]:
    """Given config files, construct the necessary models and their couplings which
    can then be passed to CouplingGraph.

    :param geojson: UrbanOptGeoJson
    :param sys_params: SystemParameters
    :param sys_param_district_type: str - type of district ["fourth_generation", "fifth_generation"]
    :return: list[Coupling], list of couplings to be passed to CouplingGraph
    """
    if sys_param_district_type == "fourth_generation":
        return _parse_fourth_generation_couplings(geojson, sys_params)

    if sys_param_district_type == "fifth_generation":
        return _parse_fifth_generation_couplings(geojson, sys_params)

    return []


class ModelicaPackage:
    """Represents a modelica package which can be simulated"""

    def __init__(self, project_path, project_name):
        self._project_path = project_path
        self._project_name = project_name

    def simulate(self):
        """Simulate the package.

        :return: tuple(bool, pathlib.Path), True or False depending on simulation success
            followed by the path to the results directory
        """
        _log.debug(f"Model name: {self._project_name}.Districts.DistrictEnergySystem")
        _log.debug(f"file to load: {self._project_path / self._project_name / 'package.mo'}")
        _log.debug(f"run path: {self._project_path / self._project_name}")

        modelica_runner = ModelicaRunner()
        return modelica_runner.run_in_docker(
            action="compile_and_run",
            model_name=f"{self._project_name}.Districts.DistrictEnergySystem",
            file_to_load=self._project_path / self._project_name / "package.mo",
            run_path=self._project_path / self._project_name,
        )


class GeoJsonModelicaTranslator:
    """Main class for using the GeoJSON to Modelica Translator."""

    def __init__(
        self,
        geojson_filepath,
        sys_params_filepath,
        root_dir,
        project_name,
        **kwargs,
    ):
        """Create an instance of this class

        :param geojson_filepath: str, path to GeoJSON file
        :param sys_params_filepath: str, path to system parameters file
        :param root_dir: str, where to create the package
        :project_name: str, name of the package
        :kwargs: additional keyword arguments
            :skip_validation: bool, optional, skip validation of the GeoJSON file
        """
        if not Path(geojson_filepath).exists():
            raise FileNotFoundError(f"GeoJSON file path does not exist: {geojson_filepath}")
        if not Path(sys_params_filepath).exists():
            raise FileNotFoundError(f"System parameters file path does not exist: {sys_params_filepath}")

        skip_validation = kwargs.get("skip_validation", False)
        self._system_parameters = SystemParameters(sys_params_filepath)

        max_buildings = os.environ.get("GMT_MAX_BUILDINGS")
        if max_buildings:
            max_buildings_count = int(max_buildings)
            self._system_parameters.param_template["buildings"] = self._system_parameters.param_template.get(
                "buildings", []
            )[:max_buildings_count]

        geojson_ids = self._system_parameters.get_param("$.buildings.[*].geojson_id")
        self._geojson = UrbanOptGeoJson(geojson_filepath, geojson_ids, skip_validation=skip_validation)

        # Use different couplings for each district system type
        # The first key of district_system is always the district system type
        sys_param_district_type = next(iter(self._system_parameters.get_param("district_system")))
        self._couplings = _parse_couplings(self._geojson, self._system_parameters, sys_param_district_type)

        self._root_dir = root_dir
        self._project_name = project_name
        self._coupling_graph = CouplingGraph(self._couplings)
        if sys_param_district_type == "fifth_generation":
            self._district = District(
                self._root_dir, self._project_name, self._system_parameters, self._coupling_graph, self._geojson
            )
        else:
            self._district = District(self._root_dir, self._project_name, self._system_parameters, self._coupling_graph)
        self._package_created = False

    def to_modelica(self):
        """Generate the modelica package. Call `simulate` method on the result
        to run the package

        :return: ModelicaPackage
        """
        self._district.to_modelica()

        return ModelicaPackage(self._root_dir, self._project_name)
