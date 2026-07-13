# :copyright (c) URBANopt, Alliance for Energy Innovation, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import logging
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from geojson_modelica_translator.external_package_utils import (
    get_num_buildings_in_loop_order,
    load_loop_order,
    normalize_package_orders_recursively,
    set_loop_order_data_in_template_params,
    set_minimum_dhw_load,
)
from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.couplings.diagram import Diagram
from geojson_modelica_translator.model_connectors.energy_transfer_systems.heat_pump_ets import HeatPumpETS
from geojson_modelica_translator.model_connectors.load_connectors.load_base import LoadBase
from geojson_modelica_translator.model_connectors.load_connectors.steam_building import SteamBuilding
from geojson_modelica_translator.model_connectors.plants.steam_boiler import SteamPlant
from geojson_modelica_translator.scaffold import Scaffold

logger = logging.getLogger(__name__)


def render_template(template_name, template_params):
    """Helper for rendering a template

    :param template_name: string, name of template (relative to templates directory)
    :param template_params: dict, template parameters
    :return: string, templated result
    """
    template_dir = Path(__file__).parent / "templates"
    template_env = Environment(loader=FileSystemLoader(searchpath=template_dir), undefined=StrictUndefined)
    template_env.filters.update(ALL_CUSTOM_FILTERS)
    template = template_env.get_template(template_name)
    return template.render(template_params)


