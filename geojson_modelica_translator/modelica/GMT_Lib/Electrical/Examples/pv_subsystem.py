from pathlib import Path

from geojson_modelica_translator.modelica.simple_gmt_base import SimpleGMTBase


class PVSubsystem(SimpleGMTBase):
    def __init__(self, system_parameters):
        self.system_parameters = system_parameters
        self.template_dir = Path(__file__).parent
        super().__init__(self.system_parameters, self.template_dir)

    def build_from_template(self, output_dir: Path):
        pv_subsystem_params = self.system_parameters.get_param("$")
        self.to_modelica(output_dir=output_dir, model_name='PVsubsystem', param_data=pv_subsystem_params)
