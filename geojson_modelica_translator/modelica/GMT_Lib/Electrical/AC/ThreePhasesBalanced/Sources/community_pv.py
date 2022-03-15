from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class CommunityPV(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        community_pv_params = self.system_parameters.get_param("$.photovoltaic_panels")
        # There can be multiple community pv arrays so we need to loop over them
        for index, pvarray in enumerate(community_pv_params):
            pv_params = {
                'net_surface_area_m2': pvarray["net_surface_area"],
                'nominal_voltage_V': pvarray["nominal_voltage"],
                'surface_azimuth_deg': pvarray["surface_azimuth"],
                'surface_tilt_deg': pvarray["surface_tilt"],
                'model_name': f"PVPanels{index}",
            }
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='PVPanels', param_data=pv_params, iteration=index)