class District:
    """Class for modeling entire district energy systems"""

    def __init__(self, root_dir, project_name, system_parameters, coupling_graph, geojson_file=None):
        self._scaffold = Scaffold(root_dir, project_name)
        self.system_parameters = system_parameters  # SystemParameters object
        self.gj = geojson_file  # UrbanOptGeoJson object
        self._coupling_graph = coupling_graph  # CouplingGraph object
        self.district_model_filepath = None
        # Modelica can't handle spaces in project name or path
        if (len(str(root_dir).split()) > 1) or (len(str(project_name).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{root_dir}' for run path and {project_name} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere."
            )

    def to_modelica(self):
        """Generate modelica files for the models as well as the modelica file for the entire district system."""

        # scaffold the project
        self._scaffold.create()
        self.district_model_filepath = Path(self._scaffold.districts_path.files_dir) / "DistrictEnergySystem.mo"

        district_system_params = self.system_parameters.get_param("$.district_system")

        # 1st-generation (steam) district systems use a simplified generation path
        if "first_generation" in district_system_params:
            self._to_modelica_first_generation(district_system_params)
            return

        # generate model modelica files
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        # construct graph of visual components
        diagram = Diagram(self._coupling_graph)

        district_system_params = self.system_parameters.get_param("$.district_system")

        district_template_params = {
            "district_within_path": ".".join([self._scaffold.project_name, "Districts"]),
            "diagram": diagram,
            "couplings": [],
            "models": [],
            "is_ghe_district": self.system_parameters.get_param("$.district_system.fifth_generation.ghe_parameters"),
            "fluid": {
                "fluid_name": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.fluid.fluid_name"
                ),
                "concentration_percent": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.fluid.concentration_percent"
                ),
                "temperature": self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.fluid.temperature"
                ),
            },
        }

        # temporary number of buildings (unused for 4G but just a placeholder)
        num_buildings = len(self.system_parameters.get_param("$.buildings"))

        common_template_params = {
            "globals": {
                "medium_w": "MediumW",
                "delChiWatTemBui": "delChiWatTemBui",
                "delChiWatTemDis": "delChiWatTemDis",
                "delHeaWatTemBui": "delHeaWatTemBui",
                "delHeaWatTemDis": "delHeaWatTemDis",
                "project_name": self._scaffold.project_name,
            },
            "graph": self._coupling_graph,
            "sys_params": {
                "district_system": district_system_params,
                # num_buildings counts the ports required for 5G systems
                "num_buildings": num_buildings,
            },
        }

        if "fifth_generation" in district_system_params and self.gj:
            if district_template_params["is_ghe_district"]:
                # determine the maximum borefield flow rate in the district
                borefields = self.system_parameters.get_param(
                    "$.district_system.fifth_generation.ghe_parameters.borefields"
                )
                number_of_boreholes_dict = {}
                for borefield in borefields:
                    ghe_id = borefield["ghe_id"]
                    if "pre_designed_borefield" not in borefield:
                        num_boreholes = self.system_parameters.get_param_by_id(ghe_id, "$.*.number_of_boreholes")
                    else:
                        num_boreholes = len(borefield["pre_designed_borefield"]["borehole_x_coordinates"])
                    number_of_boreholes_dict[ghe_id] = num_boreholes
                common_template_params["number_of_boreholes"] = number_of_boreholes_dict
                # Allow 5G systems that have ghe_parameters defined but no borefields listed.
                # A zero default avoids crashing on max([]) and keeps template math deterministic.
                common_template_params["max_number_of_boreholes"] = max(number_of_boreholes_dict.values(), default=0)

            # load loop order info from ThermalNetwork or generated fallback
            loop_order = load_loop_order(self.system_parameters.filename)
            # calculate number of connected buildings in loop order for 5G systems & reassign
            common_template_params["sys_params"]["num_buildings"] = get_num_buildings_in_loop_order(loop_order)

            # TODO: determine loop order some other way, so thermal networks without GHEs can have horizontal piping
            # or: Ensure TN is used for all networks, so loop order is generated that way.
            feature_properties = self.gj.get_feature("$.features.[*].properties")
            set_loop_order_data_in_template_params(common_template_params, feature_properties, loop_order)

        if "fifth_generation" in district_system_params:
            district_template_params["pressure_drop_per_meter"] = district_system_params["fifth_generation"][
                "horizontal_piping_parameters"
            ]["pressure_drop_per_meter"]

            # Build the heat pump ETS model to ensure chillers are available to 5G loads
            ets_templates_dir_path = Path(__file__).parent.parent / "energy_transfer_systems" / "templates"
            heat_pump_ets = HeatPumpETS(self.system_parameters, ets_templates_dir_path)
            heat_pump_ets.to_modelica(self._scaffold)
        else:
            # Remove the ETS dir which isn't used in non-5G systems
            ets_path = Path(self._scaffold.heat_pump_ets_path.files_dir)
            if ets_path.exists():
                shutil.rmtree(ets_path)
            # Also remove ETS from the Loads package order
            if hasattr(self._scaffold.package, "loads") and "ETS" in self._scaffold.package.loads.order:
                self._scaffold.package.loads.order.remove("ETS")
            if hasattr(self._scaffold.package.loads, "_subpackages"):
                self._scaffold.package.loads._subpackages.pop("ets", None)
            elif hasattr(self._scaffold.package.loads, "ets"):
                delattr(self._scaffold.package.loads, "ets")

        # render each coupling
        load_num = 1
        for coupling in self._coupling_graph.couplings:
            template_context = {
                "diagram": diagram.to_dict(coupling.id, is_coupling=True),
            }
            template_context.update(**common_template_params)

            coupling_load = coupling.get_load()
            if coupling_load is not None:
                # read sys params file for the load
                building_sys_params = self.system_parameters.get_param_by_id(coupling_load.building_id, "$")
                template_context["sys_params"]["building"] = building_sys_params
                # Note which load is being used, so ports connect properly in couplings/5G_templates/*/ConnectStatements
                template_context["sys_params"]["load_num"] = load_num
                load_num += 1

            templated_result = coupling.render_templates(template_context)
            district_template_params["couplings"].append(
                {
                    "id": coupling.id,
                    "component_definitions": templated_result["component_definitions"],
                    "connect_statements": templated_result["connect_statements"],
                    "coupling_definitions_template_path": templated_result["component_definitions_template_path"],
                    "connect_statements_template_path": templated_result["connect_statements_template_path"],
                }
            )

        # render each model instance
        for model in self._coupling_graph.models:
            template_params = {
                "model": model.to_dict(self._scaffold),
                "couplings": self._coupling_graph.couplings_by_type(model.id),
                "diagram": diagram.to_dict(model.id, is_coupling=False),
            }
            template_params.update(**common_template_params)

            if issubclass(type(model), LoadBase):
                building_sys_params = self.system_parameters.get_param_by_id(model.building_id, "$")
                template_params["sys_params"]["building"] = building_sys_params

            templated_instance, instance_template_path = model.render_instance(template_params)
            district_template_params["models"].append(
                {"id": model.id, "instance_template_path": instance_template_path, "instance": templated_instance}
            )

        # render the full district file
        if "fifth_generation" in common_template_params["sys_params"]["district_system"]:
            final_result = render_template("DistrictEnergySystem5G.mot", district_template_params)
        elif "fourth_generation" in common_template_params["sys_params"]["district_system"]:
            final_result = render_template("DistrictEnergySystem4G.mot", district_template_params)
        else:
            raise ValueError(
                "No recognized district generation found in district_system params. "
                "Expected 'fourth_generation' or 'fifth_generation' for the main to_modelica path."
            )
        with open(self.district_model_filepath, "w") as f:
            f.write(final_result)

        # Add DistrictEnergySystem to Districts package using scaffold's PackageParser
        self._scaffold.package.districts.add_model("DistrictEnergySystem", create_subpackage=False)
        self._scaffold.save()

        # Enforce minimum DHW load in Modelica model
        data_dir = Path(self._scaffold.project_path) / "Loads" / "Resources" / "Data"
        set_minimum_dhw_load(data_dir)

        # Ensure package.order files include all generated local models/subpackages.
        normalize_package_orders_recursively(self._scaffold.project_path)

    def _to_modelica_first_generation(self, district_system_params):
        """Generate modelica files for a 1st-generation (steam) district system.

        1st-generation steam systems generate all coupled models (loads, ETS, networks, plant)
        as explicit components in the district with proper instantiations and connections,
        similar to the 5G generation path.

        :param district_system_params: dict, district_system section of sys_params
        """
        steam_plant = next((m for m in self._coupling_graph.models if isinstance(m, SteamPlant)), None)
        if steam_plant is None:
            raise ValueError("First-generation district_system requires a SteamPlant in the coupling graph.")

        if self.gj is None:
            raise ValueError(
                "First-generation district_system requires a geojson_file so that per-building steam "
                "loads (Loads.<building>.building) can be generated with their time-series load files."
            )

        # Generate all models in the coupling graph (networks, plant, etc.)
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        # Generate a GMT-wrapped steam building (with integrated ETS) for each building. Each wraps
        # Buildings.DHC.Loads.Steam.BuildingTimeSeriesAtETS and reads its own time-series load file.
        steam_buildings = []
        for index, geojson_load in enumerate(self.gj.buildings, start=1):
            steam_building = SteamBuilding(self.system_parameters, geojson_load)
            steam_building.to_modelica(self._scaffold)
            steam_buildings.append(
                {
                    "instance": f"bld{index}",
                    "type": steam_building.get_modelica_type(self._scaffold),
                    "name": steam_building.building_name,
                }
            )

        # Build model lists for template generation (similar to 5G)
        plants = [m for m in self._coupling_graph.models if isinstance(m, SteamPlant)]

        # Collect the central steam plant parameters that drive the decomposed
        # plant -> distribution -> buildings steam components in the district model.
        steam_params_path = "$.district_system.first_generation.central_steam_plant_parameters"
        steam = {
            "steam_pressure_setpoint": self.system_parameters.get_param(
                f"{steam_params_path}.steam_pressure_setpoint"
            ),
            "reduced_pressure_setpoint": self.system_parameters.get_param(
                f"{steam_params_path}.reduced_pressure_setpoint"
            ),
            "condensate_pressure_drop_nominal": self.system_parameters.get_param(
                f"{steam_params_path}.condensate_pressure_drop_nominal"
            ),
            "number_of_loads": len(steam_buildings),
            # Plant controller tuning and sizing (defaults match the MBL steam example)
            "boiler_control_gain": self.system_parameters.get_param(f"{steam_params_path}.boiler_control_gain") or 600,
            "boiler_control_time_constant": self.system_parameters.get_param(
                f"{steam_params_path}.boiler_control_time_constant"
            )
            or 120,
            "pump_control_gain": self.system_parameters.get_param(f"{steam_params_path}.pump_control_gain") or 200,
            "pump_control_time_constant": self.system_parameters.get_param(
                f"{steam_params_path}.pump_control_time_constant"
            )
            or 1000,
            "boiler_drum_volume": self.system_parameters.get_param(f"{steam_params_path}.boiler_drum_volume") or 3,
            "boiler_capacity_scale": self.system_parameters.get_param(f"{steam_params_path}.boiler_capacity_scale")
            or 1.25,
            "distribution_flow_safety_factor": self.system_parameters.get_param(
                f"{steam_params_path}.distribution_flow_safety_factor"
            )
            or 1.2,
        }

        # Generate the district energy system model with explicit instantiations
        first_gen_params = {
            "district_within_path": ".".join([self._scaffold.project_name, "Districts"]),
            "project_name": self._scaffold.project_name,
            "plants": plants,
            "steam_buildings": steam_buildings,
            "couplings": self._coupling_graph.couplings,
            "steam": steam,
            "globals": {
                "project_name": self._scaffold.project_name,
            },
        }
        final_result = render_template("DistrictEnergySystem1G.mot", first_gen_params)
        with open(self.district_model_filepath, "w") as f:
            f.write(final_result)

        # Add DistrictEnergySystem to Districts package using scaffold's PackageParser
        self._scaffold.package.districts.add_model("DistrictEnergySystem", create_subpackage=False)
        self._scaffold.save()

        # Ensure package.order files include all generated local models/subpackages.
        normalize_package_orders_recursively(self._scaffold.project_path)
