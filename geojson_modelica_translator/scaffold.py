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

import logging
import os
import shutil

from geojson_modelica_translator.utils import ModelicaPath

_log = logging.getLogger(__name__)


class Scaffold(object):
    """Scaffold to hold the entire directory structure for the project. The purpose of this class is to
    allow a developer/user to easily access the various paths of the project without having to
    manually strip/replace strings/filenames/paths/etc.

    The project structure where an URBANopt-Modelica analysis will occur follows a well
    defined structure and includes multiple levels of nested directories, data files, and scripts.

    Presently, the scaffold stops at the loads, substation, plant, districts, scripts path and does not
    create a list of all of the submodels (yet).
    """

    def __init__(self, root_dir, project_name, overwrite=False):
        """Initialize the scaffold. This will clear out the directory if it already exists, so use this
        with caution.

        :param root_dir: Directory where to create the scaffold
        :param project_name: Name of the project to create (should contain no spaces)
        :param overwrite: boolean, overwrite the project if it already exists?
        """
        self.root_dir = root_dir
        self.project_name = project_name
        self.loads_path = None
        self.substations_path = None
        self.plants_path = None
        self.districts_path = None
        self.scripts_path = None
        self.networks_path = None
        self.overwrite = overwrite

        # clear out the project path
        self.project_path = os.path.join(self.root_dir, self.project_name)
        if os.path.exists(self.project_path):
            if not self.overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % self.project_path)
            else:
                shutil.rmtree(self.project_path)

    def create(self):
        """run the scaffolding"""

        # leverage the ModelicaPath function
        self.loads_path = ModelicaPath("Loads", root_dir=self.project_path, overwrite=self.overwrite)
        self.substations_path = ModelicaPath("Substations", root_dir=self.project_path, overwrite=self.overwrite)
        self.plants_path = ModelicaPath("Plants", root_dir=self.project_path, overwrite=self.overwrite)
        self.districts_path = ModelicaPath("Districts", root_dir=self.project_path, overwrite=self.overwrite)
        self.networks_path = ModelicaPath("Networks", root_dir=self.project_path, overwrite=self.overwrite)

    def clear_or_create_path(self, path, overwrite=False):
        if os.path.exists(path):
            if not overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % path)
            else:
                shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        return path
