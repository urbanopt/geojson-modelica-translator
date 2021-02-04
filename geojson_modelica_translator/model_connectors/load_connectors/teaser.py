"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import glob
import os
import shutil

from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import (
    ModelicaPath,
    copytree,
    simple_uuid
)
from modelica_builder.model import Model
from teaser.project import Project


class Teaser(LoadBase):
    """TEASER is different than the other model connectors since TEASER creates all of the building models with
    multiple thermal zones when running, at which point each building then needs to be processed."""
    model_name = 'Teaser'

    def __init__(self, system_parameters, geojson_load):
        super().__init__(system_parameters, geojson_load)
        self.id = 'TeaserLoad_' + simple_uuid()

    def lookup_building_type(self, building_type):
        """Look up the building type from the Enumerations in the building_properties.json schema. TEASER
        documentation on building types is here (look into the python files):

        https://github.com/RWTH-EBC/TEASER/tree/development/teaser/logic/archetypebuildings/bmvbs
        """

        # Also look at using JSON as the input: https://github.com/RWTH-EBC/TEASER/blob/master/teaser/examples/examplefiles/ASHRAE140_600.json  # noqa
        mapping = {
            # Single Family is not configured right now.
            "Single-Family": "SingleFamilyDwelling",
            "Office": "office",
            "Laboratory": "institute8",
            "Education": "institute",
            "Inpatient health care": "institute8",
            "Outpatient health care": "institute4",
            "Nursing": "institute4",
            "Service": "institute4",
            "Retail other than mall": "office",
            "Strip shopping mall": "office",
            "Enclosed mall": "office",
            "Food sales": "institute4",
            "Food service": "institute4",
        }

        # Other types to map!
        #         "Multifamily (2 to 4 units)",
        #         "Multifamily (5 or more units)",
        #         "Mobile Home",
        #         "Vacant",
        #         "Nonrefrigerated warehouse",
        #         "Public order and safety",
        #         "Refrigerated warehouse",
        #         "Religious worship",
        #         "Public assembly",
        #         "Lodging",
        #         "Mixed use",
        #         "Uncovered Parking",
        #         "Covered Parking"
        if building_type in mapping.keys():
            return mapping[building_type]
        else:
            raise Exception(f"Building type of {building_type} not defined in GeoJSON to TEASER mappings")

    def to_modelica(self, scaffold, keep_original_models=False):
        """
        Save the TEASER representation of the buildings to the filesystem. The path will
        be scaffold.loads_path.files_dir.

        :param scaffold: Scaffold object, contains all the paths of the project
        :param keep_original_models: boolean, whether or not to remove the models after exporting from Teaser

        """
        # Teaser changes the current dir, so make sure to reset it back to where we started
        building_names = []
        curdir = os.getcwd()
        try:
            prj = Project(load_data=True)
            for building in self.buildings:
                building_name = building["building_id"]
                prj.add_non_residential(
                    method="bmvbs",
                    usage=self.lookup_building_type(building["building_type"]),
                    name=building_name,
                    year_of_construction=building["year_built"],
                    number_of_floors=building["num_stories"],
                    height_of_floors=building["floor_height"],
                    net_leased_area=building["area"],
                    office_layout=1,
                    window_layout=1,
                    with_ahu=False,
                    construction_type="heavy",
                )
                building_names.append(building_name)

                prj.used_library_calc = "IBPSA"
                prj.number_of_elements_calc = self.system_parameters.get_param(
                    "buildings.default.load_model_parameters.rc.order", default=2
                )
                prj.merge_windows_calc = False

            # calculate the properties of all the buildings and export to the Buildings library
            prj.calc_all_buildings()
            prj.export_ibpsa(library="Buildings", path=os.path.join(curdir, scaffold.loads_path.files_dir))

        finally:
            os.chdir(curdir)

        self.post_process(scaffold, building_names, keep_original_models=keep_original_models)

    def post_process(self, scaffold, building_names, keep_original_models=False):
        """
        Cleanup the export of the TEASER files into a format suitable for the district-based analysis. This includes
        the following:

            * Update the partial to inherit from the GeojsonExport class defined in MBL.
            * Rename the files to remove the names of the buildings
            * Move the files to the Loads level and remove the Project folder (default export method from TEASER)
            * Add heat port
            * Add return temperature
            * Add fluid ports for the indoor air volume.
            * Remove weaDat and rely on weaBus
            * Add latent fraction multiplier
            * Add TAir output
            * Add TRad output
            * Add nPorts variable
            * Propagate use of moisture balance
            * Wrap the thermal zones into a single model

        :param project_name: string, name of the project which will be used to set the package.mo file
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :param keep_original_models: boolean, # TODO
        :return: None
        """

        teaser_building = self.template_env.get_template("TeaserBuilding.mot")
        teaser_coupling = self.template_env.get_template("TeaserCouplingBuilding.mot")
        run_coupling_template = self.template_env.get_template("RunTeaserCouplingBuilding.most")

        # This for loop does *a lot* of work to make the models compatible for the project structure.
        # Need to investigate moving this into a more testable location.
        for b in building_names:
            # create a list of strings that we need to replace in all the file as we go along
            string_replace_list = []
            mos_weather_filename = self.system_parameters.get_param_by_building_id(
                b, "load_model_parameters.rc.mos_weather_filename")
            # create a new modelica based path for the buildings # TODO: make this work at the toplevel, somehow.
            b_modelica_path = ModelicaPath(f"B{b}", scaffold.loads_path.files_dir, True)

            # copy over the entire model to the new location
            copytree(
                os.path.join(scaffold.loads_path.files_dir, f"Project/B{b}/B{b}_Models"),
                b_modelica_path.files_dir,
            )

            # read in the package to apply the changes as they other files are processed
            # TODO: these should be linked, so a rename method should act across the model and the package.order
            package = PackageParser(os.path.join(scaffold.loads_path.files_dir, f"B{b}"))

            # move the internal gains files to a new resources folder
            mat_files = glob.glob(os.path.join(scaffold.loads_path.files_dir, f"B{b}/*.txt"))
            for f in mat_files:
                new_file_name = os.path.basename(f).replace(f"B{b}", "")
                os.rename(f, f"{b_modelica_path.resources_dir}/{new_file_name}")
                string_replace_list.append(
                    (
                        f"Project/B{b}/B{b}_Models/{os.path.basename(f)}",
                        f"{scaffold.project_name}/Loads/{b_modelica_path.resources_relative_dir}/{new_file_name}",
                    )
                )

            # process each of the thermal zones
            thermal_zone_files = []
            mo_files = glob.glob(os.path.join(scaffold.loads_path.files_dir, f"B{b}/*.mo"))
            for f in mo_files:
                # ignore the package.mo file
                if os.path.basename(f) in ["package.mo"]:
                    continue

                mofile = Model(f)

                # previous paths and replace with the new one.
                # Make sure to update the names of any resources as well.
                mofile.set_within_statement(f'{scaffold.project_name}.Loads.B{b}')

                # remove ReaderTMY3
                mofile.remove_component("Buildings.BoundaryConditions.WeatherData.ReaderTMY3", "weaDat")

                # updating path to internal loads
                for s in string_replace_list:
                    new_file_path = s[1]
                    new_resource_arg = f'''Modelica.Utilities.Files.loadResource("modelica://{new_file_path}")'''
                    old_file_path = s[0]
                    old_resource_arg = f'''Modelica.Utilities.Files.loadResource("modelica://{old_file_path}")'''

                    mofile.update_component_modification(
                        "Modelica.Blocks.Sources.CombiTimeTable",
                        "internalGains",
                        "fileName",
                        new_resource_arg,
                        if_value=old_resource_arg
                    )

                # add heat port convective heat flow.
                mofile.insert_component(
                    "Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a", "port_a",
                    string_comment='Heat port for convective heat flow.',
                    annotations=[
                        "Placement(transformation(extent={{-10,90},{10,110}}), "
                        "iconTransformation(extent={{-10,90},{10,110}}))"
                    ]
                )
                # add heat port radiative heat flow.
                mofile.insert_component(
                    "Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a", "port_b",
                    string_comment='Heat port for radiative heat flow.',
                    annotations=[
                        "Placement(transformation(extent={{30,-110},{50,-90}}, "
                        "iconTransformation(extent={{40,-112},{60,-92}})))"
                    ]
                )
                # add fluid ports for the indoor air volume.
                mofile.insert_component(
                    "Modelica.Fluid.Vessels.BaseClasses.VesselFluidPorts_b", "ports[nPorts]",
                    string_comment='Auxiliary fluid inlets and outlets to indoor air volume.',
                    modifications={
                        'redeclare each final package Medium': 'Buildings.Media.Air'
                    },
                    annotations=[
                        "Placement(transformation(extent={{-30, -8}, {30, 8}},origin={0, -100}), "
                        "iconTransformation(extent={{-23.25, -7.25}, {23.25, 7.25}},"
                        "origin={-0.75, -98.75}))"
                    ]
                )

                fraction_latent_person = self.system_parameters.get_param(
                    "buildings.default.load_model_parameters.rc.fraction_latent_person", default=1.25
                )

                use_moisture_balance = self.system_parameters.get_param(
                    "buildings.default.load_model_parameters.rc.use_moisture_balance", default='false'
                )

                n_ports = self.system_parameters.get_param(
                    "buildings.default.load_model_parameters.rc.nPorts", default=0
                )

                # create a new parameter for fraction latent person
                mofile.add_parameter(
                    'Real', 'fraLat',
                    assigned_value=fraction_latent_person,
                    string_comment='Fraction latent of sensible persons load = 0.8 for home, 1.25 for office.'
                )
                # create a new Boolean parameter to evaluate the persons latent loads.
                mofile.add_parameter(
                    'Boolean', 'use_moisture_balance',
                    assigned_value=use_moisture_balance,
                    string_comment='If true, input connector QLat_flow is enabled and room air computes'
                                   ' moisture balance.'
                )
                # create a integer parameter to evaluate number of connected ports.
                mofile.add_parameter(
                    'Integer', 'nPorts',
                    assigned_value=n_ports,
                    string_comment='Number of fluid ports.',
                    annotations=['connectorSizing=true']
                )
                # Set the fraction latent person in the template by simply replacing the value
                mofile.insert_component(
                    'Modelica.Blocks.Sources.RealExpression', 'perLatLoa',
                    modifications={
                        'y': 'internalGains.y[2]*fraLat',
                    },
                    conditional='if use_moisture_balance',
                    string_comment='Latent person loads',
                    annotations=['Placement(transformation(extent={{-80,-60},{-60,-40}}))']
                )

                # add TRad output
                mofile.insert_component(
                    'Buildings.Controls.OBC.CDL.Interfaces.RealOutput', 'TRad',
                    modifications={
                        'quantity': '"ThermodynamicTemperature"',
                        'unit': '"K"',
                        'displayUnit': '"degC"',
                    },
                    string_comment='Mean indoor radiation temperature',
                    annotations=['Placement(transformation(extent={{100,-10},{120,10}}))']
                )

                # All existing weaDat.weaBus connections need to be updated to simply weaBus
                # (except for the connections where 'weaBus' is port_b, we will just delete these)
                mofile.edit_connect('weaDat.weaBus', '!weaBus', new_port_a='weaBus')
                # Now remove the unnecessary weaDat.weaBus -> weaBus connection
                mofile.remove_connect('weaDat.weaBus', 'weaBus')

                # add new port connections
                rc_order = self.system_parameters.get_param(
                    "buildings.default.load_model_parameters.rc.order", default=2
                )
                thermal_zone_name = None
                thermal_zone_type = None
                if rc_order == 1:
                    thermal_zone_type = 'OneElement'
                    thermal_zone_name = 'thermalZoneOneElement'
                elif rc_order == 2:
                    thermal_zone_type = 'TwoElements'
                    thermal_zone_name = 'thermalZoneTwoElements'
                elif rc_order == 3:
                    thermal_zone_type = 'ThreeElements'
                    thermal_zone_name = 'thermalZoneThreeElements'
                elif rc_order == 4:
                    thermal_zone_type = 'FourElements'
                    thermal_zone_name = 'thermalZoneFourElements'

                if thermal_zone_name is not None and thermal_zone_type is not None:
                    # add TAir output
                    # This has been moved away from the other insert_component blocks to use thermal_zone_name
                    mofile.insert_component(
                        'Buildings.Controls.OBC.CDL.Interfaces.RealOutput', 'TAir',
                        modifications={
                            'quantity': '"ThermodynamicTemperature"',
                            'unit': '"K"',
                            'displayUnit': '"degC"',
                        },
                        conditional=f'if {thermal_zone_name}.ATot > 0 or {thermal_zone_name}.VAir > 0',
                        string_comment='Room air temperature',
                        annotations=['Placement(transformation(extent={{100,38},{120,58}}))']
                    )
                    mofile.update_component_modifications(
                        f"Buildings.ThermalZones.ReducedOrder.RC.{thermal_zone_type}",
                        thermal_zone_name,
                        {"use_moisture_balance": "use_moisture_balance"}
                    )

                    mofile.update_component_modifications(
                        f"Buildings.ThermalZones.ReducedOrder.RC.{thermal_zone_type}",
                        thermal_zone_name,
                        {"nPorts": "nPorts"}
                    )

                    mofile.add_connect(
                        'port_a', f'{thermal_zone_name}.intGainsConv',
                        annotations=['Line(points={{0,100},{96,100},{96,20},{92,20}}, color={191,0,0})']
                    )

                    mofile.add_connect(
                        f'{thermal_zone_name}.TAir', 'TAir',
                        annotations=[
                            'Line(points={{93,32},{98,32},{98,48},{110,48}}, color={0,0,127})'
                        ]
                    )
                    mofile.add_connect(
                        f'{thermal_zone_name}.TRad', 'TRad',
                        annotations=[
                            'Line(points={{93,28},{98,28},{98,-20},{110,-20}}, color={0,0,127})'
                        ]
                    )
                    mofile.add_connect(
                        f'{thermal_zone_name}.QLat_flow', 'perLatLoa.y',
                        annotations=[
                            'Line(points={{43,4},{40,4},{40,-28},{-40,-28},{-40,-50},{-59,-50}}, color={0, 0,127})'
                        ]
                    )

                    mofile.add_connect(
                        f'{thermal_zone_name}.intGainsRad', 'port_b',
                        annotations=[
                            'Line(points={{92, 24}, {98, 24}, {98, -100}, {40, -100}}, color={191, 0, 0})'
                        ]
                    )
                    mofile.insert_equation_for_loop(
                        index_identifier="i",
                        expression_raw="1:nPorts",
                        loop_body_raw_list=[
                            "connect(ports[i], thermalZoneFourElements.ports[i])",
                            "\tannotation (Line(",
                            "\tpoints={{-18,-102},{-18,-84},{83,-84},{83,-1.95}},",
                            "\tcolor={0,127,255},",
                            "\tsmooth=Smooth.None));",
                        ],
                    )

                # change the name of the modelica model to remove the building id, update in package too!
                original_model_name = mofile.get_name()
                new_model_name = original_model_name.split("_")[1]
                thermal_zone_files.append(new_model_name)
                package.rename_model(original_model_name, new_model_name)
                mofile.set_name(new_model_name)

                # Save as the new filename (without building ID)
                new_filename = os.path.join(
                    scaffold.loads_path.files_dir, f'B{b}/{os.path.basename(f).split("_")[1]}'
                )
                mofile.save_as(new_filename)
                os.remove(f)

            # Now connect all the thermal zone files into the teaser building
            # 1. Need to a map of thermal zone names and instances
            zone_list = []
            for index, tz in enumerate(thermal_zone_files):
                # take /a/file/Meeting.mo -> zone_map["Meeting"] = "meeting"
                tz_process = os.path.splitext(os.path.basename(tz))[0]
                zone_list.append({
                    "index": index,
                    "model_name": tz_process,
                    "instance_name": tz_process.lower(),
                    # process where this will be stored in python otherwise too many {{}}, yes ridiculous.
                    # This needs to result in {{a,b},{x,y}}
                    "placement": f"{{{{{-160 + index * 40},-20}},{{{-140 + index * 40},0}}}}"
                })

                # TODO: Read nominal flows from system parameter file
                template_data = {
                    "thermal_zones": zone_list,
                    "nominal_heat_flow": [10000] * len(zone_list),
                    "nominal_cool_flow": [-10000] * len(zone_list),
                    "load_resources_path": b_modelica_path.resources_relative_dir,
                    "mos_weather": {
                        "mos_weather_filename": mos_weather_filename,
                        "filename": os.path.basename(mos_weather_filename),
                        "path": os.path.dirname(mos_weather_filename),
                    }
                }

            self.run_template(
                teaser_building,
                os.path.join(b_modelica_path.files_dir, "building.mo"),
                project_name=scaffold.project_name,
                model_name=f"B{b}",
                data=template_data
            )

            self.run_template(
                teaser_coupling,
                os.path.join(os.path.join(b_modelica_path.files_dir, "coupling.mo")),
                project_name=scaffold.project_name,
                model_name=f"B{b}",
                data=template_data  # AA added 9/14
            )

            full_model_name = os.path.join(
                scaffold.project_name,
                scaffold.loads_path.files_relative_dir,
                f"B{b}",
                "coupling").replace(os.path.sep, '.')

            self.run_template(
                run_coupling_template,
                os.path.join(os.path.join(b_modelica_path.scripts_dir, "RunTeaserCouplingBuilding.mos")),
                full_model_name=full_model_name,
                model_name="coupling",
            )

            # copy over the required mo files and add the other models to the package order
            mo_files = self.copy_required_mo_files(b_modelica_path.files_dir, within=f'{scaffold.project_name}.Loads')
            for f in mo_files:
                package.add_model(os.path.splitext(os.path.basename(f))[0])
            package.add_model('building')
            package.add_model('coupling')

            # save the updated package.mo and package.order in the Loads.B{} folder
            new_package = PackageParser.new_from_template(
                package.path, f"B{b}", package.order, within=f"{scaffold.project_name}.Loads"
            )
            new_package.save()
            # AA added this 9/24
            if os.path.exists(template_data["mos_weather"]["mos_weather_filename"]):
                shutil.copy(
                    template_data["mos_weather"]["mos_weather_filename"],
                    os.path.join(b_modelica_path.resources_dir, template_data["mos_weather"]["filename"])
                )
            else:
                raise Exception(
                    f"Missing MOS weather file for Spawn: {template_data['mos_weather']['mos_weather_filename']}")
            # end of what AA added 9/24

        # remaining clean up tasks across the entire exported project
        if not keep_original_models:
            shutil.rmtree(os.path.join(scaffold.loads_path.files_dir, "Project"))

        # now create the Loads level package and package.order.
        if not os.path.exists(os.path.join(scaffold.loads_path.files_dir, 'package.mo')):
            load_package = PackageParser.new_from_template(
                scaffold.loads_path.files_dir, "Loads", ["B" + b for b in building_names], within=f"{scaffold.project_name}"
            )
            load_package.save()
        else:
            load_package = PackageParser(os.path.join(scaffold.loads_path.files_dir))
            load_package.add_model(f"B{building_names[0]}")
            load_package.save()

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        pp = PackageParser.new_from_template(
            scaffold.project_path, scaffold.project_name, ["Loads"]
        )
        pp.save()

    def get_modelica_type(self, scaffold):
        building = self.buildings[0]
        building_name = f"B{building['building_id']}"

        return f'{scaffold.project_name}.Loads.{building_name}.building'
