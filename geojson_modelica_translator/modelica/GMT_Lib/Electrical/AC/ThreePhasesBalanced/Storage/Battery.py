from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class Battery(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        # TODO: add support for batteries attached to each building
        district_battery_params = self.system_parameters.get_param("$.battery_banks")
        # There can be multiple batteries so we need to loop over them
        for index, battery in enumerate(district_battery_params):
            district_battery_params = {
                'nominal_capacity': battery["capacity"],
                'nominal_voltage': battery["nominal_voltage"],
                'model_name': f"AcBattery{index}",
            }
            # render template to final modelica file
            self.to_modelica(
                output_dir=output_dir,
                model_name='AcBattery',
                param_data=district_battery_params,
                iteration=index
            )
