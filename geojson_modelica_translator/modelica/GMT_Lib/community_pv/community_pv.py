from pathlib import Path

# from geojson_modelica_translator.model_connectors.districts.district import (
#     render_template
# )
from geojson_modelica_translator.model_connectors.model_base import ModelBase

# from geojson_modelica_translator.system_parameters.system_parameters import (
#     SystemParameters
# )


class CommunityPV(ModelBase):
    def to_modelica(sys_params):
        # TODO: Do we need a way to identify pv arrays with different specs? microgrid_example.json 231:246
        # This summation is almost certainly wrong.
        community_pv_params = sys_params.get_param("$.photovoltaic_panels")
        total_net_pv_surface_area_meters = 0
        for _ in community_pv_params:
            total_net_pv_surface_area_meters += ["net_surface_area_m2"]

        pv_template_params = {
            'net_surface_area_meters': sys_params.get_param(
                    "$.photovoltaic_panels.default.central_heating_plant_parameters.chp_installed"
                ),
            }
    # render template to final modelica file
        pv_template = self.template_env.get_template("PVPanels.mot")
            self.run_template(
                template=pv_template,
                save_file_name=Path(scaffold.pv_path.files_dir) / "PVPanels.mo",
                project_name=scaffold.project_name,
                data=pv_template_params
            )
