from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt import SimpleGMT


class CommunityPV(SimpleGMT):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        community_pv_params = self.system_parameters.get_param("$.photovoltaic_panels")
        # There can be multiple community pv arrays so we need to loop over them
        for index, pvarray in enumerate(community_pv_params):
            pv_template_params = {
                f'array_{index}_net_surface_area_m2': f'{pvarray}.net_surface_area',
                f'array_{index}_nominal_voltage_V': f'{pvarray}.nominal_voltage',
                f'array_{index}_surface_azimuth_deg': f'{pvarray}.surface_azimuth',
                f'array_{index}_surface_tilt_deg': f'{pvarray}.surface_tilt',
            }
        # render template to final modelica file
        self.to_modelica(output_dir=output_dir, model_name='PVPanels', param_data=pv_template_params)
