from pathlib import Path

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class SimpleGMTBase(ModelBase):
    """Base class for simple GMT models."""

    def __init__(self, system_parameters, template_dir):
        """
        Initialize the SimpleGMT object.
        """
        super().__init__(system_parameters, template_dir)

    def to_modelica(self, output_dir: Path, model_name: str, param_data: dict, iteration='') -> None:
        """
        Render the template to a Modelica file.
        """
        # render template to final modelica file
        model_template = self.template_env.get_template(f"{model_name}.mot")
        self.run_template(
            template=model_template,
            save_file_name=output_dir / f"{model_name}{iteration}.mo",
            project_name=output_dir.stem,
            data=param_data
        )
