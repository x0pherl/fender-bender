from dataclasses import dataclass, field, fields, is_dataclass, MISSING
from enum import Enum, Flag, auto
from pathlib import Path
from typing import List, Optional

import yaml

from fb_library import Point, circular_intersection
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
    twist_snap_extension: bool = False
    tube: TubeConfig = field(default_factory=TubeConfig)

    @property
    def radius(self) -> float:
        """
        returns the radius of the connector
        """
        return self.diameter / 2


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
    frame_click_sphere_point: Point = field(default_factory=lambda: Point(47.86, 4.15))
    frame_click_sphere_radius: float = 1
    frame_clip_depth_offset: float = 10
    frame_clip_point: Point = field(default_factory=lambda: Point(50.89, 10))
    frame_clip_rail_width: float = 1.41
    frame_clip_width: float = 15.1
    frame_lock_pin_tolerance: float = 0.6
    frame_lock_style: LockStyle = LockStyle.BOTH
    lock_pin: LockPinConfig = field(default_factory=LockPinConfig)
    lock_pin_point: Point = field(default_factory=lambda: Point(50.89, 10))
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


yml = """
FilamentBracket:
    stl_folder: "NONE"
    file_prefix: ""
    file_suffix: ""
    wheel:
        diameter: 12.3
        spoke_count: 25
        lateral_tolerance: 1.111
        radial_tolerance: 0.222
        bearing:
            diameter: 1.2
            inner_diameter: 0.1
            shelf_diameter: 0.2
            depth: 1
    connector:
        name: "3mmx6mm tube connector"
        threaded: False
        file_prefix: "prefix"
        file_suffix: "suffix"
        thread_pitch: 1
        thread_angle: 30
        thread_interference: 0.4
        diameter: 6.5
        length: 6.7
        tube:
            inner_diameter: 3.6
            outer_diameter: 6.5
    wheel_support_height: 0.2
    bracket_depth: 12.6
    bracket_height: 43.5
    bracket_width: 96.3
    exterior_radius: 52
    frame_bracket_exterior_x_distance: 1
    fillet_radius: 3.15
    frame_click_sphere_point: (47.86, 4.15)
    frame_click_sphere_radius: 1
    frame_clip_depth_offset: 10
    frame_clip_point: (50.89, 10)
    frame_clip_rail_width: 1.41
    frame_clip_width: 15.1
    frame_lock_pin_tolerance: 0.6
    frame_lock_style: "BOTH"
    lock_pin:
        stl_folder: "NONE"
        pin_length: 100
        tolerance: 0.1
        height: 4
        tie_loop: True
    minimum_structural_thickness: 4
    minimum_thickness: 1
    sidewall_section_depth: 168
    sidewall_width: 96.1
    tolerance: 0.2
    wall_thickness: 3
    wall_window_apothem: 8
    wall_window_bar_thickness: 1.5
    bearing_shelf_height: 4.3
    channel_pair_direction: "LEAN_FORWARD"
"""
config = FilamentBracketConfig(yml)
print(config.bracket_height)
