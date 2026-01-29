# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import os
import shutil
import stat
from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.utils import ModelicaPath, mbl_version

_log = logging.getLogger(__name__)


class Scaffold:
    """Scaffold to hold the entire directory structure for the project. The purpose of this class is to
    allow a developer/user to easily access the various paths of the project without having to
    manually strip/replace strings/filenames/paths/etc.

    The project structure where an URBANopt-Modelica analysis will occur follows a well
    defined structure and includes multiple levels of nested directories, data files, and scripts.

    Presently, the scaffold stops at the loads, substation, plant, districts, scripts path and does not
    create a list of all of the submodels (yet).

    The scaffold now uses PackageParser for more flexible subpackage management.
    """

    def __init__(self, root_dir: Path, project_name: str, overwrite: bool = False, mbl_version_str: str | None = None):
        """Initialize the scaffold. This will clear out the directory if it already exists, so use this
        with caution.

        :param root_dir: Path, Directory where to create the scaffold
        :param project_name: str, Name of the project to create (should contain no spaces)
        :param overwrite: boolean, overwrite the project if it already exists?
        :param mbl_version_str: str, optional, the Modelica Buildings Library version to use. If None, auto-detects.
        """
        self.root_dir = Path(root_dir)
        self.project_name = project_name
        self.overwrite = overwrite
        self._mbl_version = mbl_version_str or mbl_version()
        self._package: PackageParser | None = None

        # Dynamically created paths (set by create() method). These are
        # used for mypy checks.
        self.districts_path: ModelicaPath | None = None
        self.loads_path: ModelicaPath | None = None
        self.plants_path: ModelicaPath | None = None
        self.substations_path: ModelicaPath | None = None
        self.networks_path: ModelicaPath | None = None
        self.schedules_path: ModelicaPath | None = None
        self.heat_pump_ets_path: ModelicaPath | None = None

        # clear out the project path
        self.project_path = self.root_dir / self.project_name
        self.package_path = self.project_path / "package.mo"
        if self.project_path.exists():
            if not self.overwrite:
                raise Exception(f"Directory already exists and overwrite is false for {self.project_path}")
            else:
                # Use onerror handler to force deletion of read-only files
                def handle_remove_readonly(func, path, _exc):
                    """Error handler for Windows readonly files"""
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)
                    else:
                        raise _exc[1]

                shutil.rmtree(self.project_path, onerror=handle_remove_readonly)

    @property
    def package(self) -> PackageParser:
        """Get or create the root PackageParser for this scaffold."""
        if self._package is None:
            raise RuntimeError(
                "Scaffold not yet created. Call the create() method before accessing the package property."
            )
        return self._package

    def create(self, ignore_paths: list[str] = [], subpackages: list[str] = []) -> None:
        """Run the scaffolding to create the directory structure for DES systems.

        Now uses PackageParser for dynamic subpackage creation. You can either use ignore_paths
        to exclude default packages, or use subpackages to explicitly list what to create.

        Args:
            ignore_paths (list, optional): List of paths NOT to create.
                Choose from Loads, Substations, Plants, Districts, Networks, Heat_Pump_ETSes, Schedules. Defaults to [].
            subpackages (list, optional): If provided, only create these subpackages
                (overrides ignore_paths). Defaults to [].
        """
        # Create the root package
        self._package = PackageParser.new_from_template(
            self.project_path, self.project_name, order=[], mbl_version=self._mbl_version
        )

        # Determine which subpackages to create
        default_packages = ["Schedules", "Loads", "Loads/ETS", "Substations", "Plants", "Districts", "Networks"]

        if subpackages:
            # If explicit list provided, use only those
            packages_to_create = subpackages
        else:
            # Otherwise use defaults minus ignored ones
            packages_to_create = [p for p in default_packages if p not in ignore_paths]

        # If a nested package's parent is ignored, also ignore the nested package
        filtered_packages = []
        for pkg in packages_to_create:
            if "/" in pkg:
                parent_name = pkg.split("/", 1)[0]
                if parent_name not in packages_to_create:
                    continue  # Skip nested package if parent isn't being created
            filtered_packages.append(pkg)
        packages_to_create = filtered_packages

        # Create each subpackage using PackageParser's dynamic creation
        for package_name in packages_to_create:
            # Handle nested packages like "Loads/ETS"
            if "/" in package_name:
                parent_name, subpkg_name = package_name.split("/", 1)
                parent_pkg = getattr(self._package, parent_name.lower())
                parent_pkg.add_model(subpkg_name, create_subpackage=True)

                # Create ModelicaPath for nested package
                setattr(
                    self,
                    "heat_pump_ets_path",
                    ModelicaPath(subpkg_name, root_dir=self.project_path / parent_name, overwrite=True),
                )
            else:
                self._package.add_model(package_name, create_subpackage=True)

                # Create ModelicaPath for backward compatibility
                # Set overwrite=True since PackageParser already created the directory
                getattr(self._package, package_name.lower())
                setattr(
                    self,
                    f"{package_name.lower()}_path",
                    ModelicaPath(package_name, root_dir=self.project_path, overwrite=True),
                )

    def add_subpackage(self, name: str, parent: str | None = None) -> PackageParser:
        """Add a new subpackage dynamically to the scaffold.

        Args:
            name (str): Name of the subpackage to create
            parent (str, optional): Name of parent package. If None, creates at root level.

        Returns:
            PackageParser: The newly created subpackage

        Example:
            scaffold.add_subpackage('CustomModels')
            scaffold.add_subpackage('MyModel', parent='Districts')
        """
        if self._package is None:
            raise RuntimeError("Scaffold not yet created. Call create() first.")

        if parent:
            parent_pkg = getattr(self._package, parent.lower())
            subpackage = parent_pkg.add_model(name, create_subpackage=True)
        else:
            subpackage = self._package.add_model(name, create_subpackage=True)

        # Create ModelicaPath for the new subpackage
        # Set overwrite=True since PackageParser already created the directory
        parent_path = self.project_path / parent if parent else self.project_path
        setattr(self, f"{name.lower()}_path", ModelicaPath(name, root_dir=parent_path, overwrite=True))

        return subpackage

    def save(self) -> None:
        """Save all package files to disk."""
        if self._package:
            self._package.save()

    def clear_or_create_path(self, path, overwrite=False):
        if Path(path).exists():
            if not overwrite:
                raise Exception(f"Directory already exists and overwrite is false for {path}")
            else:
                shutil.rmtree(path)
        Path(path).mkdir(exist_ok=True, parents=True)

        return path
