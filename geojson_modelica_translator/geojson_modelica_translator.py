# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
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
    # 4G implementation assumes that all generated district energy system models will have:
    #   - one heating plant
    #   - one cooling plant
    #   - one heating distribution network
    #   - one cooling distribution network
    #   - one heating and cooling ETS per load
    # NOTE: loads can be of any type/combination
    all_couplings = []

    if sys_param_district_type == "fourth_generation":
        # create the plants and networks
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

    elif sys_param_district_type == "fifth_generation":
        # create ambient water stub
        ambient_water_stub = NetworkDistributionPump(sys_params)
        # create district data
        design_data = DesignDataSeries(sys_params)
        # import loo order
        loop_order = load_loop_order(sys_params.filename)

        if sys_params.get_param("$.district_system.fifth_generation.ghe_parameters"):
            # create ground coupling
            ground_coupling = GroundCoupling(sys_params)
            for loop in loop_order:
                distribution = UnidirectionalSeries(sys_params)
                for bldg_id in loop["list_bldg_ids_in_group"]:
                    for geojson_load in geojson.buildings:
                        if bldg_id == geojson_load.id:
                            # create the building time series load
                            time_series_load = TimeSeries(sys_params, geojson_load)
                            # couple each time series load to distribution
                            all_couplings.append(
                                Coupling(time_series_load, distribution, district_type="fifth_generation")
                            )
                            all_couplings.append(
                                Coupling(time_series_load, ambient_water_stub, district_type="fifth_generation")
                            )
                            all_couplings.append(
                                Coupling(time_series_load, design_data, district_type="fifth_generation")
                            )
                # couple distribution and ground coupling
                all_couplings.append(Coupling(distribution, ground_coupling, district_type="fifth_generation"))
                # look at the keys following the building group
                keys = list(loop.keys())
                if len(keys) > 1:
                    next1_key = keys[1]
                    if len(keys) > 2:
                        next2_key = keys[2]
                    else:
                        next2_key = None
                else:
                    next1_key = None
                    next2_key = None
                if next1_key == "list_ghe_ids_in_group":
                    ghe_id = loop["list_ghe_ids_in_group"][0]
                    for ghe in sys_params.get_param("$.district_system.fifth_generation.ghe_parameters.borefields"):
                        if ghe_id == ghe["ghe_id"]:
                            borefield = Borefield(sys_params, ghe)
                            break
                    # empty coupling between each borefield and ground
                    all_couplings.append(Coupling(ground_coupling, borefield, district_type="fifth_generation"))
                    # couple each borefield and distribution
                    all_couplings.append(Coupling(distribution, borefield, district_type="fifth_generation"))
                    # look at the following object
                    if next2_key == "list_source_ids_in_group":
                        source_id = loop["list_source_ids_in_group"][0]
                        # create waste heat source and controller
                        for heat_source in sys_params.get_param(
                            "$.district_system.fifth_generation.heat_source_parameters"
                        ):
                            if source_id == heat_source["heat_source_id"]:
                                waste_heat = WasteHeat(sys_params, heat_source)
                                break
                        # couple distribution and waste heat
                        all_couplings.append(Coupling(distribution, waste_heat, district_type="fifth_generation"))
                        # couple borefield and waste heat
                        all_couplings.append(Coupling(borefield, waste_heat, district_type="fifth_generation"))
                elif next1_key == "list_source_ids_in_group":
                    source_id = loop["list_source_ids_in_group"][0]
                    # create waste heat source and controller
                    for heat_source in sys_params.get_param(
                        "$.district_system.fifth_generation.heat_source_parameters"
                    ):
                        if source_id == heat_source["heat_source_id"]:
                            waste_heat = WasteHeat(sys_params, heat_source)
                            break
                    # couple distribution and waste heat
                    all_couplings.append(Coupling(distribution, waste_heat, district_type="fifth_generation"))
                    # look at the following object
                    if next2_key == "list_ghe_ids_in_group":
                        ghe_id = loop["list_ghe_ids_in_group"][0]
                        for ghe in sys_params.get_param("$.district_system.fifth_generation.ghe_parameters.borefields"):
                            if ghe_id == ghe["ghe_id"]:
                                borefield = Borefield(sys_params, ghe)
                                break
                        # empty coupling between each borefield and ground
                        all_couplings.append(Coupling(ground_coupling, borefield, district_type="fifth_generation"))
                        # couple each borefield and distribution
                        all_couplings.append(Coupling(distribution, borefield, district_type="fifth_generation"))
                        # couple waste heat and borefield
                        all_couplings.append(Coupling(waste_heat, borefield, district_type="fifth_generation"))
            all_couplings.append(Coupling(ambient_water_stub, ambient_water_stub, district_type="fifth_generation"))

    return all_couplings


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
