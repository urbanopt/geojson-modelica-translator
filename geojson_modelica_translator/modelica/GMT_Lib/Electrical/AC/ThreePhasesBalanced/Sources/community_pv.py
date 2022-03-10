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
                f'net_surface_area_m2{index}': f'{pvarray}.net_surface_area',
                }
        self.to_modelica(output_dir, 'PVPanels', pv_template_params)

        # # render template to final modelica file
        #     pv_template = self.template_env.get_template("PVPanels.mot")
        #     self.run_template(
        #         template=pv_template,
        #         save_file_name=output_dir / f"PVPanels_{index}.mo",
        #         project_name=output_dir.stem,
        #         data=pv_template_params
        #     )
