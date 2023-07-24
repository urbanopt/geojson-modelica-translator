from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class ACACTransformer(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        transformer_params = self.system_parameters.get_param("$.transformers")
        # There can be multiple capacitors so we need to loop over them
        for index, transformer in enumerate(transformer_params):
            cap_params = {
                'nominal_capacity': transformer["nominal_capacity"],
                "reactance_resistance_ratio": transformer["reactance_resistance_ratio"],
                "tx_incoming_voltage": transformer["tx_incoming_voltage"],
                "tx_outgoing_voltage": transformer["tx_outgoing_voltage"],
                'model_name': f"Transformer{index}",
            }
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='ACACTransformer', param_data=cap_params, iteration=index)
