"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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
import shutil

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath

_log = logging.getLogger(__name__)


class GeoJsonModelicaTranslator(object):
    """
    Main class for using the GeoJSON to Modelica Translator.
    """

    def __init__(self):
        self.buildings = []

        # directory name member variables. These are set in the scaffold_directory method
        self.loads_path = None
        self.substations_path = None
        self.plants_path = None
        self.districts_path = None

        self.system_parameters = None

    @classmethod
    def from_geojson(cls, filename):
        """
        Initialize the translator from a GeoJSON file

        :param filename: string, GeoJSON file
        :return: object, GeoJsonModelicaTranslator
        """

        if os.path.exists(filename):
            json = UrbanOptGeoJson(filename)

            klass = GeoJsonModelicaTranslator()
            klass.buildings = json.buildings
            return klass
        else:
            raise Exception(f'GeoJSON file does not exist: {filename}')

    def set_system_parameters(self, sys_params):
        """
        Read in the system design parameter data

        :param SystemParameters: SystemParameters object
        """
        self.system_parameters = sys_params

    def scaffold_directory(self, root_dir, overwrite=False):
        """
        Scaffold out the initial directory and set various helper directories

        :param root_dir: string, absolute path where to save results
        :return: bool, did the directory get scaffolded
        """
        # TODO: need to be careful with this. If we are mixing load models, then we need to not remove the entire path
        if os.path.exists(root_dir):
            if overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % root_dir)
            else:
                shutil.rmtree(root_dir)

        self.loads_path = ModelicaPath('Loads', root_dir=root_dir)
        self.substations_path = ModelicaPath('Substations', root_dir=root_dir)
        self.plants_path = ModelicaPath('Plants', root_dir=root_dir)
        self.districts_path = ModelicaPath('Districts', root_dir=root_dir)

    def to_modelica(self, project_name, save_dir, model_connector_str='TeaserConnector'):
        """
        Convert the data in the GeoJSON to modelica based-objects

        :param save_dir: str, directory where the exported project will be stored. The name of the project will be
                              {save_dir}/{project_name}
        :param model_connector_str: str, which model_connector to use
        """
        prj_dir = f'{save_dir}/{project_name}'
        self.scaffold_directory(prj_dir)

        # TODO: Handle other connectors -- create map based on model_connector_str
        import geojson_modelica_translator.model_connectors.teaser
        import geojson_modelica_translator.model_connectors.spawn
        mc_klass = getattr(geojson_modelica_translator.model_connectors.teaser, model_connector_str)
        model_connector = mc_klass(self.system_parameters)

        _log.info('Exporting to Modelica')
        for building in self.buildings:
            _log.info(f'Adding building to model connector: {mc_klass.__class__}')

            model_connector.add_building(building)

        _log.info(f'Translating building to model {building}')
        model_connector.to_modelica(project_name, self.loads_path.files_dir, keep_original_models=False)

        # add in Substations
        # add in Districts
        # add in Plants

        # now add in the top level package.
        pp = PackageParser.new_from_template(prj_dir, project_name, ['Loads'])
        pp.save()

        # TODO: BuildingModelClass
        # TODO: mapper class
        # TODO: lookup tables / data sets
