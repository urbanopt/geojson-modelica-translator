# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class HeatPumpETS(ModelBase):
    model_name = "HeatPumpETS"

    def __init__(self, system_parameters, template_dir):
        super().__init__(system_parameters, template_dir)

        self.heat_pump_models = ["HeatPumpCooling.mot", "HeatPumpTrio.mot", "PartialHeatPumpCooling.mopt"]

    def to_modelica(self, scaffold):
        """Create indirect cooling models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        for model in self.heat_pump_models:
            template = self.template_env.get_template(model)
            self.run_template(
                template=template,
                save_file_name=scaffold.project_path / "Loads" / "ETS" / f"{Path(model).stem}.mo",
                project_name=scaffold.project_name,
            )

        # Add models to Loads.ETS package using scaffold's PackageParser
        package_models = [Path(model).stem for model in self.heat_pump_models]
        for model_name in package_models:
            scaffold.package.loads.ets.add_model(model_name, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return f"ETS.{self._model_filename}"
