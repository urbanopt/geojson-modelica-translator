import logging
from typing import List, Optional

from pyfmi import load_fmu

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
)


class FmuRunner():
    """Run a modelica model with Spawn."""

    # TODO Fix typing to access None or Int!
    def __init__(self, fmu_path, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None):
        """Initialize the FMU runner.

        Args:
            fmu_path (_type_): Path to FMU to run
            start (Optional[int], optional): start time in seconds. Defaults to None, will default to the FMU value.
            stop (Optional[int], optional): end time in seconds. Defaults to None, will default to the FMU value.
            step (Optional[int], optional): step in seconds. Defaults to None, will default to the FMU value.
        """
        self.fmu_path = fmu_path
        self.start_time = start
        self.stop_time = stop
        self.step = step

        # load in and reate the metadata out of the FMU
        self._load_fmu()

    def set_step(self, step: int):
        """Set the step size for the FMU. This is only used when using the `advance` method.

        Args:
            step (int): Step size in seconds.
        """
        self.step = step

    def _load_fmu(self):
        self.fmu = load_fmu(self.fmu_path, enable_logging=True)

        fmu_version = self.fmu.get_version()
        if fmu_version != '2.0':
            raise ValueError(f"FMU must be version 2.0, found {fmu_version}")

        # Get available control inputs and outputs
        input_names = self.fmu.get_model_variables(causality=2).keys()
        output_names = self.fmu.get_model_variables(causality=3).keys()
        # Get input and output meta-data
        self.inputs_metadata = self._get_var_metadata(self.fmu, input_names, inputs=True)
        self.outputs_metadata = self._get_var_metadata(self.fmu, output_names)

    def _get_var_metadata(self, fmu, var_list: List[str], inputs: bool = False) -> dict:
        """Build a dictionary of variables and their metadata.

        Args:
            fmu (fmu): FMU from which to get variable metadata
            var_list (list[str]): List of variable names
            inputs (bool, optional): Flag for when the values are the inputs. Defaults to False.

        Returns:
            dict: Dictionary of variable names as keys and metadata as fields.
                {
                    <var_name_str>:
                        "Unit" : str,
                        "Description" : str,
                        "Minimum" : float,
                        "Maximum" : float
                }
        """
        # Initialize
        var_metadata = dict()
        # Get metadata
        for var in var_list:
            # Units
            if var == 'time':
                unit = 's'
                description = 'Time of simulation'
                mini = None
                maxi = None
            elif '_activate' in var:
                unit = None
                description = fmu.get_variable_description(var)
                mini = None
                maxi = None
            else:
                unit = fmu.get_variable_unit(var)
                description = fmu.get_variable_description(var)
                if inputs:
                    mini = fmu.get_variable_min(var)
                    maxi = fmu.get_variable_max(var)
                else:
                    mini = None
                    maxi = None
            var_metadata[var] = {
                'Unit': unit,
                'Description': description,
                'Minimum': mini,
                'Maximum': maxi
            }

        return var_metadata

    def _get_sim_options(self) -> List[dict]:
        """render the sim options as needed for the .fmu.simulate command. This returns a list, the
        first element are the options to flatten/pass to the call, and the second are the sim options

        Returns:
            List[dict, dict]: named_args, sim_options
        """
        # first determine the simulate methods' named options
        named_args = {}
        if self.start_time is not None:
            named_args['start_time'] = self.start_time
        if self.stop_time is not None:
            named_args['final_time'] = self.stop_time

        # TODO: figure out where the step goes ???

        sim_options = self.fmu.simulate_options()
        sim_options['CVode_options']['rtol'] = 1e-6
        sim_options['initialize'] = True
        return named_args, sim_options

    def advance(self) -> dict:
        """Advances the test case model simulation forward one step.

        Returns:
            dict: Contains the measurement data at the end of the step.
        """
        pass

    def run(self):
        """Run the FMU from start to stop with step interval"""
        logger.info(f"Running FMU Model {self.fmu_path} with start: {self.start_time} stop: {self.stop_time} step: {self.step}")
        named_args, sim_options = self._get_sim_options()
        return self.fmu.simulate(**named_args, options=sim_options)
