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
import subprocess


class ModelicaRunner(object):
    """
    Class to run Modelica models. This is a very simple implementation of what needs to be
    a full CLI to run Modelica easily. At the moment, this probably only works on Linux/Mac
    and perhaps in Windows with Docker.

    # TODO: test in windows
    # Document how to install Docker
    """

    def __init__(self, modelica_lib_path=None):
        """
        Initialize the runner with data needed for simulation

        :param modelica_lib_path: string, Path to the MBL to run against
        """
        # check if the user has defined a MODELICAPATH, is so, then use that.
        if os.environ.get('MODELICAPATH', None):
            print('Using predefined MODELICAPATH')
            self.modelica_lib_path = os.environ['MODELICAPATH']
        else:
            self.modelica_lib_path = modelica_lib_path
        local_path = os.path.dirname(os.path.abspath(__file__))
        self.jmodelica_py_path = os.path.join(local_path, 'lib', 'runner', 'jmodelica.py')
        self.jm_ipython_path = os.path.join(local_path, 'lib', 'runner', 'jm_ipython.sh')

        # Verify that docker is up and running
        r = subprocess.call(['docker', 'ps'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.docker_configured = r == 0

    def run_in_docker(self, file_to_run, run_path=None):
        """
        Run the Modelica project in a docker-based environment. Results are saved into the path of the
        file that was selected to run.

        stdout.log will store both stdout and stderr of the simulations

        :param file_to_run: string, name of the file (could be directory?) to simulate
        """
        if not self.docker_configured:
            raise Exception('Docker not configured on host computer, unable to run')

        if not os.path.exists(file_to_run):
            raise Exception(f'File not found to run {file_to_run}')

        if not os.path.isfile(file_to_run):
            raise Exception(f'Expecting to run a file, not a folder in {file_to_run}')

        if not run_path:
            run_path = os.path.dirname(file_to_run)

        new_jm_ipython = os.path.join(run_path, os.path.basename(self.jm_ipython_path))
        shutil.copyfile(self.jm_ipython_path, new_jm_ipython)
        os.chmod(new_jm_ipython, 0o775)
        shutil.copyfile(self.jmodelica_py_path, os.path.join(run_path, os.path.basename(self.jmodelica_py_path)))
        curdir = os.getcwd()
        os.chdir(run_path)
        stdout_log = open('stdout.log', 'w')
        try:
            # get the relative difference between the file to run and the path which everything is running in.
            # make sure to simulate at a directory above the project directory!

            # Use slashes for now, but can make these periods `.replace(os.sep, '.')` but must strip off
            # the .mo extension on the model to run
            run_model = os.path.relpath(file_to_run, run_path)
            # TODO: Create a logger to show more information such as the actual run command being executed.
            p = subprocess.Popen(
                ['./jm_ipython.sh', 'jmodelica.py', run_model],
                stdout=stdout_log,
                stderr=subprocess.STDOUT,
                cwd=run_path
            )
            exitcode = p.wait()
        finally:
            os.chdir(curdir)
            stdout_log.close()

        return exitcode

    def cleanup_path(self, path):
        """
        Clean up the files in the path that was presumably used to run the simulation
        """
        remove_files = [
            'jm_ipython.sh',
            'jmodelica.py',
        ]

        for f in remove_files:
            if os.path.exists(os.path.join(path, f)):
                os.remove(os.path.join(path, f))
