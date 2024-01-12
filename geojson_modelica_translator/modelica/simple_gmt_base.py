# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class SimpleGMTBase(ModelBase):
    """Base class for simple GMT models."""

    def __init__(self, system_parameters, template_dir):
        """
        Initialize the SimpleGMT object.
        """
        super().__init__(system_parameters, template_dir)

    def to_modelica(self, output_dir: Path, model_name: str, param_data: dict, iteration=None,
                    save_file_name=None, generate_package=False, partial_files: dict = None) -> None:
        """Render the template to a Modelica file.

        Args:
            output_dir (Path): Directory to save the resulting template (modelica file) to.
            model_name (str): Model to render and also the name of the saved file (if save_file_name is None).
            param_data (dict): Data to pass to the rendering template.
            iteration (Int, optional): If dynamically creating filenames, then this is the iteration to
                                       be appended to the filename. Defaults to None.
            save_file_name (Str, optional): Name that the file will be saved as, if None, then will default.
                                            Do not include the directory, only the filename (with extension).
                                            Defaults to None.
            generate_package (bool, optional): If True, then a package.mo and package.order file will be created
                                               alongside the rendered template (Modelica) file. Defaults to False.
            partial_files (dict, optional): If the model has partial files, then this is a dictionary of the
                                            partial file name and the Modelica file name to save it as. Defaults to None.
        """
        # render template to final modelica file
        model_template = self.template_env.get_template(f"{model_name}.mot")

        # If the user passes in save_file_name, then use that name instead of trying
        # to figure out the name.
        if not save_file_name:
            if iteration is not None or iteration == '':
                save_file_name = output_dir / f"{model_name}{iteration}.mo"
            else:
                save_file_name = output_dir / f"{model_name}.mo"
        else:
            save_file_name = output_dir / save_file_name

        self.run_template(
            template=model_template,
            save_file_name=save_file_name,
            project_name=output_dir.stem,
            data=param_data
        )

        # store the order of the models that will be in the package (if requested)
        package_order = []
        package_order.append(save_file_name.stem)

        # Check if there are partial models (or other templated data) to be evaluated / saved.
        if partial_files:
            for template, filename in partial_files.items():
                self.run_template(
                    template=self.template_env.get_template(f"{template}.mot"),
                    save_file_name=output_dir / f"{filename}.mo",
                    project_name=output_dir.stem,
                    data=param_data
                )
                package_order.insert(0, filename)

        # include package.mo and package.order files if requested.
        # TODO: This will need to be updated to support multiple models in the "order".
        if generate_package:
            package = PackageParser.new_from_template(
                str(output_dir),
                output_dir.stem,
                order=package_order,
                within=output_dir.parent.stem
            )
            package.save()
