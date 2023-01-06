# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from geojson_modelica_translator.model_connectors.networks.network_base import (
    NetworkBase
)
from geojson_modelica_translator.utils import simple_uuid


class Network2Pipe(NetworkBase):
    model_name = 'Network2Pipe'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'disNet_' + simple_uuid()

    def to_modelica(self, scaffold):
        """
        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        # no model to generate, its fully implemented in the Modelica Buildings library

    def get_modelica_type(self, scaffold):
        return 'Buildings.Experimental.DHC.Networks.Distribution2Pipe'
