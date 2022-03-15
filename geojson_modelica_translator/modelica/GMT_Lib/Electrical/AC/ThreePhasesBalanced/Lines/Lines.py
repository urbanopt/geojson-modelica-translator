from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class DistributionLines(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        distribution_line_params = self.system_parameters.get_param("$.distribution_lines")
        # There can be multiple community pv arrays so we need to loop over them
        for index, line in enumerate(distribution_line_params):
            line_params = {
                'length': line["length"],
                'ampacity': line["ampacity"],
                'nominal_voltage': line["nominal_voltage"],
                'commercial_line_type': line["commercial_line_type"],
                'model_name': f"Line{index}",
            }
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='ACLine', param_data=line_params, iteration=index)
