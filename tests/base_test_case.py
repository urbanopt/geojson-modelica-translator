# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import shutil
from pathlib import Path
from unittest import TestCase

import numpy as np
import pytest

from geojson_modelica_translator.modelica.modelica_runner import ModelicaRunner


class GMTTestCase(TestCase):
    def setUp(self):
        # extend as needed to run these methods for all inherited test cases
        pass

    def tearDown(self):
        # extend as needed to run these methods for all inherited test cases
        pass


class TestCaseBase(GMTTestCase):
    """Base Test Case Class to handle generic configurations"""

    SHARED_DATA_DIR = Path(__file__).parent / "data_shared"

    def set_up(self, root_folder, project_name):
        """Base setup for the test case

        :param root_folder: Folder where the test is to run. This is also the path where the input data are located.
        :param project_name: Name of the project folder to create.
        :return:
        """
        data_dir = Path(root_folder) / "data"
        output_dir = Path(root_folder) / "output"

        project_dir = output_dir / project_name
        if project_dir.exists():
            shutil.rmtree(project_dir)

        return data_dir, output_dir

    def compile_and_assert_in_docker(self, file_to_run: str, project_path: Path, project_name: str):
        """Run the compilation test in docker

        :param file_to_run: Full path to the file to run. Typically this is the .mo file of interest (e.g., coupling.mo)
        :param project_path: Full path to the location of the project to run. This is typically the the full path to
        where the directory named with the `project_name` comes come from.
        :param project_name: The name of the project that is running. This is the directory where the root package.mo
        lives.
        :return: None
        """
        mr = ModelicaRunner()
        run_path = Path(project_path).parent.resolve()
        success = mr.run_in_docker("compile", file_to_run, save_path=run_path)
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        assert success is True

        # make sure that the results log exist
        assert (Path(run_path) / "stdout.log").exists()

    def run_and_assert_in_docker(self, model_name: str, file_to_load: str, run_path: Path, **kwargs):
        """Wrapper for running and asserting that the simulation completed successfully

        Args:
            model_name (str): Name of the model to run, this is the name in the Modelica file
            file_to_load (str): Name of the file to load, which may or may not contain the model_name
            run_path (Path): Path to the simulation directory where all the files will be copied
        """
        mr = ModelicaRunner()
        success, results_path = mr.run_in_docker(
            "compile_and_run", model_name, file_to_load=file_to_load, run_path=run_path, **kwargs
        )
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        assert success is True

        # make sure that the results log exist
        assert (Path(results_path) / "stdout.log").exists()

    @pytest.mark.dymola
    def run_and_assert_in_dymola(self, model_name: str, file_to_load: str, run_path: Path, **kwargs):
        """Wrapper for running and asserting that the simulation completed successfully in dymola

        Args:
            model_name (str): Name of the model to run, this is the name in the Modelica file
            file_to_load (str): Name of the file to load, which may or may not contain the model_name
            run_path (Path): Path to the simulation directory where all the files will be copied
        """
        mr = ModelicaRunner()
        success, results_path = mr.run_in_dymola(
            "simulate", model_name, file_to_load=file_to_load, run_path=run_path, **kwargs
        )
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        assert success is True

        # make sure that the results log exist
        assert (Path(results_path) / "stdout.log").exists()

    def cvrmsd(self, measured, simulated):
        """Return CVRMSD between arrays.
        Implementation of ASHRAE Guideline 14 (4-4)

        :param measured: numpy.array
        :param simulated: numpy.array
        :return: float
        """

        def rmsd(a, b):
            p = 1
            n_samples = len(a)
            return np.sqrt(np.sum(np.square(a - b)) / (n_samples - p))

        normalization_factor = np.mean(measured)
        return rmsd(measured, simulated) / normalization_factor
