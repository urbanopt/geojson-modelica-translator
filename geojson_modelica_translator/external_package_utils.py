import json
import logging
from pathlib import Path

from modelica_builder.modelica_mos_file import ModelicaMOS

logger = logging.getLogger(__name__)


def load_loop_order(system_parameters_file: Path) -> list:
    """Loads the loop order from a JSON file

    loop_order file is always saved next to the system parameters file

    :param system_parameters_file: Path to the system parameters file
    :return: list of building & ghe ids in loop order
    """
    loop_order_path = Path(system_parameters_file).parent / "_loop_order.json"
    if not loop_order_path.is_file():
        raise FileNotFoundError(f"Loop order file not found at {loop_order_path}")
    return json.loads(loop_order_path.read_text())


def set_minimum_dhw_load(data_dir) -> None:
    """
    If peak water heating load is 0, set it to 5kW or 10% of peak space heating load, whichever is greater.

    :param data_dir: Path to the Modelica data directory
    :return: None
    """
    if data_dir.is_dir():
        for bldg_dir in data_dir.iterdir():
            mo_load_file = data_dir / bldg_dir / "modelica.mos"
            # In case the modelica loads file isn't named modelica.mos:
            if not mo_load_file.is_file():
                modelica_loads = list((data_dir / bldg_dir).rglob("*"))
                if len(modelica_loads) == 1:
                    mo_load_file = modelica_loads[0]
            if mo_load_file.is_file():
                mos_file = ModelicaMOS(mo_load_file)
                # Force peak water heating load to be at least 5000W
                peak_water = mos_file.retrieve_header_variable_value("Peak water heating load", cast_type=float)
                if peak_water == 0:
                    peak_heat = mos_file.retrieve_header_variable_value("Peak space heating load", cast_type=float)
                    peak_swh = max(peak_heat / 10, 5000)

                    mos_file.replace_header_variable_value("Peak water heating load", peak_swh)
                    mos_file.save()
    else:
        # The scaffold didn't get built properly or there are no loads in the Modelica package.
        logger.warning(
            f"Could not find Modelica data directory {data_dir}. Perhaps there are no loads in the model,"
            " and perhaps that is intentional."
        )
