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
from pathlib import Path

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from modelica_builder.model import Model


class DistrictSystemConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        # Note that the order of the required MO files is important as it will be the order that
        # the "package.order" will be in.
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialDistribution.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialBuildingETS.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PartialBuildingWithCoolingIndirectETS.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'BuildingSpawnZ6WithCoolingIndirectETS.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'CentralCoolingPlant.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ChilledWaterPumpSpeed.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ChillerStage.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'ConnectionParallel.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'CoolingTowerParallel.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'CoolingTowerWithBypass.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'DesignDataParallel4GDC.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PipeDistribution.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'PipeConnection.mo'))
        self.required_mo_files.append(os.path.join(self.template_dir, 'UnidirectionalParallel.mo'))

    def to_modelica(self, scaffold, model_connector_base):
        """
        # TODO: Need to pass in list of buildings to connect to network.

        Create district system models based on the data in the geojson and system parameter file.

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        curdir = os.getcwd()

        try:
            district_cooling_system_template = self.template_env.get_template("DistrictCoolingSystem.mot")
            cooling_indirect_template = self.template_env.get_template("CoolingIndirect.mot")
            heating_indirect_template = self.template_env.get_template("HeatingIndirect.mot")
            spawn_building_template = self.template_env.get_template("SpawnBuilding.mot")

            idf_filename = self.system_parameters.get_param(
                "$.buildings.default.load_model_parameters.spawn.idf_filename"
            )
            epw_filename = self.system_parameters.get_param(
                "$.buildings.default.load_model_parameters.spawn.epw_filename"
            )
            mos_weather_filename = self.system_parameters.get_param(
                "$.buildings.default.load_model_parameters.spawn.mos_weather_filename"
            )
            mos_wet_bulb_filename = self.system_parameters.get_param(
                "$.buildings.default.load_model_parameters.spawn.mos_wet_bulb_filename"
            )
            thermal_zones = self.system_parameters.get_param(
                "$.buildings.default.load_model_parameters.spawn.thermal_zone_names"
            )

            # construct the dict to pass into the template
            template_data = {
                "load_resources_path": scaffold.districts_path.resources_relative_dir,
                "idf": {
                    "idf_filename": idf_filename,
                    "filename": os.path.basename(idf_filename),
                    "path": os.path.dirname(idf_filename),
                    "modelica_path": model_connector_base.modelica_path(self, idf_filename),
                },
                "epw": {
                    "epw_filename": epw_filename,
                    "filename": os.path.basename(epw_filename),
                    "path": os.path.dirname(epw_filename),
                    "modelica_path": model_connector_base.modelica_path(self, epw_filename),
                },
                "mos_weather": {
                    "mos_weather_filename": mos_weather_filename,
                    "filename": os.path.basename(mos_weather_filename),
                    "path": os.path.dirname(mos_weather_filename),
                    # TODO: Should/How/Can we remove "model_connector_base" here? Compare line 112 with line 220
                    "modelica_path": model_connector_base.modelica_path(self, mos_weather_filename),
                },
                "wet_bulb_calc": {
                    "mos_wet_bulb_filename": mos_wet_bulb_filename,
                    "filename": Path(mos_wet_bulb_filename).name,
                    "path": Path(mos_wet_bulb_filename).parent,
                    "modelica_path": model_connector_base.modelica_path(self, mos_wet_bulb_filename),
                },
                "nominal_values": {
                    "delta_temp": self.system_parameters.get_param(
                        "$.district_system.default.cooling_plant.delta_t_nominal"
                    ),
                    "fan_power": self.system_parameters.get_param(
                        "$.district_system.default.cooling_plant.fan_power_nominal"
                    ),
                    "chilled_water_pump_pressure_drop": self.system_parameters.get_param(
                        "$.district_system.default.cooling_plant.chilled_water_pump_pressure_drop"
                    ),
                    "condenser_water_pump_pressure_drop": self.system_parameters.get_param(
                        "$.district_system.default.cooling_plant.condenser_water_pump_pressure_drop"
                    )
                },
                "thermal_zones": [],
                "thermal_zones_count": len(thermal_zones),
            }
            for tz in thermal_zones:
                # TODO: method for creating nice zone names for modelica
                template_data["thermal_zones"].append(
                    {"modelica_object_name": f"zn{tz}", "spawn_object_name": tz}
                )

            # copy over the resource files for this building
            # TODO: move some of this over to a validation step
            if os.path.exists(template_data["idf"]["idf_filename"]):
                shutil.copy(
                    template_data["idf"]["idf_filename"],
                    os.path.join(
                        scaffold.districts_path.resources_dir,
                        template_data["idf"]["filename"],
                    ),
                )
            else:
                raise Exception(
                    f"Missing IDF file for Spawn: {template_data['idf']['idf_filename']}"
                )

            if os.path.exists(template_data["epw"]["epw_filename"]):
                shutil.copy(template_data["epw"]["epw_filename"],
                            os.path.join(scaffold.districts_path.resources_dir, template_data["epw"]["filename"]))
            else:
                raise Exception(f"Missing EPW file for Spawn: {template_data['epw']['epw_filename']}")

            if os.path.exists(template_data["mos_weather"]["mos_weather_filename"]):
                shutil.copy(
                    template_data["mos_weather"]["mos_weather_filename"],
                    os.path.join(scaffold.districts_path.resources_dir, template_data["mos_weather"]["filename"])
                )
            else:
                raise Exception(
                    f"Missing MOS weather file for Spawn: {template_data['mos_weather']['mos_weather_filename']}")

            self.run_template(
                spawn_building_template,
                os.path.join(scaffold.districts_path.files_dir, "building.mo"),
                project_name=scaffold.project_name,
                model_name="SOMEMODELNAME",
                data=template_data
            )
            # rename the within clause because this is not too flexible and the ETS needs to be in
            # a different directory (not districts), but that isn't the case.
            mofile = Model(os.path.join(scaffold.districts_path.files_dir, "building.mo"))

            # previous paths and replace with the new one.
            # Make sure to update the names of any resources as well.
            mofile.set_within_statement(f'{scaffold.project_name}.Districts')
            mofile.save()

            self.run_template(
                district_cooling_system_template,
                os.path.join(scaffold.districts_path.files_dir, "DistrictCoolingSystem.mo"),
                project_name=scaffold.project_name,
                data=template_data
            )

            ets_model_type = self.system_parameters.get_param("$.buildings.default.ets_model")
            ets_data = self.system_parameters.get_param(
                    "$.buildings.default.ets_model_parameters.indirect"
                )
            if "Cooling" in ets_model_type:
                self.run_template(
                    cooling_indirect_template,
                    os.path.join(scaffold.districts_path.files_dir, "CoolingIndirect.mo"),
                    project_name=scaffold.project_name,
                    model_name="RENAMEME",
                    ets_data=ets_data
                )
                # rename the within clause because this is not too flexible and the ETS needs to be in
                # a different directory (not districts), but that isn't the case.
                mofile = Model(os.path.join(scaffold.districts_path.files_dir, "CoolingIndirect.mo"))

                # TODO: DRY up this if statement and rearrange the whole DistrictSystemConnector class
            elif "Heating" in ets_model_type:
                self.run_template(
                    heating_indirect_template,
                    os.path.join(scaffold.districts_path.files_dir, "HeatingIndirect.mo"),
                    project_name=scaffold.project_name,
                    model_name="RENAMEME",
                    ets_data=ets_data
                )
                # rename the within clause because this is not too flexible and the ETS needs to be in
                # a different directory (not districts), but that isn't the case.
                mofile = Model(os.path.join(scaffold.districts_path.files_dir, "HeatingIndirect.mo"))

            else:
                raise Exception("Only ETS Model of type 'Indirect Cooling' or 'Indirect Heating' type enabled currently")

            # previous paths and replace with the new one.
            # Make sure to update the names of any resources as well.
            mofile.set_within_statement(f'{scaffold.project_name}.Districts')
            mofile.save()

            self.copy_required_mo_files(
                scaffold.districts_path.files_dir, within=f'{scaffold.project_name}.Districts'
            )

        finally:
            os.chdir(curdir)

        # run post process to create the remaining project files for this building
        self.post_process(scaffold)

    def post_process(self, scaffold):
        """
        Cleanup the export of district systems. This includes the following:

            * Add a project level project

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        :return: None
        """

        # now create the Districts level package. This (for now) will create the package without
        # considering any existing files in the Districts directory.
        order_files = [os.path.splitext(os.path.basename(mo))[0] for mo in self.required_mo_files]
        order_files.append("DistrictCoolingSystem")
        order_files.append("CoolingIndirect")
        order_files.append("building")
        package = PackageParser.new_from_template(
            scaffold.districts_path.files_dir, "Districts",
            order=order_files,
            within=f"{scaffold.project_name}"
        )
        package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Districts"]
        )
        pp.save()
