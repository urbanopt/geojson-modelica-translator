import logging
from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class Polynomial_Boiler(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        polynomial_boiler_params = self.system_parameters.get_param("$.district_system.fourth_generation.central_heating_plant_parameters")
        # render template to final modelica file
        self.to_modelica(
            output_dir=output_dir,
            model_name='BoilerPolynomial',
            param_data=polynomial_boiler_params,
        )
        # If the sys-param file is missing an entry, it will show up as a jinja2.exceptions.UndefinedError
