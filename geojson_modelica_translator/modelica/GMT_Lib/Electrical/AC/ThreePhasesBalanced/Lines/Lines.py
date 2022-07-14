from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class DistributionLines(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        distribution_line_params = self.system_parameters.get_param("$.distribution_lines")
        # Each segment of cable gets its own mofile, numbered with 'iteration'
        for index, line in enumerate(distribution_line_params):
            # This is how we map from ditto-reader to mbl. It's pretty brittle, and will need updating in this state
            # https://github.com/urbanopt/urbanopt-ditto-reader/blob/develop/example/extended_catalog.json
            for wire in line["commercial_line_type"]:
                if '477kcmil' in wire:
                    mbl_wire = 'Buildings.Electrical.Transmission.MediumVoltageCables.Annealed_Al_500'
                if '750kcmil' in wire:
                    # FIXME: This mapping from 750kcmil to 1000kcmil is not ideal
                    # A 750kcmil has been proposed for the MBL
                    # The temporary alternative is to map to 5000 kcmil, which didn't seem right to me
                    mbl_wire = 'Buildings.Electrical.Transmission.MediumVoltageCables.Annealed_Al_1000'
            line_params = {
                'length': line["length"],
                'ampacity': line["ampacity"],
                'nominal_voltage': line["nominal_voltage"],
                'commercial_line_type': mbl_wire,
                'model_name': f"Line{index}",
            }
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='ACLine', param_data=line_params, iteration=index)
