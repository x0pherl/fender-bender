from dataclasses import dataclass, fields
from pathlib import Path

import yaml

from partomatic import PartomaticConfig


class LockPinConfig(PartomaticConfig):
    yaml_tree: str = "lockpin"
    stl_folder: str = "NONE"
    pin_length: float = 100
    tolerance: float = 0.1
    height: float = 4
    tie_loop: bool = True
