# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from modelica_builder.package_parser import PackageParser

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

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path / "Loads")
        if "ETS" not in package.order:
            package.add_model("ETS")
            package.save()

        package_models = [Path(model).stem for model in self.heat_pump_models]
        ets_package = PackageParser(scaffold.heat_pump_ets_path.files_dir)
        if ets_package.order_data is None:
            ets_package = PackageParser.new_from_template(
                path=scaffold.heat_pump_ets_path.files_dir,
                name="ETS",
                order=package_models,
                within=f"{scaffold.project_name}.Loads",
            )
        else:
            for model_name in package_models:
                if model_name not in ets_package.order:
                    ets_package.add_model(model_name)
        ets_package.save()

    def get_modelica_type(self, scaffold):
        return f"ETS.{self._model_filename}"
