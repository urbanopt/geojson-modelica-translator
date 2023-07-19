# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from geojson_modelica_translator.model_connectors.networks.network_base import (
    NetworkBase
)


class NetworkDistributionPump(NetworkBase):
    model_name = 'NetworkDistributionPump'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'MyNetworkDistributionPump'

    def to_modelica(self, scaffold):
        """
        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        # this stub has no model to generate, its fully implemented in the coupling currently

    def get_modelica_type(self, scaffold):
        # this stub has no model, so there's no type
        return 'UNIMPLEMENTED'
