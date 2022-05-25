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

from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import (
    ModelicaPath,
    convert_c_to_k,
    simple_uuid
)


class TimeSeries(LoadBase):
    model_name = 'TimeSeries'

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = 'TimeSerLoa_' + simple_uuid()

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        time_series_building_template = self.template_env.get_template("TimeSeriesBuilding.mot")

        b_modelica_path = ModelicaPath(
            self.building_name, scaffold.loads_path.files_dir, True
        )

        self.copy_required_mo_files(b_modelica_path.files_dir, within=f'{scaffold.project_name}.Loads')

        # Note that the system_parameters object when accessing filepaths will fully resolve the
        # location of the file.
        time_series_filename = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.time_series.filepath"
        )

        if not os.path.exists(time_series_filename):
            raise Exception(f"Missing MOS file for time series: {time_series_filename}")
        elif os.path.splitext(time_series_filename)[1].lower() == '.csv':
            raise Exception("The timeseries file is CSV format. This must be converted to an MOS file for use.")

        # construct the dict to pass into the template. Depending on the type of model, not all the parameters are
        # used. The `nominal_values` are only used when the time series is coupled to an ETS system.
        building_template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
            "nominal_values": {
                "delta_temp_air_cooling": self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.delta_temp_air_cooling"
                ),
                "delta_temp_air_heating": self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.delta_temp_air_heating"
                ),
                "temp_setpoint_heating": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_setpoint_heating"
                )),
                "temp_setpoint_cooling": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_setpoint_cooling"
                )),
                "chw_supply_temp": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_chw_supply"
                )),
                "chw_return_temp": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_chw_return"
                )),
                "hhw_supply_temp": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_hw_supply"
                )),
                "hhw_return_temp": convert_c_to_k(self.system_parameters.get_param_by_building_id(
                    self.building_id, "load_model_parameters.time_series.temp_hw_return"
                )),
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

        # merge ets template values from load_base.py into the building nominal values
        # If there is no ets defined in sys-param file, use the building template data alone
        try:
            nominal_values = {**building_template_data['nominal_values'], **self.ets_template_data}
            combined_template_data = {**building_template_data, **nominal_values}
        except AttributeError:
            combined_template_data = building_template_data

        # copy over the resource files for this building
        # TODO: move some of this over to a validation step
        new_file = os.path.join(b_modelica_path.resources_dir, os.path.basename(time_series_filename))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        shutil.copy(time_series_filename, new_file)

        self.run_template(
            template=time_series_building_template,
            save_file_name=os.path.join(b_modelica_path.files_dir, "building.mo"),
            project_name=scaffold.project_name,
            model_name=self.building_name,
            data=combined_template_data
        )

        # run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """
        Cleanup the export of time series files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """
        b_modelica_path = os.path.join(scaffold.loads_path.files_dir, self.building_name)
        new_package = PackageParser.new_from_template(
            b_modelica_path, self.building_name, self.template_files_to_include,
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
        package = PackageParser(scaffold.project_path)
        if 'Loads' not in package.order:
            package.add_model('Loads')
            package.save()

    def get_modelica_type(self, scaffold):
        return f'{scaffold.project_name}.Loads.{self.building_name}.building'
