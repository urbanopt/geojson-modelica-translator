import logging
from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class Generator(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        for building_index, building in enumerate(self.system_parameters.get_param("$.buildings")):
            building_generator_params = building["diesel_generators"]
            # There can be multiple generators attached to each building so we need to loop over them
            # FIXME: This code doesn't currently support multiple generators per building
            # If multiple generators are attached to one building, only the last one will be used
            for generator_index, generator in enumerate(building_generator_params):
                generator_params = {
                    'source_phase_shift': generator["source_phase_shift"],
                    'nominal_power_generation': generator["nominal_power_generation"],
                    'model_name': f"Generator{building_index}",
                }
            # render template to final modelica file
            self.to_modelica(
                output_dir=output_dir,
                model_name='Generator',
                param_data=generator_params,
                iteration=building_index
            )
