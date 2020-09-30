"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath


class TimeSeriesConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)

    def to_modelica(self, scaffold):
        """
        Create timeSeries models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        # The list of MOT files are conditional, but for now just include them all so that they exist as needed.

        # Building Load
        time_series_building_template = self.template_env.get_template("TimeSeriesBuilding.mot")

        # Building Only Coupling
        time_series_coupling_template = self.template_env.get_template("TimeSeriesCouplingBuilding.mot")
        time_series_mos_template = self.template_env.get_template("RunTimeSeriesBuilding.most")

        # ETS Models
        cooling_indirect_template = self.template_env.get_template("CoolingIndirect.mot")
        heating_indirect_template = self.template_env.get_template("HeatingIndirect.mot")
        time_series_ets_coupling_template = self.template_env.get_template("TimeSeriesCouplingETS.mot")
        time_series_ets_mos_template = self.template_env.get_template("RunTimeSeriesCouplingETS.most")

        # Central Plant
        time_series_mft_central_plant = self.template_env.get_template("TimeSeriesMassFlowTemperaturesCentralPlants.mot")

        # We should move to a LoadConnector only acting on a single building. Originally thought that a single
        # building/load can have multiple thermalzones/models. For now, assert that only a single building exists per
        # this connector. Move these validation methods to the base class (eventually).
        if len(self.buildings) == 0:
            raise Exception("No load to translate")

        if len(self.buildings) > 1:
            raise Exception("The TimeSeriesConnector is expecting only one building per connector")

        building = self.buildings[0]
        building_name = f"B{building['building_id']}"

        b_modelica_path = ModelicaPath(
            f"B{building['building_id']}", scaffold.loads_path.files_dir, True
        )

        self.copy_required_mo_files(b_modelica_path.files_dir, within=f'{scaffold.project_name}.Loads')

        # Note that the system_parameters object when accessing filepaths will fully resolve the
        # location of the file.
        time_series_filename = self.system_parameters.get_param_by_building_id(
            building["building_id"], "load_model_parameters.time_series.filepath"
        )

        if not os.path.exists(time_series_filename):
            raise Exception(f"Missing MOS file for time series: {time_series_filename}")
        elif os.path.splitext(time_series_filename)[1].lower() == '.csv':
            raise Exception("The timeseries file is CSV format. This must be converted to an MOS file for use.")

        # construct the dict to pass into the template. Depending on the type of model, not all the parameters are
        # used. The `nominal_values` are only used when the time series is coupled to an ETS system.
        template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "time_series": {
                "filepath": time_series_filename,
                "filename": os.path.basename(time_series_filename),
                "path": os.path.dirname(time_series_filename),
            },
            "nominal_values": {
                "delTDisCoo": self.system_parameters.get_param_by_building_id(
                    building["building_id"], "load_model_parameters.time_series.delTDisCoo"
                )
            }
        }

        # copy over the resource files for this building
        # TODO: move some of this over to a validation step
        new_file = os.path.join(b_modelica_path.resources_dir, os.path.basename(time_series_filename))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        shutil.copy(time_series_filename, new_file)

        self.run_template(
            template=time_series_building_template,
            save_file_name=os.path.join(b_modelica_path.files_dir, "building.mo"),
            project_name=scaffold.project_name,
            model_name=f"B{building['building_id']}",
            data=template_data
        )

        # Now switch between the building if it has only coupling vs when it has an ETS
        ets_model_type = self.system_parameters.get_param_by_building_id(
            building["building_id"], "ets_model"
        )

        if ets_model_type == "None":
            self.run_template(
                template=time_series_coupling_template,
                save_file_name=os.path.join(b_modelica_path.files_dir, "coupling.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{building['building_id']}",
                data=template_data
            )

            self.run_template(
                template=time_series_mos_template,
                save_file_name=os.path.join(b_modelica_path.scripts_dir, "RunTimeSeriesBuilding.most"),
                full_model_name=os.path.join(
                    scaffold.project_name,
                    scaffold.loads_path.files_relative_dir,
                    f"B{building['building_id']}",
                    "coupling").replace(os.path.sep, '.')
            )
        elif ets_model_type == "Indirect Heating and Cooling":
            # The ETS model is Indirect Cooling. If this model is to be connected to a district, then
            # somehow we need to know that context and remove the "TimeSeriesCouplingETS.mo file" and connect
            # the system to the distribution network.
            ets_data = self.system_parameters.get_param_by_building_id(
                building["building_id"],
                "ets_model_parameters.indirect"
            )

            self.run_template(
                template=cooling_indirect_template,
                save_file_name=os.path.join(b_modelica_path.files_dir, "CoolingIndirect.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{building['building_id']}",
                data=template_data,
                ets_data=ets_data,
            )

            self.run_template(
                template=heating_indirect_template,
                save_file_name=os.path.join(b_modelica_path.files_dir, "HeatingIndirect.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{building['building_id']}",
                data=template_data,
                ets_data=ets_data,
            )

            self.run_template(
                template=time_series_ets_coupling_template,
                save_file_name=os.path.join(b_modelica_path.files_dir, "TimeSeriesCouplingETS.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{building['building_id']}",
                data=template_data,
            )

            self.run_template(
                template=time_series_mft_central_plant,
                save_file_name=os.path.join(b_modelica_path.files_dir, "TimeSeriesMassFlowTemperaturesCentralPlants.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{building['building_id']}",
                data=template_data,
                ets_data=ets_data,
            )

            file_data = time_series_ets_mos_template.render(
                full_model_name=os.path.join(
                    scaffold.project_name,
                    scaffold.loads_path.files_relative_dir,
                    f"B{building['building_id']}", "TimeSeriesCouplingETS").replace(os.path.sep, '.'),
                model_name="TimeSeriesCouplingETS"
            )

            with open(os.path.join(b_modelica_path.scripts_dir, "RunTimeSeriesCouplingETS.mos"), "w") as f:
                f.write(file_data)
        else:
            raise Exception("Only ETS Model of type 'Indirect Heating and Cooling' and 'None' type enabled currently")

        # run post process to create the remaining project files for this building
        self.post_process(scaffold, building_name)

    def post_process(self, scaffold, building_name):
        """
        Cleanup the export of time series files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :return: None
        """
        b_modelica_path = os.path.join(scaffold.loads_path.files_dir, building_name)
        new_package = PackageParser.new_from_template(
            b_modelica_path, building_name, self.template_files_to_include,
            within=f"{scaffold.project_name}.Loads"
        )
        new_package.save()

        # now create the Loads level package. This (for now) will create the package without considering any existing
        # files in the Loads directory.
        # TODO: Check if the package.order and package.mo file exists, if so then just append
        package = PackageParser.new_from_template(
            scaffold.loads_path.files_dir, "Loads", [building_name], within=f"{scaffold.project_name}"
        )
        package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Loads"]
        )
        pp.save()
