# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class EnergyTransferBase(ModelBase):
    """
    Base class of the energy transfer connectors.
    """
    simple_gmt_type = 'ets'

    def __init__(self, system_parameters, geojson_load_id):
        super().__init__(system_parameters, Path(__file__).parent / 'templates')

        # geojson load id is used for fetching load-specific ETS configs from sys params
        self._geojson_load_id = geojson_load_id
