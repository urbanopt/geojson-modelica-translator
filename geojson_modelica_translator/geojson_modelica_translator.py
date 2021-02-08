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

from geojson_modelica_translator.geojson.urbanopt_geojson import (
    UrbanOptGeoJson
)
from geojson_modelica_translator.model_connectors.load_connectors import (
    Spawn,
    Teaser,
    TimeSeries
)
from geojson_modelica_translator.scaffold import Scaffold

_log = logging.getLogger(__name__)


load_mapper = {
    "spawn": Spawn,
    "rc": Teaser,
    "time_series": TimeSeries
}


class LoadsList(list):
    pass


class GeoJsonModelicaTranslator(object):
    """
    Main class for using the GeoJSON to Modelica Translator.
    """

    def __init__(self):
        # self.json = None
        # These objects should be removed eventually and used as helpers to
        # translate the geojson to iterators for processing in this class.
        self.json_loads = []

        # directory name member variables. These are set in the scaffold_directory method
        self.scaffold = None
        self.system_parameters = None

        self.loads = LoadsList()
        # self.district_systems = DistrictSystemsList()

    @classmethod
    def from_geojson(cls, filename):
        """
        Initialize the translator from a GeoJSON file

        :param filename: string, GeoJSON file
        :return: object, GeoJsonModelicaTranslator
        """

        if os.path.exists(filename):
            klass = GeoJsonModelicaTranslator()
            json = UrbanOptGeoJson(filename)
            klass.json_loads = json.buildings

            # load in the building loads
            return klass
        else:
            raise Exception(f"GeoJSON file does not exist: {filename}")

    def process_loads(self):
        """
        Process the loads of the GeoJSON file. This combines the GeoJSON object
        with the sys_params object. Each building object contains all the data
        it needs to generate the resulting model.

        :return: None
        """
        if self.system_parameters is None:
            raise Exception("Must set the system parameter file first. Use gj.set_system_parameters")

        for load in self.json_loads:
            # Read in the load and determine if the model is RC, CSV, or Spawn
            _log.debug(load)
            model_con = self.system_parameters.get_param_by_building_id(load.id, "load_model")
            try:
                # Also handle the load as if it is connected to the ETS or not
                class_ = load_mapper[model_con]
            except KeyError:
                raise SystemExit(f'Model of type {model_con} not recognized. Verify sysparam file')

            _log.info(f"Adding building to load model: {class_.__class__}")
            model_connector = class_(self.system_parameters, load)
            self.loads.append(model_connector)

    def set_system_parameters(self, sys_params):
        """
        Read in the system design parameter data

        :param SystemParameters: SystemParameters object
        """
        self.system_parameters = sys_params

    def scaffold_directory(self, root_dir, project_name, overwrite=False):
        """
        Scaffold out the initial directory and set various helper directories

        :param root_dir: string, absolute path where the project will be scaffolded.
        :param project_name: string, name of the project that is being created
        :return: string, path to the scaffold directory
        """
        self.scaffold = Scaffold(root_dir, project_name)
        self.scaffold.create()
        return self.scaffold.project_path

    def to_modelica(self, project_name, save_dir):
        """
        Convert the data in the GeoJSON to modelica based-objects

        :param save_dir: str, directory where the exported project will be stored. The name of the project will be
                              {save_dir}/{project_name}
        :param model_connector_str: str, which model_connector to use
        """
        self.scaffold_directory(save_dir, project_name)

        # Only call to_modelica once all the buildings have been added
        for load in self.loads:
            load.to_modelica(self.scaffold)  # , keep_original_models=False)

        # import geojson_modelica_translator.model_connectors.load_connectors.ets_template as ets_template
        # ets_class = getattr(ets_template, "ETSConnector")
        # ets_connector = ets_class(self.system_parameters)

        # _log.info("Exporting District System")

        # model_connector.to_modelica(self.scaffold, keep_original_models=False)

        # for building in self.buildings:
        #    ets_connector.to_modelica(self.scaffold, building)

        # add in Districts
        # add in Plants

        # now add in the top level package.
        # Need to decide how to create the top level packages when running this as part of the model_connectors.
        # pp = PackageParser.new_from_template(self.scaffold.project_path, project_name, ["Loads"])
        # pp.save()

        # TODO: BuildingModelClass
        # TODO: mapper class
        # TODO: lookup tables / data sets
