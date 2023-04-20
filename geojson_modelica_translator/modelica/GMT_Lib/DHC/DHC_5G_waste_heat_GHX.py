import shutil
from pathlib import Path

from geojson_modelica_translator.modelica.input_parser import PackageParser
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

        # 1: grab all of the time series files and place them in the proper location
        for building_load_file in self.system_parameters.get_param("$.buildings[?load_model=time_series].load_model_parameters.time_series.filepath"):
            shutil.copy(building_load_file, scaffold.districts_path.resources_dir)

            # 2: add the path to the param data with Modelica friendly path names
            template_data['building_load_files'].append(f"modelica://{project_name}/{scaffold.districts_path.resources_relative_dir}/{Path(building_load_file).name}")

        # 3: generate the modelica files from the template
        self.to_modelica(output_dir=Path(scaffold.districts_path.files_dir),
                         model_name='DHC_5G_waste_heat_GHX',
                         param_data=template_data,
                         save_file_name='district.mo',
                         generate_package=True)

        # 4. save the root package.mo
        package.save()
