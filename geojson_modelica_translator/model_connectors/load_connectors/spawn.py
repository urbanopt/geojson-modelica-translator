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


class Spawn(LoadBase):
    model_name = 'Spawn'

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = 'SpawnLoad_' + simple_uuid()

    def to_modelica(self, scaffold, keep_original_models=False):
        """
        Create spawn models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        spawn_coupling_template = self.template_env.get_template("SpawnCouplingBuilding.mot")
        spawn_building_template = self.template_env.get_template("SpawnBuilding.mot")
        spawn_mos_template = self.template_env.get_template("RunSpawnCouplingBuilding.most")

        # create spawn building and save to the correct directory
        print(f"Creating spawn for building: {self.building_id}")

        # Path for building data
        b_modelica_path = ModelicaPath(
            self.building_name, scaffold.loads_path.files_dir, True
        )

        # grab the data from the system_parameter file for this building id
        # TODO: create method in system_parameter class to make this easier and respect the defaults

        idf_filename = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.idf_filename"
        )
        epw_filename = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.epw_filename"
        )
        mos_weather_filename = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.mos_weather_filename",
        )
        thermal_zones = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.thermal_zone_names",
        )
        zone_nom_htg_loads = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.zone_nom_htg_loads",
        )
        zone_nom_clg_loads = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.zone_nom_clg_loads",
        )
        # TODO: pick up default value from schema if not specified in system_parameters,
        # to avoid the inline if/then statement in nominal_values below
        has_liquid_heating = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.has_liquid_heating",
        )
        has_liquid_cooling = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.has_liquid_cooling",
        )
        has_electric_heating = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.has_electric_heating",
        )
        has_electric_cooling = self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.has_electric_cooling",
        )
        hhw_supply_temp = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_hw_supply",
        ))
        hhw_return_temp = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_hw_return",
        ))
        chw_supply_temp = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_chw_supply",
        ))
        chw_return_temp = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_chw_return",
        ))
        temp_setpoint_cooling = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_setpoint_cooling",
        ))
        temp_setpoint_heating = convert_c_to_k(self.system_parameters.get_param_by_building_id(
            self.building_id, "load_model_parameters.spawn.temp_setpoint_heating",
        ))

        # construct the dict to pass into the template
        building_template_data = {
            "load_resources_path": b_modelica_path.resources_relative_dir,
            "idf": {
                "idf_filename": idf_filename,
                "filename": os.path.basename(idf_filename),
                "path": os.path.dirname(idf_filename),
            },
            "epw": {
                "epw_filename": epw_filename,
                "filename": os.path.basename(epw_filename),
                "path": os.path.dirname(epw_filename),
            },
            "mos_weather": {
                "mos_weather_filename": mos_weather_filename,
                "filename": os.path.basename(mos_weather_filename),
                "path": os.path.dirname(mos_weather_filename),
            },
            "thermal_zones": [],
            "thermal_zones_count": len(thermal_zones),
            "nominal_values": {
                "hhw_supply_temp": hhw_supply_temp,
                "hhw_return_temp": hhw_return_temp,
                "chw_supply_temp": chw_supply_temp,
                "chw_return_temp": chw_return_temp,
                "temp_setpoint_heating": temp_setpoint_heating,
                "temp_setpoint_cooling": temp_setpoint_cooling,
                "has_liquid_heating": "true" if has_liquid_heating else "false",
                "has_liquid_cooling": "true" if has_liquid_cooling else "false",
                "has_electric_heating": "true" if has_electric_heating else "false",
                "has_electric_cooling": "true" if has_electric_cooling else "false",
            },
            # Reformatting lists for Modelica
            "zone_nom_htg_loads": str(repr(zone_nom_htg_loads)).replace("[", "{").replace("]", "}").split("rray(", 1)[-1],
            "zone_nom_clg_loads": str(repr(zone_nom_clg_loads)).replace("[", "{").replace("]", "}").split("rray(", 1)[-1],
        }
        for tz in thermal_zones:
            # TODO: method for creating nice zone names for modelica
            building_template_data["thermal_zones"].append(
                {"modelica_object_name": f"zn{tz}", "spawn_object_name": tz}
            )

        # copy over the resource files for this building
        # TODO: move some of this over to a validation step
        if os.path.exists(building_template_data["idf"]["idf_filename"]):
            shutil.copy(
                building_template_data["idf"]["idf_filename"],
                os.path.join(
                    b_modelica_path.resources_dir,
                    building_template_data["idf"]["filename"],
                ),
            )
        else:
            raise Exception(
                f"Missing IDF file for Spawn: {building_template_data['idf']['idf_filename']}"
            )

        if os.path.exists(building_template_data["epw"]["epw_filename"]):
            shutil.copy(building_template_data["epw"]["epw_filename"],
                        os.path.join(b_modelica_path.resources_dir, building_template_data["epw"]["filename"]))
        else:
            raise Exception(f"Missing EPW file for Spawn: {building_template_data['epw']['epw_filename']}")

        if os.path.exists(building_template_data["mos_weather"]["mos_weather_filename"]):
            shutil.copy(
                building_template_data["mos_weather"]["mos_weather_filename"],
                os.path.join(b_modelica_path.resources_dir, building_template_data["mos_weather"]["filename"])
            )
        else:
            raise Exception(
                f"Missing MOS weather file for Spawn: {building_template_data['mos_weather']['mos_weather_filename']}")
        # merge ets template values from load_base.py into the building nominal values
        # If there is no ets defined in sys-param file, use the building template data alone
        try:
            nominal_values = {**building_template_data['nominal_values'], **self.ets_template_data}
            combined_template_data = {**building_template_data, **nominal_values}
        except AttributeError:
            combined_template_data = building_template_data

        self.run_template(
            spawn_building_template,
            os.path.join(b_modelica_path.files_dir, "building.mo"),
            project_name=scaffold.project_name,
            model_name=self.building_name,
            data=combined_template_data
        )

        full_model_name = os.path.join(
            scaffold.project_name,
            scaffold.loads_path.files_relative_dir,
            self.building_name,
            "coupling").replace(os.path.sep, '.')

        file_data = spawn_mos_template.render(full_model_name=full_model_name, model_name=self.model_name)
        with open(os.path.join(b_modelica_path.scripts_dir, "RunSpawnCouplingBuilding.mos"), "w") as f:
            f.write(file_data)

        self.run_template(
            spawn_coupling_template,
            os.path.join(b_modelica_path.files_dir, "coupling.mo"),
            project_name=scaffold.project_name,
            model_name=self.building_name,
            data=combined_template_data
        )

        # Copy the required modelica files
        self.copy_required_mo_files(b_modelica_path.files_dir, within=f'{scaffold.project_name}.Loads')

        # run post process to create the remaining project files for this building
        self.post_process(scaffold, keep_original_models=keep_original_models)

    def post_process(self, scaffold, keep_original_models=False):
        """
        Cleanup the export of Spawn files into a format suitable for the district-based analysis. This includes
        the following:

            * Add a Loads project
            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :param keep_original_models: boolean, # TODO
        :return: None
        """
        b_modelica_path = os.path.join(scaffold.loads_path.files_dir, self.building_name)
        new_package = PackageParser.new_from_template(
            b_modelica_path, self.building_name, ["building", "coupling"], within=f"{scaffold.project_name}.Loads"
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
