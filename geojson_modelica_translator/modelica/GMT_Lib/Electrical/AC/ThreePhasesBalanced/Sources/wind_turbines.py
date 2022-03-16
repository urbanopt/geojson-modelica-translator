from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class WindTurbine(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        wind_turbine_params = self.system_parameters.get_param("$.wind_turbines")
        # There can be multiple community pv arrays so we need to loop over them
        for index, turbine in enumerate(wind_turbine_params):
            turbine_params = {
                'scaling_factor': turbine["scaling_factor"],
                'height_over_ground': turbine["height_over_ground"],
                'nominal_voltage': turbine["nominal_voltage"],
                'power_curve': turbine["power_curve"],
                'model_name': f"WindTurbine{index}",
            }
            # FIXME: "power_curve" is a list of lists in the sys-param file.
            # This whole string shenanigans is to format it into something that will make modelica happy.
            # TODO: confirm that modelica chokes on a list of lists - ie comment this whole block out and see if the model will run.
            power_curve_string = '['
            for point in turbine_params["power_curve"]:
                power_curve_string += f'{point[0]}, {point[1]}; '
            power_curve_string = power_curve_string.rstrip('; ')
            power_curve_string += ']'
            turbine_params["power_curve"] = power_curve_string
            # render template to final modelica file
            self.to_modelica(output_dir=output_dir, model_name='WindTurbine', param_data=turbine_params, iteration=index)
