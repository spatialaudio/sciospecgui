from dataclasses import dataclass
from typing import Union


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
