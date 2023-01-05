# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
from pathlib import Path

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.couplings import (
    Coupling,
    CouplingGraph
)
from geojson_modelica_translator.model_connectors.districts import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems import (
    CoolingIndirect,
    HeatingIndirect
)
from geojson_modelica_translator.model_connectors.load_connectors import (
    Spawn,
    Teaser,
    TimeSeries,
    TimeSeriesMFT
)
from geojson_modelica_translator.model_connectors.networks import Network2Pipe
from geojson_modelica_translator.model_connectors.plants import CoolingPlant
from geojson_modelica_translator.model_connectors.plants.chp import (
    HeatingPlantWithOptionalCHP
)
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

_log = logging.getLogger(__name__)


# map the system parameter "load_model" to Python class
LOAD_MODEL_TO_CLASS = {
    "spawn": Spawn,
    "rc": Teaser,
    "time_series": TimeSeries,
    "time_series_massflow_temperature": TimeSeriesMFT,
}


def _parse_couplings(geojson, sys_params):
    """Given config files, construct the necessary models and their couplings which
    can then be passed to CouplingGraph.

    :param geojson: UrbanOptGeoJson
    :param sys_params: SystemParameters
    :return: list[Coupling], list of couplings to be passed to CouplingGraph
    """
    # Current implementation assumes that all generated district energy system models will have:
    #   - one heating plant
    #   - one cooling plant
    #   - one heating distribution network
    #   - one cooling distribution network
    #   - one heating and cooling ETS per load
    # NOTE: loads can be of any type/combination
    all_couplings = []

    # create the plants and networks
    cooling_network = Network2Pipe(sys_params)
    cooling_plant = CoolingPlant(sys_params)
    heating_network = Network2Pipe(sys_params)
    heating_plant = HeatingPlantWithOptionalCHP(sys_params)
    all_couplings += [
        Coupling(cooling_plant, cooling_network),
        Coupling(heating_plant, heating_network),
    ]

    # create the loads and their ETSes
    for building in geojson.buildings:
        load_model_type = sys_params.get_param_by_building_id(building.id, "load_model")
        load_class = LOAD_MODEL_TO_CLASS[load_model_type]
        load = load_class(sys_params, building)

        cooling_indirect = CoolingIndirect(sys_params, building.id)
        all_couplings.append(Coupling(load, cooling_indirect))
        all_couplings.append(Coupling(cooling_indirect, cooling_network))

        heating_indirect = HeatingIndirect(sys_params, building.id)
        all_couplings.append(Coupling(load, heating_indirect))
        all_couplings.append(Coupling(heating_indirect, heating_network))

    return all_couplings


class ModelicaPackage(object):
    """Represents a modelica package which can be simulated"""

    def __init__(self, file_to_run, project_path, project_name):
        self._file_to_run = file_to_run
        self._project_path = project_path
        self._project_name = project_name

    def simulate(self):
        """Simulate the package.

        :return: tuple(bool, pathlib.Path), True or False depending on simulation success
            followed by the path to the results directory
        """
        modelica_runner = ModelicaRunner()
        return modelica_runner.run_in_docker(
            self._file_to_run,
            run_path=self._project_path,
            project_name=self._project_name
        )


class GeoJsonModelicaTranslator(object):
    """
    Main class for using the GeoJSON to Modelica Translator.
    """

    def __init__(
        self,
        geojson_filepath,
        sys_params_filepath,
        root_dir,
        project_name,
    ):
        """Create an instance of this class

        :param geojson_filepath: str, path to GeoJSON file
        :param sys_params_filepath: str, path to system parameters file
        :param root_dir: str, where to create the package
        :project_name: str, name of the package
        """
        if not Path(geojson_filepath).exists():
            raise FileNotFoundError(f'GeoJSON file path does not exist: {geojson_filepath}')
        if not Path(sys_params_filepath).exists():
            raise FileNotFoundError(f'System parameters file path does not exist: {sys_params_filepath}')

        self._system_parameters = SystemParameters(sys_params_filepath)

        geojson_ids = self._system_parameters.get_default(
            '$.buildings.[*].geojson_id',
            []
        )
        self._geojson = UrbanOptGeoJson(geojson_filepath, geojson_ids)

        self._root_dir = root_dir
        self._project_name = project_name
        self._couplings = _parse_couplings(self._geojson, self._system_parameters)
        self._coupling_graph = CouplingGraph(self._couplings)
        self._district = District(
            self._root_dir,
            self._project_name,
            self._system_parameters,
            self._coupling_graph
        )
        self._package_created = False

    def to_modelica(self):
        """Generate the modelica package. Call `simulate` method on the result
        to run the package

        :return: ModelicaPackage
        """
        self._district.to_modelica()

        return ModelicaPackage(
            self._district.district_model_filepath,
            self._root_dir,
            self._project_name
        )
