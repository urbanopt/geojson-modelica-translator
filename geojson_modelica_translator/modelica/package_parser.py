# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
from pathlib import Path
from typing import Any, Union

from jinja2 import Environment, FileSystemLoader

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS


class PackageParser(object):
    """Class to read and modify the package.mo and the package.order file
    """

    def __init__(self, path: Union[str, Path] = None):
        """Create an instance to manage the package.mo/order file. If no path is provided then the user
        must add in their own package and order data. Or the user can load from the new_from_template
        class method.

        Args:
            path (Union[str, Path], optional): path to where the package.mo and package.order reside.
                                               Defaults to None.
        """
        self.path: Union[str, Path, None] = path
        self.order_data: Any = None
        self.package_data: Any = None
        self.load()

        self.template_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "templates"
                )
            )
        )
        self.template_env.filters.update(ALL_CUSTOM_FILTERS)

    @classmethod
    def new_from_template(cls, path: Union[str, Path], name: str, order: list[str], within: Union[str, None] = None) -> "PackageParser":
        """Create new package data based on the package.mo template. If within is not specified, then it is
        assumed that this is a top level package and will load from the package_base template.

        Args:
            path (str): the path where the resulting package file and order will be saved to.
            name (str): the name of the model
            order (list[str]): ordered list of which models will be loaded (saved to package.order)
            within (str, optional): name where this package is within.. Defaults to None.

        Returns:
            PackageParser: object of the package parser
        """
        klass = PackageParser(path)
        if within:
            template = klass.template_env.get_template("package.mot")
        else:
            template = klass.template_env.get_template("package_base.mot")

        klass.package_data = template.render(within=within, name=name, order=order)
        klass.order_data = "\n".join(order)
        return klass

    def load(self) -> None:
        """Load the package.mo and package.mo data from the member variable path
        """
        filename = os.path.join(str(self.path), "package.mo")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.package_data = f.read()

        filename = os.path.join(str(self.path), "package.order")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.order_data = f.read()

    def save(self) -> None:
        """Save the updated files to the same location
        """
        with open(os.path.join(os.path.join(str(self.path), "package.mo")), "w") as f:
            f.write(self.package_data)

        with open(os.path.join(os.path.join(str(self.path), "package.order")), "w") as f:
            f.write(self.order_data)
            f.write("\n")

    @property
    def order(self) -> list[str]:
        """Return the order of the packages from the package.order file

        Returns:
            list[str]: list of the loaded models in the package.order file
        """
        data = self.order_data.split("\n")
        if "" in data:
            data.remove("")
        return data

    def rename_model(self, old_model: str, new_model: str):
        """Rename the model name in the package.order file.

        Args:
            old_model (str): existing name
            new_model (str): new name
        """
        self.order_data = self.order_data.replace(old_model, new_model)

    def add_model(self, new_model_name: str, insert_at: int = -1) -> None:
        """Insert a new model into the package. Note that the order_data is stored as a string right now,
        so there is a bit of a hack to get this to work correctly.

        Args:
            new_model_name (str): name of the new model to add to the package order.
            insert_at (int, optional):  location to insert package, if 0 at beginning, -1 at end. Defaults to -1.
        """
        data = self.order_data.split("\n")
        if insert_at == -1:
            data.append(new_model_name)
        else:
            data.insert(insert_at, new_model_name)
        self.order_data = "\n".join(data)

        # remove any empty lines
        self.order_data = self.order_data.replace('\n\n', '\n')
