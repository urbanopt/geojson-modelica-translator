# -*- coding: utf-8 -*-
# Helper file to allow for easy setup of test files. This allows for running tests in PyCharm and
# the command line using py.test.

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import geojson_modelica_translator  # noqa  # Do not remove this line.
