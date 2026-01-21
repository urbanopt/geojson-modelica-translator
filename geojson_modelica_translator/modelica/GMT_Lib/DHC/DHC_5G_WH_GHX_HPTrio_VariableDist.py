import shutil
from pathlib import Path

from modelica_builder.modelica_mos_file import ModelicaMOS

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase
from geojson_modelica_translator.scaffold import Scaffold


class DHC5GWasteHeatGHXwithHPTrioVariableDist(SimpleGMTBase):
    """Generates a full Modelica package with the DHC 5G waste heat and GHX model with a
    controlled variable speed distribution pump.
    """

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
        template_data = {"project_name": project_name, "save_file_name": "district", "building_load_files": []}

        # create the directory structure
        scaffold = Scaffold(output_dir, project_name=project_name)
        scaffold.create(ignore_paths=["Networks", "Plants", "Substations"])

        # Verify districts_path was created
        if scaffold.districts_path is None:
            raise RuntimeError("Districts path must be created by scaffold")
        districts_path = scaffold.districts_path  # Type narrowing for mypy

        if scaffold.loads_path is None:
            raise RuntimeError("Loads path must be created by scaffold")
        loads_path = scaffold.loads_path  # Type narrowing for mypy

        # create the district package with the template_data from above
        files_to_copy = []

        template_data["pressure_drop_per_meter"] = self.system_parameters.get_param(
            "$.district_system.fifth_generation.horizontal_piping_parameters.pressure_drop_per_meter"
        )

        # 1: Grab all of the time series files and place them in the proper location
        #    If this is a dict, then there is only one building
        time_series = self.system_parameters.get_param("$.buildings[?load_model=time_series]")
        if isinstance(time_series, dict):
            time_series = [time_series]

        for building in time_series:
            building_load_file = Path(building["load_model_parameters"]["time_series"]["filepath"])
            files_to_copy.append(
                {
                    "orig_file": building_load_file,
                    "geojson_id": building["geojson_id"],
                    "save_path": f"{districts_path.resources_dir}/{building['geojson_id']}",
                    "save_filename": building_load_file.name,
                }
            )

        # 2: Copy the files to the appropriate location and ensure uniqueness by putting into a unique directory
        #    (since OpenStudio creates all files with modelica.mos)
        total_heating_load = 0
        total_cooling_load = 0
        total_swh_load = 0
        for file_to_copy in files_to_copy:
            # create the path if it doesn't exist
            Path(file_to_copy["save_path"]).mkdir(parents=True, exist_ok=True)
            save_filename = f"{file_to_copy['save_path']}/{file_to_copy['save_filename']}"
            shutil.copy(file_to_copy["orig_file"], save_filename)

            # 3: If the file is an MOS file and Peak water heating load is set to zero, then set it to a minimum value
            #    Also, store the total heating, cooling, and water loads which will be used for sizing.
            mos_file = ModelicaMOS(save_filename)
            total_heating_load += mos_file.retrieve_header_variable_value("Peak space heating load", cast_type=float)
            total_cooling_load += mos_file.retrieve_header_variable_value("Peak space cooling load", cast_type=float)
            peak_water = mos_file.retrieve_header_variable_value("Peak water heating load", cast_type=float)
            total_swh_load += peak_water
            if peak_water == 0:
                peak_heat = mos_file.retrieve_header_variable_value("Peak space heating load", cast_type=float)
                peak_swh = max(peak_heat / 10, 5000)

                mos_file.replace_header_variable_value("Peak water heating load", peak_swh)
                mos_file.save()

            # 4: Add the path to the param data with Modelica friendly path names
            rel_path_name = f"{project_name}/{districts_path.resources_relative_dir}/{file_to_copy['geojson_id']}/{file_to_copy['save_filename']}"  # noqa: E501
            template_data["building_load_files"].append(f"modelica://{rel_path_name}")  # type: ignore[attr-defined]

        # 5: Calculate the mass flow rates (kg/s) for the heating and cooling
        #    networks peak load (in Watts).
        #    (assuming 5C delta T [since 5G] and 4.18 Cp (kJ/kgK)). Add 1.5x
        #    the peak for oversizing
        delta_t = 5
        heating_flow_rate = 1.5 * total_heating_load / (1000 * delta_t * 4.18)
        cooling_flow_rate = 1.5 * total_cooling_load / (1000 * delta_t * 4.18)
        swh_flow_rate = 1.5 * total_swh_load / (1000 * delta_t * 4.18)

        template_data["max_flow_rate"] = round(max(heating_flow_rate, cooling_flow_rate, swh_flow_rate), 3)  # type: ignore[arg-type]

        n_buildings = len(template_data["building_load_files"])
        template_data["lDis"] = self.build_string("lDis = {", "0.5, ", n_buildings)
        template_data["lCon"] = self.build_string("lCon = {", "0.5, ", n_buildings)

        # 6: Generate the modelica files from the template
        self.to_modelica(
            output_dir=Path(str(districts_path.files_dir)),
            model_name="DHC_5G_WH_GHX_HPTrio_VariableDist",
            param_data=template_data,
            save_file_name="district.mo",
            generate_package=True,
            partial_files={"DHC_5G_partial": "PartialSeries"},
        )

        # 7: Now generate the building load files, which are one per load
        for building_load_path in template_data["building_load_files"]:
            building_template_data = {"project_name": project_name, "building_load_file": building_load_path}
            self.to_modelica(
                output_dir=Path(str(loads_path.files_dir)),
                model_name="Components/Loads/buildingHPTrio",
                param_data=building_template_data,
                save_file_name="buildingHPTrio.mo",
                generate_package=True,
            )

            # TimeSeriesBuilding
            self.to_modelica(
                output_dir=Path(str(loads_path.files_dir)),
                model_name="Components/Loads/TimeSeriesBuilding",
                param_data=building_template_data,
                save_file_name="TimeSeriesBuilding.mo",
                generate_package=False,
            )
        # 8: Copy over the Components/Loads/ETS files which need mild templating.
        self.to_modelica(
            output_dir=Path(str(loads_path.files_dir)),
            model_name="Components/Loads/ETS/HeatPumpCooling",
            param_data={"project_name": project_name},
            save_file_name="ETS/HeatPumpCooling.mo",
            generate_package=False,
        )
        self.to_modelica(
            output_dir=Path(str(loads_path.files_dir)),
            model_name="Components/Loads/ETS/HeatPumpTrio",
            param_data={"project_name": project_name},
            save_file_name="ETS/HeatPumpTrio.mo",
            generate_package=False,
        )
        self.to_modelica(
            output_dir=Path(str(loads_path.files_dir)),
            model_name="Components/Loads/ETS/PartialHeatPumpCooling",
            param_data={"project_name": project_name},
            save_file_name="ETS/PartialHeatPumpCooling.mo",
            generate_package=False,
        )

        # 8: Add the models to the packages and save
        scaffold.package.districts.add_model("PartialSeries", create_subpackage=False)
        scaffold.package.districts.add_model("district", create_subpackage=False)

        scaffold.package.loads.add_model("TimeSeriesBuilding", create_subpackage=False)
        scaffold.package.loads.add_model("buildingHPTrio", create_subpackage=False)

        scaffold.package.loads.ets.add_model("HeatPumpTrio", create_subpackage=False)
        scaffold.package.loads.ets.add_model("HeatPumpCooling", create_subpackage=False)
        scaffold.package.loads.ets.add_model("PartialHeatPumpCooling", create_subpackage=False)
        scaffold.package.save()

    def build_string(self, base_text: str, value: str, iterations: int) -> str:
        """Builds a string with a comma separated list of values.

        This is used to build 5G districts with arbitrary number of buildings.
        It's ugly because of the Jinja/Modelica templating system.
        This is a bit of a hack but it works.

        Example output: lDis = { 0.5, 0.5, 0.5 }

        Args:
            base_text (str): The text to start the string with.
            value (str): The value to add multiple times.
            iterations (int): The number of values to add to the string."""
        text = f"{base_text} {value * iterations}"
        return text.removesuffix(", ") + " }"
