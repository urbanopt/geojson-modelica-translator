import json
from pathlib import Path


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
