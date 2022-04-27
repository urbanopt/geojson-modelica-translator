"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import logging
from pathlib import Path

import geojson
from geojson_modelica_translator.geojson.schemas import Schemas

_log = logging.getLogger(__name__)


class GeoJsonValidationError(Exception):
    pass


# TODO: Inherit from GeoJSON Feature class, move to its own file
class UrbanOptLoad(object):
    """
    An UrbanOptLoad is a container for holding Building-related data in a dictionary. This object
    does not do much work on the GeoJSON definition of the data at the moment, rather it creates
    an isolation layer between the GeoJSON data and the GMT.
    """

    def __init__(self, feature):
        self.feature = feature
        self.id = feature.get("properties", {}).get("id", None)

        # do some validation
        if self.id is None:
            raise GeoJsonValidationError("GeoJSON feature requires an ID property but value was null")

    def __str__(self):
        return f"ID: {self.id}"


class UrbanOptGeoJson(object):
    """
    Root class for parsing an URBANopt GeoJSON file. This class simply reads and parses
    URBANopt GeoJSON files.
    """

    def __init__(self, filename, building_ids=None):
        """
        :param filename: str, path to the GeoJSON file to parse
        :param building_ids: list[str | int] | None, optional, list of GeoJSON building
            IDs to parse from the file. If None or an empty list, parse all buildings.
        """
        if not Path(filename).exists():
            raise GeoJsonValidationError(f"URBANopt GeoJSON file does not exist: {filename}")

        with open(filename, "r") as f:
            self.data = geojson.load(f)

        self.schemas = Schemas()

        building_errors = {}
        self.buildings = []
        for feature in self.data.features:
            if feature["properties"]["type"] == "Building":
                building = UrbanOptLoad(feature)
                if not building_ids or building.id in building_ids:
                    errors = self.schemas.validate("building", building.feature.properties)
                    if errors:
                        building_errors[building.id] = errors
                    else:
                        self.buildings.append(building)

        if building_errors:
            formatted_errors = ''
            for building_id, errors in building_errors.items():
                building_errors_bullets = ''.join([f'\n    * {error}' for error in errors])
                formatted_errors += f'\n  ID {building_id}:{building_errors_bullets}'

            message = f'GeoJSON file is not valid:{formatted_errors}'
            raise GeoJsonValidationError(message)

        if not self.buildings:
            raise GeoJsonValidationError(f'No valid buildings found in GeoJSON file: {filename}')
