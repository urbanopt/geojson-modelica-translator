import logging
from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class Inductive_load(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        inductive_load_params = self.system_parameters.get_param("$.ac_inductive_loads")
        for index, load in enumerate(inductive_load_params):
            inductive_params = {
                'nominal_power_consumption': load["nominal_power_consumption"],
                'nominal_voltage': load["nominal_voltage"],
                'model_name': f"InductiveLoad{index}",
            }
            # render template to final modelica file
            self.to_modelica(
                output_dir=output_dir,
                model_name='Inductive',
                param_data=inductive_params,
                iteration=index
            )
            # If the sys-param file is missing an entry, it will show up as a jinja2.exceptions.UndefinedError
