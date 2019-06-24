# -*- coding: utf-8 -*-

import logging
import os
import shutil
import importlib

_log = logging.getLogger(__name__)

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson


class GeoJsonModelicaTranslator(object):
    """
    Main class for using the GeoJSON to Modelica Translator.
    """

    def __init__(self):
        self.buildings = []

        # directory name member variables. These are set in the scaffold_directory method
        self.loads_dir = None
        self.substations_dir = None
        self.plants_dir = None
        self.districts_dir = None
        self.resources_dir = None
        self.resources_data_root_dir = None
        self.resources_data_loads_dir = None
        self.resources_data_districts_dir = None
        self.resources_data_weather_dir = None

    @classmethod
    def from_geojson(cls, filename):
        """
        Initialize the translator from a GeoJSON file

        :param filename:
        :return:
        """

        if os.path.exists(filename):
            json = UrbanOptGeoJson(filename)

            klass = GeoJsonModelicaTranslator()
            klass.buildings = json.buildings
            return klass
        else:
            raise Exception("Filename does not exist: %s" % filename)

    def scaffold_directory(self, root_dir, overwrite=False):
        """
        Scaffold out the initial directory and set various helper directories

        :param root_dir: string, absolute path where to save results
        :return: bool, did the directory get scaffolded
        """
        if os.path.exists(root_dir):
            if overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % root_dir)
            else:
                shutil.rmtree(root_dir)

        paths = [
            {'member_variable': 'loads_dir', 'path': ['Loads']},
            {'member_variable': 'substations_dir', 'path': ['Substations']},
            {'member_variable': 'plants_dir', 'path': ['Plants']},
            {'member_variable': 'districts_dir', 'path': ['Districts']},
            {'member_variable': 'resources_dir', 'path': ['Resources']},
            {'member_variable': 'resources_data_root_dir', 'path': ['Resources', 'Data']},
            {'member_variable': 'resources_data_loads_dir', 'path': ['Resources', 'Data', 'Loads']},
            {'member_variable': 'resources_data_districts_dir', 'path': ['Resources', 'Data', 'Districts']},
            {'member_variable': 'resources_data_weather_dir', 'path': ['Resources', 'Data', 'Weather']},
        ]

        for p in paths:
            check_path = os.path.abspath(os.path.join(root_dir, str.join(os.path.sep, p['path'])))
            os.makedirs(check_path, exist_ok=True)
            setattr(self, p['member_variable'], check_path)

    def to_modelica(self, root_dir, model_connector_str='TeaserConnector'):
        """
        Convert the data in the GeoJSON to modelica based-objects

        :param root_dir: str, directory where the exported building loads will be stored
        :param model_connector_str: str, which model_connector to use
        :return:
        """
        self.scaffold_directory(root_dir)

        _log.info('Exporting to Modelica')
        for building in self.buildings:
            _log.info("Translating building to model %s" % building)
            # TODO: Handle other connectors -- create map based on model_connector_str
            import geojson_modelica_translator.model_connectors.teaser
            mc_klass = getattr(geojson_modelica_translator.model_connectors.teaser, model_connector_str)
            model_connector = mc_klass(building)
            model_connector.to_modelica(self.loads_dir)


        # TODO: BuildingModelClass
        # TODO: mapper class
        # TODO: lookup tables / data sets
