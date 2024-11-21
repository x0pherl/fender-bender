from dataclasses import dataclass, fields
from enum import Flag, auto
import yaml
from pathlib import Path

from partomatic import PartomaticConfig

from shapely.geometry import Point


class FrameStyle(Flag):
    """What sort of frame to have"""

    HANGING = auto()
    STANDING = auto()
    HYBRID = HANGING | STANDING


@dataclass
class FrameConfig(PartomaticConfig):
    yaml_tree: str = "frame"
    stl_folder: str = "NONE"
    frame_style: FrameStyle = FrameStyle.HYBRID
    exterior_width: float = 91
    exterior_length: float = 120
    depth: float = 9
    interior_length: float = 90.1
    interior_width: float = 77
    interior_offset: float = 2
    fillet_radius: float = 3.15
    bracket_spacing: float = 16
    bracket_width: float = 96.3
    filament_count: int = 5
    wall_thickness: float = 3
    minimum_thickness: float = 1
    tolerance: float = 0.2
    groove_width: float = 3.2
    groove_depth: float = 4.2
    groove_distance: float = 99.1
    click_fit_radius: float = 1
    click_fit_distance: float = 61
    base_depth: float = 8
    bracket_height: float = 43.2
    exterior_radius: float = 51.86
    interior_radius: float = 35
    tube_radius: float = 3.25
    minimum_structural_thickness: float = 4
    include_lock_clip: bool = True
    include_lock_pin: bool = True
    cut_hanger: bool = True
    wall_bracket_post_count: int = 3
    lock_pin_tolerance: float = 0.5
    lock_pin_point: Point = (Point(50.89, 10),)
    screw_head_radius: float = 4.5
    screw_head_sink: float = 1.4
    screw_shaft_radius: float = 2.25
    drybox: bool = False

    @property
    def bracket_depth(self) -> float:
        return self.bracket_spacing - self.wall_thickness - self.tolerance * 2

    @property
    def exterior_diameter(self) -> float:
        return self.exterior_radius * 2

    @property
    def interior_diameter(self) -> float:
        return self.interior_radius * 2

    @property
    def stand_depth(self) -> float:
        return self.base_depth * 2 + self.exterior_radius

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)
