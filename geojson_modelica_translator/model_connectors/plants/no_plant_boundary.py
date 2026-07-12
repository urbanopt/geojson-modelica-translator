# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from geojson_modelica_translator.model_connectors.plants.plant_base import PlantBase
from geojson_modelica_translator.utils import simple_uuid


class NoPlantBoundary(PlantBase):
    """Explicit marker model for 5G loops that have no GHE or waste-heat source.

    The actual no-plant behavior is rendered by the dedicated coupling templates.
    This model exists so the no-plant case is represented explicitly in the graph
    instead of being inferred ad hoc inside unrelated couplings.
    """

    model_name = "NoPlantBoundary"

    def __init__(self, system_parameters):
        if (
            system_parameters.get_param("$.district_system.fifth_generation.no_central_plant.distribution_temperature")
            is None
        ):
            raise ValueError(
                "5G no-plant systems require "
                "district_system.fifth_generation.no_central_plant.distribution_temperature "
                "in the system parameters JSON."
            )
        super().__init__(system_parameters)
        self.id = "noPla_" + simple_uuid()

    def to_modelica(self, scaffold):
        """No standalone Modelica files are needed for the marker model."""

    def get_modelica_type(self, scaffold):
        return "Plants.NoPlantBoundary"
