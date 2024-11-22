from dataclasses import dataclass, field, fields, is_dataclass, MISSING
from enum import Enum, Flag, auto
from pathlib import Path
from typing import List, Optional

from shapely.geometry import Point
import yaml

from basic_shapes import circular_intersection
from filament_wheel_config import WheelConfig
from lock_pin_config import LockPinConfig
from partomatic import PartomaticConfig


class LockStyle(Flag):
    """What sort of clip to have"""

    CLIP = auto()
    PIN = auto()
    BOTH = CLIP | PIN
    NONE = auto()


class ChannelPairDirection(Enum):
    """
    the direction of the filament channels
    -------
    options:
        - LEAN_FORWARD: the channel closest to the back of the frame is straight,
            the channel closest to the front of the frame is curved outwards
        - LEAN_REVERSE: the channel closest to the front of the frame is straight,
            the channel closest to the back of the frame is curved outwards
        - STRAIGHT: both channels extend straight out from the bracket
    """

    LEAN_FORWARD = auto()
    LEAN_REVERSE = auto()
    STRAIGHT = auto()


@dataclass
class TubeConfig(PartomaticConfig):
    inner_diameter: float = 3.55
    outer_diameter: float = 6.5

    @property
    def inner_radius(self) -> float:
        """
        returnes the inner radius of the tube
        """
        return self.inner_diameter / 2

    @property
    def outer_radius(self) -> float:
        """
        returnes the outer radius of the tube
        """
        return self.outer_diameter / 2

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)


@dataclass
class ConnectorConfig(PartomaticConfig):
    name: str = "connector"
    file_prefix: Optional[str] = None
    file_suffix: Optional[str] = None
    diameter: float = 10.1
    length: float = 6.7
    threaded: bool = True
    thread_pitch: float = 1.0
    thread_angle: float = 30.0
    thread_interference: float = 0.4
    tube: TubeConfig = field(default_factory=TubeConfig)

    @property
    def radius(self) -> float:
        """
        returns the radius of the connector
        """
        return self.diameter / 2

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)


@dataclass
class FilamentBracketConfig(PartomaticConfig):
    yaml_tree: str = "FilamentBracket"

    stl_folder: str = "NONE"
    file_prefix: str = ""
    file_suffix: str = ""
    wheel: WheelConfig = field(default_factory=WheelConfig)
    connector: ConnectorConfig = field(default_factory=ConnectorConfig)
    wheel_support_height: float = 0.2
    bracket_depth: float = 12.6
    bracket_height: float = 43.5
    bracket_width: float = 96.3
    exterior_radius: float = 52
    frame_bracket_exterior_x_distance: float = 1
    fillet_radius: float = 3.15
    frame_click_sphere_point: Point = Point(47.86, 4.15)
    frame_click_sphere_radius: float = 1
    frame_clip_depth_offset: float = 10
    frame_clip_point: Point = Point(50.89, 10)
    frame_clip_rail_width: float = 1.41
    frame_clip_width: float = 15.1
    frame_lock_pin_tolerance: float = 0.6
    frame_lock_style: LockStyle = LockStyle.BOTH
    lock_pin: LockPinConfig = field(default_factory=LockPinConfig)
    lock_pin_point: Point = Point(50.89, 10)
    minimum_structural_thickness: float = 4
    minimum_thickness: float = 1
    sidewall_section_depth: float = 168
    sidewall_width: float = 96.1
    tolerance: float = 0.2
    wall_thickness: float = 3
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    bearing_shelf_height: float = 4.3
    channel_pair_direction: ChannelPairDirection = (
        ChannelPairDirection.LEAN_FORWARD
    )
    block_pin_generation: bool = False

    @property
    def filament_funnel_height(self) -> float:
        """
        calculates the appropriate filament funnel height
        to clear the filament wheel
        """
        return circular_intersection(
            self.wheel.radius
            + self.wheel.radial_tolerance
            + self.minimum_thickness,
            self.wheel.radius - self.connector.tube.outer_radius,
        )

    @property
    def wheel_guide_outer_radius(self) -> float:
        return (
            self.wheel.radius
            + self.wheel.radial_tolerance
            + self.wheel_support_height
        )

    @property
    def wheel_guide_inner_radius(self) -> float:
        return self.wheel_guide_outer_radius - self.spoke_thickness

    @property
    def spoke_thickness(self) -> float:
        return self.wheel_support_height * 1.5

    def _default_config(self):
        """
        Resets all values to their default values.
        """
        for field in fields(self):
            if field.default is not MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not MISSING:
                setattr(self, field.name, field.default_factory())
            else:
                raise ValueError(f"Field {field.name} has no default value")

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)


from basic_shapes import circular_intersection
