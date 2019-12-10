import os
import shutil
import json

from jinja2 import FileSystemLoader, Environment

from geojson_modelica_translator.model_connectors.base import Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath

class ETS_template():
    def __init__(self, ets_geojsoni, building_modelica):
        self.text = "ets_geojson preserves json data of ETS; 
                    building_modelica holds building-only data in modelica;
                    i need to add ETS to the building_modelica."
        self.ets_geojson = ets_geojson 
        self.building_modelica = building_modelica

    def check_ETS_geojson(self):
        '''check if ETS info are in geojson file'''
        data = json.read(self.ets_geojson)
        pass

    def check_AirTerminal(self):
        '''check if building has terminal or not'''
        '''Currently i just use a aggregated heating/cooling load'''
        pass

    def check_ETS_supply(self):
        '''check the supply port of ETS'''
        pass

    def check_ETS_return(self):
        '''check the return port of ETS'''
        pass

    def check_building(self):
        '''check the supply/return port of building'''
        pass

    def template(self):
        '''convert ETS json to modelica'''
        pass

    def connect(self):
        '''connect ETS-modelica to building-modelica'''
        pass


   



