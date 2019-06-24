# -*- coding: utf-8 -*-

import logging
import os
import shutil

_log = logging.getLogger(__name__)

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson


class ModelicaPath(object):
    """
    Class for storing Modelica paths. This allows the path to point to
    the model directory and the resources directory.
    """

    def __init__(self):
        pass

