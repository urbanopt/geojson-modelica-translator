# -*- coding: utf-8 -*-

import logging
import os
from collections import defaultdict
import geojson
from jsonschema import validate as validate_json
from geojson_modelica_translator.geojson.schemas import Schemas

_log = logging.getLogger(__name__)


# TODO: Inherit from GeoJSON Feature class, move to its own file
class UrbanOptBuilding(object):
    def __init__(self, feature):
        self.feature = feature


class UrbanOptGeoJson(object):
    """
    Root class for parsing an URBANopt GeoJSON file. This class simply reads and parses
    URBANopt GeoJSON files.
    """

    def __init__(self, filename):
        if os.path.exists(filename):
            self.data = geojson.load(open(filename))
        else:
            raise Exception("URBANopt GeoJSON file not found: %s" % filename)

        # load the shemas
        self.schemas = Schemas()

        # break up the file based on the various features
        self.buildings = []
        for f in self.data.features:
            if f['properties']['type'] == 'Building':
                self.buildings.append(UrbanOptBuilding(f))

    def validate(self):
        """
        Validate each of the properties object for each of the types

        :return: dict of lists, errors for each of the types
        """
        validations = defaultdict(dict)
        validations['building'] = []
        status = True

        # go through building properties for validation
        for b in self.buildings:
            val_res = self.schemas.validate('building', b.feature.properties)
            if len(val_res) > 0:
                status = False
                res = {
                    "id": b.feature.properties['id'],
                    "errors": val_res,
                }
                validations['building'].append(res)

        return status, validations
