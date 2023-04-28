from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class Capacitor(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        cap_params = self.system_parameters.get_param("$.capacitor_banks")
        # There can be multiple capacitors so we need to loop over them
        for index, capacitor in enumerate(cap_params):
            cap_params = {
                'nominal_capacity': capacitor["nominal_capacity"],
                'model_name': f"Capacitor{index}",
            }
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='Capacitor', param_data=cap_params, iteration=index)
