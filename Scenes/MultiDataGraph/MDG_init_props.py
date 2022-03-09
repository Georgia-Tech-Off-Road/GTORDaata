from Utilities.general_constants import TIME_OPTION
from dataclasses import dataclass
from numpy import ndarray
from typing import List, Dict


@dataclass(frozen=True)
class MDGInitProps:
    is_line_graph: bool = True
    x_sensor: str = TIME_OPTION
    y_sensors: List[str] = None
    read_only: bool = False
    initial_data_values: Dict[str, ndarray] = None
