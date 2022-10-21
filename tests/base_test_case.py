"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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

import shutil
from pathlib import Path
from unittest import TestCase

import numpy as np

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

    SHARED_DATA_DIR = Path(__file__).parent / 'data_shared'

    def set_up(self, root_folder, project_name):
        """

        :param root_folder: Folder where the test is to run. This is also the path where the input data are located.
        :param project_name: Name of the project folder to create.
        :return:
        """
        data_dir = Path(root_folder) / 'data'
        output_dir = Path(root_folder) / 'output'

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
        success, results_path = mr.compile_in_docker(file_to_run, save_path=run_path)
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        self.assertTrue(success)

        # make sure that the results log exist
        self.assertTrue((Path(results_path) / 'stdout.log').exists())

    def run_and_assert_in_docker(self, file_to_run: str, project_path: Path, project_name: str):
        """Run the test in docker.

        :param file_to_run: Full path to the file to run. Typically this is the .mo file of interest (e.g., coupling.mo)
        :param project_path: Full path to the location of the project to run. This is typically the the full path to
        where the directory named with the `project_name` comes come from.
        :param project_name: The name of the project that is running. This is the directory where the root package.mo
        lives.
        :return: None
        """
        mr = ModelicaRunner()
        run_path = Path(project_path).parent.resolve()
        success, results_path = mr.run_in_docker(file_to_run, run_path=run_path, project_name=project_name)
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        self.assertTrue(success)

        # make sure that the results log exist
        self.assertTrue((Path(results_path) / 'stdout.log').exists())

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
            return np.sqrt(
                np.sum(
                    np.square(
                        a - b
                    )
                ) / (n_samples - p)
            )

        normalization_factor = np.mean(measured)
        return rmsd(measured, simulated) / normalization_factor
