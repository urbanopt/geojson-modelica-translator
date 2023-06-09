# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

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
        self.package_path = os.path.join(self.project_path, "package.mo")
        if os.path.exists(self.project_path):
            if not self.overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % self.project_path)
            else:
                shutil.rmtree(self.project_path)

    def create(self, ignore_paths=[]):
        """run the scaffolding to create the directory structure for DES systems

        Args:
            ignore_paths (list, optional): List of paths NOT to create. Choose from Loads, Substations, Plants, Districts, Networks. Defaults to [].
        """
        # initialize all of path objects
        self.loads_path = None
        self.substations_path = None
        self.plants_path = None
        self.districts_path = None
        self.networks_path = None

        # leverage the ModelicaPath function
        if 'Loads' not in ignore_paths:
            self.loads_path = ModelicaPath("Loads", root_dir=self.project_path, overwrite=self.overwrite)

        if 'Substations' not in ignore_paths:
            self.substations_path = ModelicaPath("Substations", root_dir=self.project_path, overwrite=self.overwrite)

        if 'Plants' not in ignore_paths:
            self.plants_path = ModelicaPath("Plants", root_dir=self.project_path, overwrite=self.overwrite)

        if 'Districts' not in ignore_paths:
            self.districts_path = ModelicaPath("Districts", root_dir=self.project_path, overwrite=self.overwrite)

        if 'Networks' not in ignore_paths:
            self.networks_path = ModelicaPath("Networks", root_dir=self.project_path, overwrite=self.overwrite)

    def clear_or_create_path(self, path, overwrite=False):
        if os.path.exists(path):
            if not overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % path)
            else:
                shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        return path
