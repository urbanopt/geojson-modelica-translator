# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
import logging
import os
import time
from pathlib import Path

from modelica_builder.model import Model

from geojson_modelica_translator.modelica.package_parser import PackageParser

_log = logging.getLogger(__name__)


class ModelicaFileObject:
    """Class for storing a Modelica file object. Example is a '.mo' file that is
    lazily parsed into the AST using Modelica-Builder or a '.mos' file that reads in the
    header's values using the ModelicaMOS class."""

    # enumerations for different file types
    FILE_TYPE_PACKAGE = 0
    FILE_TYPE_MODEL = 1
    FILE_TYPE_SCRIPT = 2
    FILE_TYPE_TEXT = 3

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.object = None
        self.file_contents = None
        self.file_type = None

        # depending on the file type, parse the object when it is first accessed.
        if self.file_path.is_dir():
            self.file_contents = None
        elif self.file_path.name == 'package.mo':
            # this parses both the .mo and .order files, so we
            # need to skip over the .order file. The PackageParser is
            # a directory, not the file itself.
            self.object = PackageParser(self.file_path.parent)
            self.file_type = self.FILE_TYPE_PACKAGE
        elif self.file_path.name == 'package.order':
            pass
        elif self.file_path.suffix == '.mo':
            self.file_type = self.FILE_TYPE_MODEL
            self._parse_mo_file()
        elif self.file_path.suffix == '.mos':
            self.file_type = self.FILE_TYPE_SCRIPT
            self.file_contents = self.file_path.read_text()
        elif self.file_path.suffix == '.txt':
            self.file_type = self.FILE_TYPE_TEXT
            self.file_contents = self.file_path.read_text()
        else:
            # not sure what to do with this
            _log.warning(f"Unknown file type {self.file_path}")

    def exists(self):
        self.file_path.exists()

    def _parse_mo_file(self):
        """method to parse the mo file into a Modelica AST"""
        # time the loading of the file
        start = time.time()
        self.object = Model(self.file_path)
        end = time.time()

        print(f"Took {end - start} seconds to load {self.file_path.name}")

    @property
    def name(self):
        """method to get the name of the file"""
        return self.file_path.name


class ModelicaProject:
    """Class for storing all the files in a Modelica project. This class should organically
    grow as more requirements are needed.

    The current functionality includes:
    * Load in a package.mo file and store all the related files in memory space."""

    def __init__(self, package_file):
        self.root_directory = Path(package_file).parent
        self.file_types = ['.mo', '.txt', '.mos', '.order']
        self.file_data = {}

        self._load_data()

    def _load_data(self) -> None:
        """method to load all of the files into a data structure for processing"""
        # walk the tree and add in all the files
        for file_path in self.root_directory.rglob('*'):
            if file_path.suffix in self.file_types and file_path.is_file():
                # only store the relative path that is in the package
                rel_path = file_path.relative_to(self.root_directory)
                self.file_data[str(rel_path)] = ModelicaFileObject(file_path)
            elif file_path.is_dir():
                # this is a directory, just add in
                # a temp object for now to keep the path known
                rel_path = file_path.relative_to(self.root_directory)
                self.file_data[str(rel_path)] = ModelicaFileObject(file_path)
            else:
                print(f"Unknown file {file_path}")

        # now sort the file_data by the keys
        self.file_data = {key: self.file_data[key] for key in sorted(self.file_data)}

        # validate the data, extend as needed.
        if self.file_data.get('package.mo', None) is None:
            raise Exception('ModelicaPackage does not contain a /package.mo file')

        self.pretty_print_tree()

    def pretty_print_tree(self) -> None:
        """Pretty print all the items in the directory structure
        """
        # Print a couple lines, just because
        print()
        for key, obj in self.file_data.items():
            # find how many indents we need based on the number of path separators
            indent = key.count(os.path.sep)
            print(" " * indent + f"{os.path.sep} {key.replace(os.path.sep, f' {os.path.sep} ')}")

    def save_as(self, new_package_name: str, output_dir: Path = None) -> None:
        """method to save the ModelicaProject to a new location which
        requires a new path name and updating all of the within statement

        Args:
            new_package_name (str): Name of the new package, which will also be the directory name
            output_dir (Path, optional): Where to persist the new directory and package. Defaults to existing.
        """
        if output_dir is None:
            output_dir = self.root_directory
        output_dir = output_dir / new_package_name

        # in the root package, rename the modelica package (there is not within statement)
        self.file_data['package.mo'].object.rename_package(new_package_name)

        # go through each of the package.mo files first and update the within statements
        for path, file in self.file_data.items():
            if path == 'package.mo':
                # this file is handled above, so just skip
                continue

            if file.file_type == ModelicaFileObject.FILE_TYPE_PACKAGE:
                # this is a package, so update the within statement
                file.object.update_within_statement(new_package_name, element_index=0)

            elif file.file_type == ModelicaFileObject.FILE_TYPE_MODEL:
                new_within_statement = f"{new_package_name}.{str(Path(path).parent).replace(os.path.sep, '.')}"
                file.object.set_within_statement(new_within_statement)

                # there are a few very specific methods that exist when reading in weather files or
                # load files. I am not sure how to abstract out this logic at the moment.

                # IDF names - find the existing value and replace if found
                idf_name = file.object.get_parameter_value('String', 'idfName')
                if idf_name:
                    # replace the previous model name with the new name
                    idf_name = idf_name.replace(self.root_directory.name, new_package_name)
                    file.object.update_parameter('String', 'idfName', idf_name)

                epw_name = file.object.get_parameter_value('String', 'epwName')
                if epw_name:
                    # replace the previous model name with the new name
                    epw_name = epw_name.replace(self.root_directory.name, new_package_name)
                    file.object.update_parameter('String', 'epwName', epw_name)

                weather_filename = file.object.get_parameter_value('String', 'weaName')
                if weather_filename:
                    # replace the previous model name with the new name
                    weather_filename = weather_filename.replace(self.root_directory.name, new_package_name)
                    file.object.update_parameter('String', 'weaName', weather_filename)

                filename = file.object.get_parameter_value('String', 'filNam')
                if filename:
                    # replace the previous model name with the new name
                    filename = filename.replace(self.root_directory.name, new_package_name)
                    file.object.update_parameter('String', 'filNam', filename)

        # now persist all the files to the new location
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        for path, file in self.file_data.items():
            # create the new path
            new_path = output_dir / path
            if file.file_path.is_dir():
                # this is a directory, so just create it
                new_path.mkdir(parents=True, exist_ok=True)

            elif file.file_type == ModelicaFileObject.FILE_TYPE_PACKAGE:
                file.object.save_as(new_path.parent)
            elif file.file_type == ModelicaFileObject.FILE_TYPE_MODEL:
                file.object.save_as(new_path)
            elif file.file_type == ModelicaFileObject.FILE_TYPE_SCRIPT:
                # just save the file as it is text (mos-based file)
                open(new_path, 'w').write(file.file_contents)
            elif file.file_type == ModelicaFileObject.FILE_TYPE_TEXT:
                # just save the file as it is text (all other files)
                open(new_path, 'w').write(file.file_contents)
            else:
                _log.warn("Unknown file type, not saving")