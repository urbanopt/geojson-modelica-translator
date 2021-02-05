"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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
import os
from collections import defaultdict

import geojson
from geojson_modelica_translator.geojson.schemas import Schemas

_log = logging.getLogger(__name__)


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
        self.dirname = f"B{self.id}"

        # do some validation
        if self.id is None:
            raise Exception("GeoJSON feature requires an ID property but value was null")

    def __str__(self):
        return f"ID: {self.id}"


class UrbanOptGeoJson(object):
    """
    Root class for parsing an URBANopt GeoJSON file. This class simply reads and parses
    URBANopt GeoJSON files.
    """

    def __init__(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.data = geojson.load(f)
        else:
            raise Exception(f"URBANopt GeoJSON file does not exist: {filename}")

        # load the shemas
        self.schemas = Schemas()

        # break up the file based on the various features
        self.buildings = []
        for f in self.data.features:
            if f["properties"]["type"] == "Building":
                self.buildings.append(UrbanOptLoad(f))
            elif f["properties"]["type"] == "District System":
                print('Found district system, not parsing yet')
                pass

    def validate(self):
        """
        Validate each of the properties object for each of the types

        :return: dict of lists, errors for each of the types
        """
        validations = defaultdict(dict)
        validations["building"] = []
        status = True

        # go through building properties for validation
        for b in self.buildings:
            val_res = self.schemas.validate("building", b.feature.properties)
            if len(val_res) > 0:
                status = False
                res = {"id": b.feature.properties["id"], "errors": val_res}
                validations["building"].append(res)

        return status, validations
