from dataclasses import dataclass, fields
from enum import Enum, auto
import yaml
from pathlib import Path

from partomatic import PartomaticConfig


class HangingBracketStyle(Enum):
    """What sort of frame to have"""

    SURFACE_MOUNT = auto()
    WALL_MOUNT = auto()
    SURFACE_TOOL = auto()


@dataclass
class HangingBracketConfig(PartomaticConfig):
    stl_folder: str = "NONE"
    yaml_tree: str = "hanging-bracket"
    bracket_style: HangingBracketStyle = HangingBracketStyle.SURFACE_MOUNT
    width: float = 91
    height: float = 43.2
    arm_thickness: float = 8
    fillet_radius: float = 3.15
    bracket_inset: float = 4
    tolerance: float = 0.2
    post_count: int = 3
    screw_head_radius: float = 4.5
    screw_head_sink: float = 1.4
    screw_shaft_radius: float = 2.25
    m4_heatsink_radius: float = 3
    m4_heatsink_depth: float = 5
    m4_nut_radius: float = 4.3
    m4_nut_depth: float = 5
    m4_shaft_radius: float = 2.1
    heatsink_desk_nut: bool = False
    wall_screw_offset: float = 0

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)

    @property
    def surface_bolt_spacing(self):
        return ((self.width - self.arm_thickness * 2) // 10) * 10
