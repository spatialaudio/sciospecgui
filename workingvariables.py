from dataclasses import dataclass
from typing import Union


@dataclass
class ScioSpecMeasurementConfig:
    burst_count: int
    total_meas_num: int
    n_el: int
    exc_freq: int
    framerate: int
    amplitude: Union[int, float]
    inj_skip: str
    notes: str
    configured: bool


@dataclass
class StoreConfig:
    s_path: str
    save_format: str


@dataclass
class ScioSpecDeviceInfo:
    com_port: str
    connection_established: bool


@dataclass
class OperatingSystem:
    system: str
    resolution_width: int
    resolution_height: int
