# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import EnergyTransferBase
from geojson_modelica_translator.utils import simple_uuid


class CoolingIndirect(EnergyTransferBase):
    model_name = "CoolingIndirect"

    def __init__(self, system_parameters, geojson_load_id):
        super().__init__(system_parameters, geojson_load_id)
        self.id = "cooInd_" + simple_uuid()
        # _model_filename is the name of the file we generate, and thus the actual
        # model to be referenced when instantiating in the District model
        # TODO: refactor these property names (model_name and model_filename) because
        # it's confusing
        self._model_filename = f"CoolingIndirect_{self._geojson_load_id}"

    def to_modelica(self, scaffold):
        """Create indirect cooling models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        cooling_indirect_template = self.template_env.get_template("CoolingIndirect.mot")

        ets_data = self.system_parameters.get_param_by_id(self._geojson_load_id, "ets_indirect_parameters")

        combined_template_data = {**ets_data, **self.district_template_data}

        self.run_template(
            template=cooling_indirect_template,
            save_file_name=os.path.join(scaffold.project_path, "Substations", f"{self._model_filename}.mo"),
            project_name=scaffold.project_name,
            model_filename=self._model_filename,
            ets_data=combined_template_data,
        )

        # Add model to the Substations package using scaffold's PackageParser
        scaffold.package.substations.add_model(self._model_filename, create_subpackage=False)
        scaffold.package.save()

    def get_modelica_type(self, scaffold):
        return f"Substations.{self._model_filename}"
