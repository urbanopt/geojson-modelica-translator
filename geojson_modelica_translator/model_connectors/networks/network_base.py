# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class NetworkBase(ModelBase):
    """
    Base class of the network connectors.
    """
    simple_gmt_type = 'network'

    def __init__(self, system_parameters):
        super().__init__(system_parameters, Path(__file__).parent / 'templates')
