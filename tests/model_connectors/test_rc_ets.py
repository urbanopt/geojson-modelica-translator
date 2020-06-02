import itertools
import os
import shutil
import unittest

from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)
from geojson_modelica_translator.model_connectors.rc_ets_template import (
    RCETSConnector
)
# from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

# from pathlib import Path


class RCETSConnectorSingleBuildingTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')

        project_name = "RCZ6_ETS_Coupling"
        if os.path.exists(os.path.join(self.output_dir, project_name)):
            shutil.rmtree(os.path.join(self.output_dir, project_name))

        # load in the example geojson with a single offie building
        filename = os.path.join(self.data_dir, "RC_building_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        self.gj.scaffold_directory(self.output_dir, project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "RC_system_params_ex1.json")
        sys_params = SystemParameters(filename)

        # now test the spawn connector (independent of the larger geojson translator
        self.RCETS = RCETSConnector(sys_params)
        for b in self.gj.buildings:
            self.RCETS.add_building(b)

    def test_rcETS_init(self):
        self.assertIsNotNone(self.RCETS)
        self.assertEqual(
            self.RCETS.system_parameters.get_param("buildings.custom")[0]["load_model"], "ROM/RC"
        )

    def test_rcETS_to_modelica(self):
        self.RCETS.to_modelica(self.gj.scaffold)

        # setup model names to check
        model_names = [
            "BuildingRCZ6",
            "CoolingIndirect",
            "CouplingRCZ6_ETS",
        ]
        building_paths = [
            os.path.join(self.gj.scaffold.loads_path.files_dir, b.dirname) for b in self.gj.buildings
        ]
        path_checks = [
            f"{os.path.sep.join(r)}.mo"
            for r in itertools.product(building_paths, model_names)
        ]

        for p in path_checks:
            self.assertTrue(os.path.exists(p), f"Path not found: {p}")

        # make sure the model can run using the ModelicaRunner class
        # YL: currently the coupling-of-rc-ets is not running in doccker,
        # because it needs dependency components from modelica-building library.
        # I need to talk to Nick to include the whole modelica-building library to run it.
        # It is running good if i copy out to appropriate folder within MBL in my Dymola(Windows).
        """
        mr = ModelicaRunner()
        file_to_run = os.path.abspath(
            os.path.join(
               self.gj.scaffold.loads_path.files_dir, 'B5a6b99ec37f4de7f94020090', 'CouplingRCZ6_ETS.mo')
        )

        run_path = Path(os.path.abspath(self.gj.scaffold.project_path)).parent
        exitcode = mr.run_in_docker(file_to_run, run_path=run_path,
                                    project_name=self.gj.scaffold.project_name)
        self.assertEqual(0, exitcode)
        results_path = os.path.join(run_path, f"{self.gj.scaffold.project_name}_results")
        self.assertTrue(os.path.join(results_path, 'stdout.log'))
        """
