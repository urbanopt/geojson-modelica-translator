# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md
from pathlib import Path


class ModelicaFileObject:
    """Class for storing a Modelica file object. Example is a '.mo' file that is
    lazily parsed into the AST using Modelica-Builder or a '.mos' file that reads in the
    header's values using the ModelicaMOS class."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file_contents = None

        # depending on the file type, parse the object when it is first accessed.
        if self.file_path.suffix == '.mo':
            self._parse_mo_file()
        elif self.file_path.suffix == '.mos':
            self._parse_mos_file()
        else:
            # treat the object as a text object
            self.file_contents = self.file_path.read_text()

    def _parse_mo_file(self):
        """method to parse the mo file into a Modelica AST"""

    def _parse_mos_file(self):
        """method to parse the mos file into a ModelicaMOS object"""


class ModelicaProject:
    """Class for storing all the files in a Modelica project. This class should organically
    grow as more requirements are needed.

    The current functionality includes:
    * Load in a package.mo file and store all the related files in memory space"""

    def __init__(self, package_file):
        self.package_file = Path(package_file)
        self.root_directory = Path(package_file).parent
        self.file_types = ['.mo', '.txt', '.mos']
        self.file_data = {}

        self._load_data()

    def _load_data(self):
        """method to load all of the files into a data structure for processing"""
        for file_path in self.root_directory.rglob('*'):
            if file_path.suffix in self.file_types and file_path.is_file():
                # only store the relative path that is in the package
                rel_path = file_path.relative_to(self.root_directory)
                self.file_data[str(rel_path)] = ModelicaFileObject(file_path)

        print(self.file_data)

    # def find_file(self, file_name):
    #     for file_path in self.file_data:
    #         if Path(file_path).name == file_name:
    #             return file_path
    #     return None

    # def get_file_contents(self, file_path):
    #     if file_path in self.file_data:
    #         return self.file_data[file_path]
    #     return None

    # def save_file_contents(self, file_path, new_contents):
    #     if file_path in self.file_data:
    #         with open(file_path, 'w') as f:
    #             f.write(new_contents)
    #             self.file_data[file_path] = new_contents
    #             return True
    #     return False
