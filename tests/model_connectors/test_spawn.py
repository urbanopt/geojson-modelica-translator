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

import os
import shutil
import unittest
from pathlib import Path

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.spawn import SpawnConnector
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)


class SpawnModelConnectorSingleBuildingTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')

        project_name = "spawn_single"
        if os.path.exists(os.path.join(self.output_dir, project_name)):
            shutil.rmtree(os.path.join(self.output_dir, project_name))

        # load in the example geojson with a single offie building
        filename = os.path.join(self.data_dir, "spawn_geojson_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        self.gj.scaffold_directory(self.output_dir, project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "spawn_system_params_ex1.json")
        sys_params = SystemParameters(filename)

        # now test the spawn connector (independent of the larger geojson translator
        self.spawn = SpawnConnector(sys_params)

        for b in self.gj.buildings:
            self.spawn.add_building(b)

    def test_spawn_init(self):
        self.assertIsNotNone(self.spawn)
        self.assertEqual(self.spawn.system_parameters.get_param("buildings.custom")[0]["load_model"], "Spawn", )

    def test_spawn_to_modelica(self):
        self.spawn.to_modelica(self.gj.scaffold)

    def test_spawn_to_modelica_and_run(self):
        self.spawn.to_modelica(self.gj.scaffold)

        # make sure the model can run using the ModelicaRunner class
        mr = ModelicaRunner()

        file_to_run = os.path.abspath(
            os.path.join(self.gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090', 'coupling.mo'),
        )
        run_path = Path(os.path.abspath(self.gj.scaffold.project_path)).parent
        exitcode = mr.run_in_docker(file_to_run, run_path=run_path, project_name=self.gj.scaffold.project_name)
        self.assertEqual(0, exitcode)

        results_path = os.path.join(run_path, f"{self.gj.scaffold.project_name}_results")
        self.assertTrue(os.path.join(results_path, 'stdout.log'))
        self.assertTrue(
            os.path.join(results_path, 'spawn_single_Loads_B5a6b99ec37f4de7f94020090_CouplingETS_SpawnBuilding.fmu')
        )


# Do not run this case as it takes too long on travis.
# class SpawnModelConnectorTwoBuildingTest(unittest.TestCase):
#     def setUp(self):
#         self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
#         self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
#         if not os.path.exists(self.output_dir):
#             os.makedirs(self.output_dir)
#
#         project_name = "spawn_two_building"
#         if os.path.exists(os.path.join(self.output_dir, project_name)):
#             shutil.rmtree(os.path.join(self.output_dir, project_name))
#
#         # load in the example geojson with a single offie building
#         filename = os.path.join(self.data_dir, "spawn_geojson_ex2.json")
#         self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
#         # use the GeoJson translator to scaffold out the directory
#         self.gj.scaffold_directory(self.output_dir, project_name)
#
#         # load system parameter data
#         filename = os.path.join(self.data_dir, "spawn_system_params_ex2.json")
#         sys_params = SystemParameters(filename)
#
#         # now test the spawn connector (independent of the larger geojson translator
#         self.spawn = SpawnConnector(sys_params)
#
#         for b in self.gj.buildings:
#             self.spawn.add_building(b)
#
#     def test_spawn_to_modelica_and_run(self):
#         self.spawn.to_modelica(self.gj.scaffold)
#
#         # make sure the model can run using the ModelicaRunner class
#         mr = ModelicaRunner()
#         file_to_run = os.path.abspath(
#             os.path.join(self.gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94021950', 'coupling.mo')
#         )
#         run_path = Path(os.path.abspath(self.gj.scaffold.project_path)).parent
#         exitcode = mr.run_in_docker(file_to_run, run_path=run_path)
#         self.assertEqual(0, exitcode)
#
#         exitcode = mr.run_in_docker(file_to_run, run_path=run_path, project_name=self.gj.scaffold.project_name)
#         self.assertEqual(0, exitcode)
#
#         results_path = os.path.join(run_path, f"{self.gj.scaffold.project_name}_results")
#         self.assertTrue(os.path.join(results_path, 'stdout.log'))
