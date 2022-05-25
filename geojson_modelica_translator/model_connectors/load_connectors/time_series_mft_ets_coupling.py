"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import os
import shutil
from pathlib import Path

from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath, simple_uuid


class TimeSeriesMFT(LoadBase):
    model_name = 'TimeSeriesMFT'

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = 'TimeSerMFTLoa_' + simple_uuid()

        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files.append(os.path.join(self.template_dir, 'getPeakMassFlowRate.mo'))

    def to_modelica(self, scaffold):
        """
        Create TimeSeries models based on the data in the building and geojson

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """

        # MassFlowrate Temperature models
        time_series_mft_template = self.template_env.get_template("TimeSeriesMassFlowTemperatures.mot")

        b_modelica_path = ModelicaPath(
            self.building_name, scaffold.loads_path.files_dir, True
        )

        # grab the data from the system_parameter file for this building id
        # TODO: create method in system_parameter class to make this easier and respect the defaults
        time_series_filename = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.time_series.filepath"
        )

        template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
            "nominal_values": {
                "delTDisCoo": self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.delTDisCoo"
                ),
                # FIXME: pick up default value from schema if not specified in system_parameters,
                # FYI: Modelica insists on booleans being lowercase, so we need to explicitly set "true" and "false"
                "has_liquid_heating": "true" if self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.has_liquid_heating",
                ) else "false",
                "has_liquid_cooling": "true" if self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.has_liquid_cooling",
                ) else "false",
                "has_electric_heating": "true" if self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.has_electric_heating",
                ) else "false",
                "has_electric_cooling": "true" if self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.has_electric_cooling",
                ) else "false",
            }
        }

        if os.path.exists(template_data["time_series"]["filepath"]):
            new_file = os.path.join(b_modelica_path.resources_dir, template_data["time_series"]["filename"])
            os.makedirs(os.path.dirname(new_file), exist_ok=True)
            shutil.copy(template_data["time_series"]["filepath"], new_file)
        else:
            raise Exception(f"Missing MOS file for time series: {template_data['time_series']['filepath']}")

        # Run templates to write actual Modelica models
        ets_model_type = self.system_parameters.get_param_by_building_id(self.building_id, "ets_model")

        ets_data = None
        if ets_model_type == "Indirect Heating and Cooling":
            ets_data = self.system_parameters.get_param_by_building_id(
                self.building_id,
                "ets_model_parameters.indirect"
            )
        else:
            raise Exception("Only ETS Model of type 'Indirect Heating and Cooling' type enabled currently")

        self.run_template(
            template=time_series_mft_template,
            save_file_name=Path(b_modelica_path.files_dir) / "building.mo",
            project_name=scaffold.project_name,
            model_name=self.building_name,
            data=template_data,
            ets_data=ets_data,
        )

        self.copy_required_mo_files(b_modelica_path.files_dir, within=f'{scaffold.project_name}.Loads')

        # Run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """
        Cleanup the export of TimeSeries files into a format suitable for the district-based analysis. This includes
        the following:
            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """
        order_files = [Path(mo).stem for mo in self.required_mo_files]
        order_files += self.template_files_to_include
        b_modelica_path = Path(scaffold.loads_path.files_dir) / self.building_name
        new_package = PackageParser.new_from_template(
            path=b_modelica_path,
            name=self.building_name,
            order=order_files,
            within=f"{scaffold.project_name}.Loads"
        )
        new_package.save()

        # now create the Loads level package and package.order.
        if not os.path.exists(os.path.join(scaffold.loads_path.files_dir, 'package.mo')):
            load_package = PackageParser.new_from_template(
                scaffold.loads_path.files_dir, "Loads", [self.building_name], within=f"{scaffold.project_name}"
            )
            load_package.save()
        else:
            load_package = PackageParser(os.path.join(scaffold.loads_path.files_dir))
            load_package.add_model(self.building_name)
            load_package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Loads"]
        )
        pp.save()

    def get_modelica_type(self, scaffold):
        return f'{scaffold.project_name}.Loads.{self.building_name}.building'
