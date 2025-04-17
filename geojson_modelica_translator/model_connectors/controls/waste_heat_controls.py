# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.model_base import ModelBase


class WasteHeatControls(ModelBase):
    model_name = "WasteHeatControls"

    def __init__(self, system_parameters, template_dir):
        super().__init__(system_parameters, template_dir)

        self.controls_models = ["WasteHeatController.mot"]

    def to_modelica(self, scaffold):
        """Create indirect cooling models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        template_data = {
            "rate_schedule_path": self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.rate_schedule_path"
            ),
            "rate_schedule_filename": Path(
                self.system_parameters.get_param(
                    "$.district_system.fifth_generation.waste_heat_parameters.rate_schedule_path"
                )
            ).name,
            "temperature_schedule_path": self.system_parameters.get_param(
                "$.district_system.fifth_generation.waste_heat_parameters.temperature_schedule_path"
            ),
            "temperature_schedule_filename": Path(
                self.system_parameters.get_param(
                    "$.district_system.fifth_generation.waste_heat_parameters.temperature_schedule_path"
                )
            ).name,
        }

        for model in self.controls_models:
            template = self.template_env.get_template(model)
            self.run_template(
                template=template,
                save_file_name=scaffold.project_path / "Controls" / f"{Path(model).stem}.mo",
                project_name=scaffold.project_name,
                template_data=template_data,
            )

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if "Controls" not in package.order:
            package.add_model("Controls")
            package.save()

        package_models = [Path(model).stem for model in self.controls_models]
        controls_package = PackageParser(scaffold.controls_path.files_dir)
        if controls_package.order_data is None:
            controls_package = PackageParser.new_from_template(
                path=scaffold.controls_path.files_dir,
                name="Controls",
                order=package_models,
                within=scaffold.project_name,
            )
        else:
            for model_name in package_models:
                if model_name not in controls_package.order:
                    controls_package.add_model(model_name)
        controls_package.save()

    def get_modelica_type(self, scaffold):
        return f"Controls.{self._model_filename}"
