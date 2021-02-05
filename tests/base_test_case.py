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

import os
import shutil
from pathlib import Path
from unittest import TestCase

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

    def set_up(self, root_folder, project_name):
        """

        :param root_folder: Folder where the test is to run. This is also the path where the input data are located.
        :param project_name: Name of the project folder to create.
        :return:
        """
        self.data_dir = os.path.join(root_folder, 'data')
        self.output_dir = os.path.join(root_folder, 'output')

        if os.path.exists(os.path.join(self.output_dir, project_name)):
            shutil.rmtree(os.path.join(self.output_dir, project_name))

        return self.data_dir, self.output_dir

    def run_and_assert_in_docker(self, file_to_run, project_path, project_name):
        """
        Run the test in docker.

        :param file_to_run: Full path to the file to run. Typically this is the .mo file of interest (e.g., coupling.mo)
        :param project_path: Full path to the location oft he project to run. This is typically the the full path to
        where the directory named with the `project_name` comes come from.
        :param project_name: The name of the project that is running. This is the directory where the root package.mo
        lives.
        :return: None
        """
        mr = ModelicaRunner()
        run_path = Path(os.path.abspath(project_path)).parent
        exitcode = mr.run_in_docker(file_to_run, run_path=run_path, project_name=project_name)
        # on the exit of the docker command it should return a zero exit code, otherwise there was an issue.
        # Look at the stdout.log if this is non-zero.
        self.assertEqual(0, exitcode)

        # make sure that the results log exist
        results_path = os.path.join(run_path, f"{project_name}_results")
        self.assertTrue(os.path.join(results_path, 'stdout.log'))
