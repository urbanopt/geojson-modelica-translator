# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)


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
    with open(filename) as f:
        filelength = len(f.readlines())
    return filelength


def mbl_version():
    """
    Returns the version of the Modelica Buildings Library (MBL) used by the
    geojson-modelica-translator.
    """
    return "10.0.0"


def _add_water_heating_patch(modelica_dir: Path):
    """Add a dummy value for water heating for MBL 10 limitation."""
    data_dir = Path(modelica_dir) / "Loads" / "Resources" / "Data"
    if data_dir.is_dir():
        for bldg_dir in data_dir.iterdir():
            mo_load_file = data_dir / bldg_dir / "modelica.mos"
            # In case the modelica loads file isn't named modelica.mos:
            if not mo_load_file.is_file():
                modelica_loads = list((data_dir / bldg_dir).rglob("*"))
                if len(modelica_loads) == 1:
                    mo_load_file = modelica_loads[0]
            if mo_load_file.is_file():
                fixed_lines, fl_found = [], False
                with open(mo_load_file) as mlf:
                    for line in mlf:
                        if line == "#Peak water heating load = 0 Watts\n":
                            logger.debug(f"Adding dummy value for water heating to {mo_load_file}")
                            nl = "#Peak water heating load = 1 Watts\n"
                            fixed_lines.append(nl)
                        elif not fl_found and ";" in line:
                            split_vals = line.split(";")
                            split_vals[-1] = "1.0\n"
                            fixed_lines.append(";".join(split_vals))
                            fl_found = True
                        else:
                            fixed_lines.append(line)
                with open(mo_load_file, "w") as mlf:
                    mlf.write("".join(fixed_lines))


class ModelicaPath:
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
                raise Exception(f"Directory already exists and overwrite is false for {path}")
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
    def scripts_relative_dir(self, platform="Dymola"):  # noqa: PLR0206
        # FIXME: https://docs.astral.sh/ruff/rules/property-with-parameters/
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
USE_DETERMINISTIC_ID = bool(os.environ.get("GMT_DETERMINISTIC_ID", False))

counter = 0


def simple_uuid():
    """Generates a simple string uuid

    :return: string, uuid
    """
    global counter  # noqa: PLW0603

    if not USE_DETERMINISTIC_ID:
        return str(uuid4()).split("-")[0]
    else:
        string_id = str(counter)
        counter += 1
        return string_id
