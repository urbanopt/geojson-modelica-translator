# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from modelica_builder.package_parser import PackageParser

from geojson_modelica_translator.jinja_filters import ALL_CUSTOM_FILTERS
from geojson_modelica_translator.model_connectors.couplings.diagram import (
    Diagram
)
from geojson_modelica_translator.model_connectors.load_connectors.load_base import (
    LoadBase
)
from geojson_modelica_translator.scaffold import Scaffold


def render_template(template_name, template_params):
    """Helper for rendering a template

    :param template_name: string, name of template (relative to templates directory)
    :param template_params: dict, template parameters
    :return: string, templated result
    """
    template_dir = Path(__file__).parent / 'templates'
    template_env = Environment(
        loader=FileSystemLoader(searchpath=template_dir),
        undefined=StrictUndefined)
    template_env.filters.update(ALL_CUSTOM_FILTERS)
    template = template_env.get_template(template_name)
    return template.render(template_params)


class District:
    """
    Class for modeling entire district energy systems
    """

    def __init__(self, root_dir, project_name, system_parameters, coupling_graph):
        self._scaffold = Scaffold(root_dir, project_name)
        self.system_parameters = system_parameters
        self._coupling_graph = coupling_graph
        self.district_model_filepath = None
        # Modelica can't handle spaces in project name or path
        if (len(str(root_dir).split()) > 1) or (len(str(project_name).split()) > 1):
            raise SystemExit(
                f"\nModelica does not support spaces in project names or paths. "
                f"You used '{root_dir}' for run path and {project_name} for model project name. "
                "Please update your directory path or model name to not include spaces anywhere.")

    def to_modelica(self):
        """Generate modelica files for the models as well as the modelica file for
        the entire district system.
        """
        # scaffold the project
        self._scaffold.create()
        self.district_model_filepath = Path(self._scaffold.districts_path.files_dir) / 'DistrictEnergySystem.mo'

        # create the root package
        root_package = PackageParser.new_from_template(
            self._scaffold.project_path, self._scaffold.project_name, order=[])
        root_package.save()

        # generate model modelica files
        for model in self._coupling_graph.models:
            model.to_modelica(self._scaffold)

        # construct graph of visual components
        diagram = Diagram(self._coupling_graph)

        district_template_params = {
            "district_within_path": '.'.join([self._scaffold.project_name, 'Districts']),
            "diagram": diagram,
            "couplings": [],
            "models": [],
            "is_ghe_district": self.system_parameters.get_param('$.district_system.fifth_generation.ghe_parameters')
        }
        common_template_params = {
            'globals': {
                'medium_w': 'MediumW',
                'delChiWatTemBui': 'delChiWatTemBui',
                'delChiWatTemDis': 'delChiWatTemDis',
                'delHeaWatTemBui': 'delHeaWatTemBui',
                'delHeaWatTemDis': 'delHeaWatTemDis',
            },
            'graph': self._coupling_graph,
            'sys_params': {
                'district_system': self.system_parameters.get_param('$.district_system'),
                # num_buildings counts the ports required for 5G systems
                "num_buildings": len(self.system_parameters.get_param('$.buildings')),
            }
        }

        # render each coupling
        load_num = 1
        for coupling in self._coupling_graph.couplings:
            template_context = {
                'diagram': diagram.to_dict(coupling.id, is_coupling=True),
            }
            template_context.update(**common_template_params)

            coupling_load = coupling.get_load()
            if coupling_load is not None:
                # read sys params file for the load
                building_sys_params = self.system_parameters.get_param_by_building_id(coupling_load.building_id, '$')
                template_context['sys_params']['building'] = building_sys_params
                # Note which load is being used, so ports connect properly in couplings/5G_templates/ConnectStatements
                template_context['sys_params']['load_num'] = load_num
                load_num += 1

            templated_result = coupling.render_templates(template_context)
            district_template_params['couplings'].append({
                'id': coupling.id,
                'component_definitions': templated_result['component_definitions'],
                'connect_statements': templated_result['connect_statements'],
                'coupling_definitions_template_path': templated_result['component_definitions_template_path'],
                'connect_statements_template_path': templated_result['connect_statements_template_path'],
            })

        # render each model instance
        for model in self._coupling_graph.models:
            template_params = {
                'model': model.to_dict(self._scaffold),
                'couplings': self._coupling_graph.couplings_by_type(model.id),
                'diagram': diagram.to_dict(model.id, is_coupling=False),
            }
            template_params.update(**common_template_params)

            if issubclass(type(model), LoadBase):
                building_sys_params = self.system_parameters.get_param_by_building_id(model.building_id, '$')
                template_params['sys_params']['building'] = building_sys_params

            templated_instance, instance_template_path = model.render_instance(template_params)
            district_template_params['models'].append({
                'id': model.id,
                'instance_template_path': instance_template_path,
                'instance': templated_instance
            })

        # render the full district file
        if 'fifth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem5G.mot', district_template_params)
        elif 'fourth_generation' in common_template_params['sys_params']['district_system']:
            final_result = render_template('DistrictEnergySystem.mot', district_template_params)
        with open(self.district_model_filepath, 'w') as f:
            f.write(final_result)

        districts_package = PackageParser.new_from_template(self._scaffold.districts_path.files_dir, "Districts", [
            'DistrictEnergySystem'], within=f"{self._scaffold.project_name}")
        districts_package.save()

        root_package = PackageParser(self._scaffold.project_path)
        if 'Districts' not in root_package.order:
            root_package.add_model('Districts')
            root_package.save()
