# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4

_log = logging.getLogger(__name__)


def copytree(src, dst, symlinks=False, ignore=None):
    """
    Alternate version of copytree that will work if the directory already exists (use instead of shutil)
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def convert_c_to_k(c):
    """Converts a temperature in celsius to kelvin

    :param c: float, temperature in celsius
    :return: float, temperature in kelvin
    """
    return c + 273.15


def linecount(filename: Path) -> int:
    """Counts the number of lines in a file
    Probably not the most efficient way to do this, but it works
    """
    return len(open(filename).readlines())


class ModelicaPath(object):
    """
    Class for storing Modelica paths. This allows the path to point to
    the model directory, resources, and scripts directory.
    """

    def __init__(self, name, root_dir, overwrite=False):
        """
        Create a new modelica-based path with name of 'name'

        :param name: Name to create
        """
        self.name = name
        self.root_dir = root_dir
        self.overwrite = overwrite

        # create the directories
        if root_dir is not None:
            check_path = os.path.join(self.files_dir)
            self.clear_or_create_path(check_path)
            check_path = os.path.join(self.resources_dir)
            self.clear_or_create_path(check_path)
            check_path = os.path.join(self.scripts_dir)
            self.clear_or_create_path(check_path)

    def clear_or_create_path(self, path):
        if os.path.exists(path):
            if not self.overwrite:
                raise Exception("Directory already exists and overwrite is false for %s" % path)
            else:
                shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    @property
    def files_dir(self):
        """
        Return the path to the files (models) for the specified ModelicaPath. This path does not include the
        trailing slash.

        :return: string, path to where files (models) are stored, without trailing slash
        """
        if self.root_dir is None:
            return self.files_relative_dir
        else:
            return f"{self.root_dir}/{self.name}"

    @property
    def resources_relative_dir(self):
        """
        Return the relative resource directory instead of the full path. This is useful when replacing
        strings within modelica files which are relative to the package.

        :return: string, relative resource's data path
        """
        return f"Resources/Data/{self.name}"

    @property
    def scripts_relative_dir(self, platform='Dymola'):
        """Return the scripts directory that is in the resources directory. This only returns the
        relative directory and is useful when replacing string values within Modelica files.

        :return: string, relative scripts path
        """
        return f"Resources/Scripts/{self.name}/{platform}"

    @property
    def files_relative_dir(self):
        """Return the path to the files relative to the project name."""
        return os.path.join(self.name)

    @property
    def resources_dir(self):
        """
        Return the path to the resources directory for the specified ModelicaPath. This path does not include
        the trailing slash.

        :return: string, path to where resources are stored, without trailing slash.
        """
        if self.root_dir is None:
            return self.resources_relative_dir
        else:
            return f"{self.root_dir}/{self.resources_relative_dir}"

    @property
    def scripts_dir(self):
        """
        Return the path to the scripts directory (in the resources dir) for the specified ModelicaPath.
        This path does not include the trailing slash.

        :return: string, path to where scripts are stored, without trailing slash.
        """
        if self.root_dir is None:
            return self.scripts_relative_dir
        else:
            return f"{self.root_dir}/{self.scripts_relative_dir}"


# This is used for some test cases where we need deterministic IDs to be generated
USE_DETERMINISTIC_ID = bool(os.environ.get('GMT_DETERMINISTIC_ID', False))

counter = 0


def simple_uuid():
    """Generates a simple string uuid

    :return: string, uuid
    """
    global counter

    if not USE_DETERMINISTIC_ID:
        return str(uuid4()).split("-")[0]
    else:
        id = str(counter)
        counter += 1
        return id
