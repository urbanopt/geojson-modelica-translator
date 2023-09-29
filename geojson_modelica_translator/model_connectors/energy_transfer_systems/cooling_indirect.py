# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os

from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.utils import simple_uuid


class CoolingIndirect(EnergyTransferBase):
    model_name = 'CoolingIndirect'

    def __init__(self, system_parameters, geojson_load_id):
        super().__init__(system_parameters, geojson_load_id)
        self.id = 'cooInd_' + simple_uuid()
        # _model_filename is the name of the file we generate, and thus the actual
        # model to be referenced when instantiating in the District model
        # TODO: refactor these property names (model_name and model_filename) because
        # it's confusing
        self._model_filename = f'CoolingIndirect_{self._geojson_load_id}'

    def to_modelica(self, scaffold):
        """
        Create indirect cooling models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        cooling_indirect_template = self.template_env.get_template("CoolingIndirect.mot")

        ets_data = self.system_parameters.get_param_by_building_id(
            self._geojson_load_id,
            'ets_indirect_parameters'
        )

        combined_template_data = {**ets_data, **self.district_template_data}

        self.run_template(
            template=cooling_indirect_template,
            save_file_name=os.path.join(scaffold.project_path, 'Substations', f'{self._model_filename}.mo'),
            project_name=scaffold.project_name,
            model_filename=self._model_filename,
            ets_data=combined_template_data,
        )

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if 'Substations' not in package.order:
            package.add_model('Substations')
            package.save()

        package_models = [self._model_filename]
        ets_package = PackageParser(scaffold.substations_path.files_dir)
        if ets_package.order_data is None:
            ets_package = PackageParser.new_from_template(
                path=scaffold.substations_path.files_dir,
                name="Substations",
                order=package_models,
                within=scaffold.project_name)
        else:
            for model_name in package_models:
                if model_name not in ets_package.order:
                    ets_package.add_model(model_name)
        ets_package.save()

    def get_modelica_type(self, scaffold):
        return f'Substations.{self._model_filename}'
