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

import itertools
import os
from pathlib import Path

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.teaser import TeaserConnector
from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class TeaserModelConnectorSingleBuildingTest(TestCaseBase):
    def load_project(self, project_name, geojson_filename, sys_param_filename):
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, geojson_filename)
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        self.gj.scaffold_directory(self.output_dir, project_name)

        if sys_param_filename is not None:
            filename = os.path.join(self.data_dir, sys_param_filename)
            sys_params = SystemParameters(filename)
        else:
            sys_params = SystemParameters()

        self.teaser = TeaserConnector(sys_params)
        for b in self.gj.json_loads:
            self.teaser.add_building(b)

    def test_building_types(self):
        sys_params = SystemParameters()
        tc = TeaserConnector(sys_params)
        self.assertEqual('institute8', tc.lookup_building_type('Laboratory'))
        self.assertEqual('institute', tc.lookup_building_type('Education'))
        self.assertEqual('office', tc.lookup_building_type('Office'))

    def test_undefined_building_type(self):
        sys_params = SystemParameters()
        tc = TeaserConnector(sys_params)

        with self.assertRaises(Exception) as exc:
            tc.lookup_building_type('Undefined Building Type')
        self.assertEqual("Building type of Undefined Building Type not defined in GeoJSON to TEASER mappings",
                         str(exc.exception))

    def test_teaser_rc_default(self):
        """Should result in TEASER models with two element RC models"""
        project_name = 'teaser_rc_default'
        self.load_project(project_name, "teaser_geojson_ex1.json", None)
        self.teaser.to_modelica(self.gj.scaffold)

        # Check that the created file is two element
        check_file = os.path.join(self.gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090', 'Office.mo')
        self.assertTrue(os.path.exists(check_file))

        with open(check_file) as f:
            self.assertTrue('Buildings.ThermalZones.ReducedOrder.RC.TwoElements' in f.read())

        mr = ModelicaRunner()

        file_to_run = os.path.abspath(
            os.path.join(self.gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090', 'coupling.mo'),
        )
        run_path = Path(os.path.abspath(self.gj.scaffold.project_path)).parent
        exitcode = mr.run_in_docker(file_to_run, run_path=run_path, project_name=self.gj.scaffold.project_name)
        self.assertEqual(0, exitcode)

    def test_teaser_rc_4(self):
        """Models should be 4 element RC models"""
        project_name = 'teaser_rc_4'

        self.load_project(project_name, "teaser_geojson_ex1.json", "teaser_system_params_ex1.json")
        self.teaser.to_modelica(self.gj.scaffold)

        # setup what wze are going to check
        model_names = ["Floor", "ICT", "Meeting", "Office", "package", "Restroom", "Storage", ]
        building_paths = [
            os.path.join(self.gj.scaffold.loads_path.files_dir, b.dirname) for b in self.gj.json_loads
        ]
        path_checks = [f"{os.path.sep.join(r)}.mo" for r in itertools.product(building_paths, model_names)]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found {p}")
            if os.path.basename(p) == 'package.mo':
                continue

            with open(p) as f:
                self.assertTrue('Buildings.ThermalZones.ReducedOrder.RC.FourElements' in f.read(),
                                "Could not find the correct RC Model Order")

        # go through the generated buildings and ensure that the resources are created
        resource_names = ["InternalGains_Floor", "InternalGains_ICT", "InternalGains_Meeting",
                          "InternalGains_Office", "InternalGains_Restroom", "InternalGains_Storage", ]
        for b in self.gj.json_loads:
            for resource_name in resource_names:
                # TEASER 0.7.2 used .txt for schedule files
                path = os.path.join(self.gj.scaffold.loads_path.files_dir, "Resources", "Data",
                                    b.dirname, f"{resource_name}.txt")
                self.assertTrue(os.path.exists(path), f"Path not found: {path}")
