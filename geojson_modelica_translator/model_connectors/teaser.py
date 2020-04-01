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

import glob
import os
import shutil

from geojson_modelica_translator.model_connectors.base import \
    Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import (
    InputParser,
    PackageParser
)
from geojson_modelica_translator.utils import ModelicaPath, copytree
from teaser.project import Project


class TeaserConnector(model_connector_base):
    def __init__(self, system_parameters):
        super().__init__(system_parameters)

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.

        :param urbanopt_building: an urbanopt_building
        """
        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        # note-1(Yanfei): any building/district geojson file needs to have the following properties.
        # note-2(Yanfei): there is a need to clean the building/district geojson file, before making into modelica
        if mapper is None:
            number_stories = urbanopt_building.feature.properties["number_of_stories"]
            # print("Jing: ", urbanopt_building.feature.properties.keys())
            number_stories_above_ground = urbanopt_building.feature.properties["number_of_stories_above_ground"]
            self.buildings.append(
                {
                    "area": urbanopt_building.feature.properties["floor_area"] * 0.092936,  # ft2 -> m2
                    "building_id": urbanopt_building.feature.properties["id"],
                    "building_type": urbanopt_building.feature.properties["building_type"],
                    "floor_height": urbanopt_building.feature.properties["floor_height"],  # ft -> m
                    "num_stories": urbanopt_building.feature.properties["number_of_stories"],
                    "num_stories_below_grade": number_stories - number_stories_above_ground,
                    "year_built": urbanopt_building.feature.properties["year_built"],

                }
            )

    def lookup_building_type(self, building_type):
        if "office" in building_type.lower():
            return "office"
        else:
            # TODO: define these mappings 'office', 'institute', 'institute4', institute8'
            return "office"

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
            * Remove weaDat and rely on weaBus

        :param project_name: string, name of the project which will be used to set the package.mo file
        :param root_building_dir: string, where the project will be ultimately saved
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :return: None
        """
        for b in building_names:
            # create a list of strings that we need to replace in all the file as we go along
            string_replace_list = []

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
                        f"Loads/{b_modelica_path.resources_relative_dir}/{new_file_name}",
                    )
                )

            # process each of the building models
            mo_files = glob.glob(os.path.join(scaffold.loads_path.files_dir, f"B{b}/*.mo"))
            for f in mo_files:
                # ignore the package.mo file
                if os.path.basename(f) == "package.mo":
                    continue

                mofile = InputParser(f)

                # previous paths and replace with the new one.
                # Make sure to update the names of any resources as well.
                mofile.replace_within_string(f"{scaffold.project_name}.Loads.B{b}")

                # remove ReaderTMY3
                mofile.remove_object("ReaderTMY3")

                # updating path to internal loads
                for s in string_replace_list:
                    mofile.replace_model_string("Modelica.Blocks.Sources.CombiTimeTable", "internalGains", s[0], s[1])

                # add heat port
                data = [
                    "annotation (Placement(transformation(extent={{-10,90},{10,110}}), "
                    "iconTransformation(extent={{-10,90},{10,110}})));"
                ]
                mofile.add_model_object(
                    "Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a", "port_a", data,
                )

                # add TAir output
                # TODO: read in the object by name -- parse the parenthetic content
                instance = 'TAir(\n    quantity="ThermodynamicTemperature", unit="K", displayUnit="degC")'
                data = [
                    '"Room air temperature"',
                    "annotation (Placement(transformation(extent={{100,-10},{120,10}})));",
                ]
                mofile.add_model_object(
                    "Buildings.Controls.OBC.CDL.Interfaces.RealOutput", instance, data
                )

                # All existing weaDat.weaBus connections need to be updated to simply weaBus
                mofile.replace_connect_string('weaDat.weaBus', None, 'weaBus', None, True)
                # Now remove the redundant weaBus -> weaBus connection
                mofile.remove_connect_string('weaBus', 'weaBus')

                # add new port connections
                if self.system_parameters.get_param(
                        "buildings.default.load_model_parameters.rc.order", default=2) == 1:
                    data = "annotation (Line(points={{0,100},{96,100},{96,20},{92,20}}, color={191,0,0}))"
                    mofile.add_connect("port_a", "thermalZoneOneElement.intGainsConv", data)

                    data = "annotation (Line(points={{93,32},{98,32},{98,0},{110,0}}, color={0,0,127}))"
                    mofile.add_connect("thermalZoneOneElement.TAir", "TAir", data)
                elif self.system_parameters.get_param(
                        "buildings.default.load_model_parameters.rc.order", default=2) == 2:
                    data = "annotation (Line(points={{0,100},{96,100},{96,20},{92,20}}, color={191,0,0}))"
                    mofile.add_connect("port_a", "thermalZoneTwoElements.intGainsConv", data)

                    data = "annotation (Line(points={{93,32},{98,32},{98,0},{110,0}}, color={0,0,127}))"
                    mofile.add_connect("thermalZoneTwoElements.TAir", "TAir", data)
                elif self.system_parameters.get_param(
                        "buildings.default.load_model_parameters.rc.order", default=2) == 4:
                    data = "annotation (Line(points={{0,100},{96,100},{96,20},{92,20}}, color={191,0,0}))"
                    mofile.add_connect("port_a", "thermalZoneFourElements.intGainsConv", data)

                    data = "annotation (Line(points={{93,32},{98,32},{98,0},{110,0}}, color={0,0,127}))"
                    mofile.add_connect("thermalZoneFourElements.TAir", "TAir", data)

                # change the name of the modelica model to remove the building id, update in package too!
                new_model_name = mofile.model["name"].split("_")[1]
                package.rename_model(mofile.model["name"], new_model_name)
                mofile.model["name"] = new_model_name

                # Save as the new filename (without building ID)
                new_filename = os.path.join(
                    scaffold.loads_path.files_dir, f'B{b}/{os.path.basename(f).split("_")[1]}'
                )
                mofile.save_as(new_filename)
                os.remove(f)

            # save the updated package.mo and package.order.
            new_package = PackageParser.new_from_template(
                package.path, f"B{b}", package.order, within=f"{scaffold.project_name}.Loads"
            )
            new_package.save()

        # remaining clean up tasks across the entire exported project
        if not keep_original_models:
            shutil.rmtree(os.path.join(scaffold.loads_path.files_dir, "Project"))

        # now create the Loads level package. This (for now) will create the package without considering any existing
        # files in the Loads directory.
        # add in the silly 'B' before the building names
        package = PackageParser.new_from_template(
            scaffold.loads_path.files_dir,
            "Loads", ["B" + b for b in building_names],
            within=f"{scaffold.project_name}"
        )
        package.save()
