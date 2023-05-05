import shutil
from pathlib import Path

from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.modelica.modelica_mos_file import ModelicaMOS
from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase
from geojson_modelica_translator.scaffold import Scaffold


class DHC5GWasteHeatAndGHX(SimpleGMTBase):
    """Generates a full Modelica package with the DHC 5G waste heat and GHX model."""

    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path, project_name: str) -> None:
        """This is a bit past being a simple template as it is exporting an entire scaffolded package
        that can be loaded and simulated in Modelica. The scaffold is very specific to DES.

        Args:
            output_dir (Path): directory to save the package to (without the project name)
            project_name (str, optional): The name of the project which is used in the Scaffold object.
        """
        template_data = {
            'project_name': project_name,
            'save_file_name': 'district',
            'building_load_files': []
        }

        # create the directory structure
        scaffold = Scaffold(output_dir, project_name=project_name)
        scaffold.create(ignore_paths=['Loads', 'Networks', 'Plants', 'Substations'])

        # create the root package
        package = PackageParser.new_from_template(scaffold.project_path, project_name, order=[])
        package.add_model('Districts')

        # create the district package with the template_data from above
        files_to_copy = []

        # 1: grab all of the time series files and place them in the proper location
        for building in self.system_parameters.get_param("$.buildings[?load_model=time_series]"):
            building_load_file = Path(building['load_model_parameters']['time_series']['filepath'])

            files_to_copy.append({
                "orig_file": building_load_file,
                "geojson_id": building['geojson_id'],
                "save_path": f"{scaffold.districts_path.resources_dir}/{building['geojson_id']}",
                "save_filename": building_load_file.name
            })

        # 2: Copy the files to the appropriate location and ensure uniqueness by putting into a unique directory
        #    (since openstudio creates all files with modelica.mos)
        for file_to_copy in files_to_copy:
            # create the path if it doesn't exist
            Path(file_to_copy['save_path']).mkdir(parents=True, exist_ok=True)
            save_filename = f"{file_to_copy['save_path']}/{file_to_copy['save_filename']}"
            shutil.copy(file_to_copy['orig_file'], save_filename)

            # 3: If the file is an MOS file, and it has the Peak water heating load set to zero, then set it to a minimum value
            mos_file = ModelicaMOS(save_filename)
            peak_water = mos_file.retrieve_header_variable_value('Peak water heating load', cast_type=float)
            if peak_water == 0:
                peak_heat = mos_file.retrieve_header_variable_value('Peak space heating load', cast_type=float)
                peak_swh = max(peak_heat / 10, 5000)

                mos_file.replace_header_variable_value('Peak water heating load', peak_swh)
                mos_file.save()

            # 4: add the path to the param data with Modelica friendly path names
            rel_path_name = f"{project_name}/{scaffold.districts_path.resources_relative_dir}/{file_to_copy['geojson_id']}/{file_to_copy['save_filename']}"
            template_data['building_load_files'].append(f"modelica://{rel_path_name}")  # type: ignore

        # 5: generate the modelica files from the template
        self.to_modelica(output_dir=Path(scaffold.districts_path.files_dir),
                         model_name='DHC_5G_waste_heat_GHX',
                         param_data=template_data,
                         save_file_name='district.mo',
                         generate_package=True)

        # 4: save the root package.mo
        package.save()
