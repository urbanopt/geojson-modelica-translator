# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.utils import simple_uuid


class EtsColdWaterStub(EnergyTransferBase):
    model_name = 'EtsColdWaterStub'

    def __init__(self, system_parameters):
        super().__init__(system_parameters, None)
        self.id = 'etsColWatStub_' + simple_uuid()

    def to_modelica(self, scaffold):
        """
        Create cooling water stub models

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        # this stub does not have any modelica files to generate as it's not its own model
        # It's contained within the coupling files

    def get_modelica_type(self, scaffold):
        # this stub does not have a type as it's not packaged into its own model currently
        return 'UNIMPLEMENTED'
