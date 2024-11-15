"""
module for all of the configuration required to build a filament bank
"""

import yaml
from dataclasses import dataclass, field, fields
from typing import Optional, List
from enum import Enum, Flag, auto
from math import sqrt
from pathlib import Path

from shapely.geometry import Point

from basic_shapes import distance_to_circle_edge

from filament_wheel_config import WheelConfig
from guidewall_config import GuidewallConfig
from sidewall_config import SidewallConfig
from frame_config import FrameConfig
from lock_pin_config import LockPinConfig
from filament_bracket_config import (
    LockStyle,
    FilamentBracketConfig,
    TubeConfig,
    ConnectorConfig,
    ChannelPairDirection,
)


class FrameStyle(Flag):
    """What sort of frame to have"""

    HANGING = auto()
    STANDING = auto()
    HYBRID = HANGING | STANDING


@dataclass
class BenderConfig:
    """
    A dataclass for configuration values for our filament bank
    """

    stl_folder: str = "../stl/default"

    wheel: WheelConfig = field(default_factory=WheelConfig)

    minimum_structural_thickness: float = 4
    minimum_thickness: float = 1

    minimum_bracket_depth: float = -1
    minimum_bracket_width: float = -1
    minimum_bracket_height: float = -1

    connectors: List[ConnectorConfig] = field(default_factory=list)
    fillet_ratio: float = 4
    tolerance: float = 0.2
    filament_count: int = 5

    frame_chamber_depth: float = 340
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    wall_thickness: float = 3

    frame_tongue_depth: float = 4
    frame_lock_pin_tolerance: float = 0.4
    frame_click_sphere_radius: float = 1
    frame_lock_style: LockStyle = LockStyle.BOTH

    frame_clip_depth_offset: float = 10

    wall_bracket_screw_radius: float = 2.25
    wall_bracket_screw_head_radius: float = 4.5
    wall_bracket_screw_head_sink: float = 1.4
    wall_bracket_post_count: int = 3

    m4_heatsink_radius: float = 3
    m4_heatsink_depth: float = 5
    m4_nut_radius: float = 3.9
    m4_nut_depth: float = 5
    m4_shaft_radius: float = 2.1

    @property
    def frame_clip_point(self) -> Point:
        """
        the x/y coordinates at which the center of the frame clip is positioned
        """
        return Point(
            distance_to_circle_edge(
                self.frame_bracket_exterior_radius,
                (0, self.frame_clip_depth_offset),
                angle=0,
            ),
            self.frame_clip_depth_offset,
        )

    def frame_bracket_exterior_x_distance(self, y_value) -> float:
        """
        for a given y value, find the distance from the center
        to the exterior of the frame curve
        -------
        arguments:
            - y_value: the placement of the intersection on the y axis
        """
        return distance_to_circle_edge(
            self.frame_bracket_exterior_radius, (0, y_value), 0
        )

    @property
    def sidewall_section_depth(self) -> float:
        """
        returns the length of the sidewall based on the overall chamber
        depth and allowing for the frame elements that contribute to the height
        """
        return (
            self.frame_chamber_depth
            - self.frame_connector_depth
            - self.frame_base_depth
            - (self.frame_bracket_exterior_radius - self.wheel.radius)
        ) / 2

    @property
    def frame_clip_inset(self) -> float:
        """
        the amount that the frame clip extends into
        each of the sidewalls of the frame
        """
        return self.wall_thickness / 3

    @property
    def frame_clip_rail_width(self) -> float:
        """
        the radius of the diamond that helps lock in
        the clip to the frame
        """
        return self.frame_clip_inset / sqrt(2) * 2

    @property
    def frame_clip_width(self) -> float:
        """
        the overall width of the clip that locks the
        filament bracket into the frame
        """
        return (
            self.bracket_depth
            + self.minimum_thickness / 2
            + self.wall_thickness * 2 / 3
        )

    @property
    def frame_base_depth(self) -> float:
        """
        the appropriate height for the bottom frame
        """
        return self.frame_tongue_depth + self.minimum_structural_thickness

    @property
    def sidewall_straight_depth(self) -> float:
        """
        the length of the straight portion of the sidewall
        """
        return (
            self.sidewall_section_depth
            - self.wheel.radius
            - self.frame_base_depth
        )

    @property
    def frame_connector_depth(self) -> float:
        """
        the depth of the connector frame
        """
        return self.frame_tongue_depth * 2 + self.minimum_thickness

    @property
    def frame_bracket_exterior_radius(self) -> float:
        """
        the correct exterior radius for the cylinder of the frame bracket
        """
        return Point(0, 0).distance(
            Point(
                self.wheel.radius - self.bracket_depth / 2, self.bracket_height
            )
        )

    @property
    def frame_bracket_exterior_diameter(self) -> float:
        """
        the correct exterior diameter for the cylinder of the frame bracket
        """
        return self.frame_bracket_exterior_radius * 2

    @property
    def frame_bracket_spacing(self) -> Point:
        """
        returns the distance between the sidewalls of the frame
        """
        return self.bracket_depth + self.wall_thickness + self.tolerance * 2

    @property
    def frame_click_sphere_point(self) -> Point:
        """
        the x / y coordinates for the snap fit points
        """
        return Point(
            self.frame_bracket_exterior_radius
            - self.minimum_structural_thickness,
            self.fillet_radius + self.frame_click_sphere_radius,
        )

    @property
    def top_frame_interior_width(self) -> float:
        """
        the overall interior width of the top frame
        """
        return (
            (self.bracket_depth + self.wall_thickness + self.tolerance * 2)
            * self.filament_count
        ) - self.wall_thickness

    #
    # do we want to eliminate the hanging bit given the way we are now
    # building frames and alternate parts?
    #
    def frame_exterior_length(self, frame_style=FrameStyle.HYBRID) -> float:
        """
        the overall interior length of the top frame
        """
        length = (
            self.frame_bracket_exterior_diameter
            + self.wall_thickness * 2
            + self.minimum_structural_thickness * 2.5
        )
        if FrameStyle.HANGING in frame_style:
            length += self.frame_hanger_offset * 2
        return length

    @property
    def frame_hanger_offset(self) -> float:
        """
        the offset to adjust for a wall bracket if enabled
        """
        return self.minimum_structural_thickness / 2

    @property
    def frame_exterior_width(self) -> float:
        """
        the overall interior width of the top frame
        """
        return self.top_frame_interior_width + (
            (self.minimum_structural_thickness + self.wall_thickness) * 2
        )

    @property
    def default_connector(self) -> ConnectorConfig:
        """
        returns the default connector
        """
        default_index = 0
        for connector in self.connectors:
            if connector.name.lower() == "default":
                return connector
        return self.connectors[default_index]

    @property
    def sidewall_width(self) -> float:
        """
        returns the appropriate width for the sidewalls
        """
        return (
            self.wheel.diameter
            + (
                self.wheel.radial_tolerance
                + self.default_connector.diameter
                + self.fillet_radius
                + self.wall_thickness
                + self.tolerance
            )
            * 2
        )

    @property
    def bearing_shelf_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (self.bracket_depth - self.wheel.bearing.depth) / 2

    @property
    def bracket_width(self) -> float:
        """
        returns the width of the bracket
        """
        return max(
            self.minimum_bracket_width,
            self.wheel.diameter
            + self.wheel_support_height * 2
            + self.minimum_structural_thickness * 3
            + self.fillet_radius * 2,
        )

    @property
    def wheel_support_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (
            self.bracket_depth
            - self.wheel.bearing.depth
            - self.wheel.lateral_tolerance
        ) / 2

    @property
    def chamber_cut_length(self) -> float:
        """
        the length to cut for each chamber in the frames
        """
        return self.sidewall_width - self.wall_thickness * 2

    @property
    def bracket_height(self) -> float:
        """
        returns the height of the bracket
        """
        return max(
            self.minimum_bracket_height,
            self.wheel.radius
            + self.wheel.radial_tolerance
            + self.minimum_structural_thickness * 2,
        )

    @property
    def bracket_depth(self) -> float:
        """
        returns the depth of the bracket
        """
        return max(
            self.minimum_bracket_depth,
            self.wheel.bearing.depth
            + self.wheel.lateral_tolerance
            + self.minimum_structural_thickness * 2,
            self.default_connector.diameter + self.minimum_thickness * 2,
            self.default_connector.tube.outer_diameter
            + self.minimum_thickness * 2,
        )

    @property
    def fillet_radius(self) -> float:
        """
        returns the fillet radis for bracket parts
        """
        return self.bracket_depth / self.fillet_ratio

    @property
    def sidewall_config(self) -> SidewallConfig:
        return SidewallConfig(
            stl_folder=self.stl_folder,
            top_diameter=self.wheel.diameter,
            top_extension=self.frame_base_depth,
            straight_length=self.sidewall_section_depth
            - self.frame_base_depth
            - self.wheel.radius,
            sidewall_width=self.sidewall_width,
            wall_thickness=self.wall_thickness,
            minimum_thickness=self.minimum_thickness,
            reinforcement_thickness=self.minimum_structural_thickness
            + self.wall_thickness,
            reinforcement_inset=self.minimum_structural_thickness,
            wall_window_apothem=self.wall_window_apothem,
            wall_window_bar_thickness=self.wall_window_bar_thickness,
            click_fit_radius=self.frame_click_sphere_radius,
            end_count=1,
        )

    @property
    def guidewall_config(self) -> SidewallConfig:
        return GuidewallConfig(
            stl_folder=self.stl_folder,
            core_length=self.sidewall_straight_depth - self.wall_thickness / 2,
            section_width=self.frame_bracket_spacing,
            tongue_width=self.top_frame_interior_width - self.tolerance * 2,
            tongue_depth=self.frame_tongue_depth,
            section_count=self.filament_count,
            wall_thickness=self.wall_thickness,
            minimum_thickness=self.minimum_thickness,
            reinforcement_thickness=self.minimum_structural_thickness,
            reinforcement_inset=self.minimum_structural_thickness,
            wall_window_apothem=self.wall_window_apothem,
            wall_window_bar_thickness=self.wall_window_bar_thickness,
            click_fit_radius=self.frame_click_sphere_radius,
            tolerance=self.tolerance,
            fillet_ratio=self.fillet_ratio,
        )

    @property
    def frame_config(self) -> FrameConfig:
        return FrameConfig(
            stl_folder=self.stl_folder,
            exterior_width=self.frame_exterior_width,
            exterior_length=self.frame_exterior_length(
                frame_style=FrameStyle.STANDING
            ),
            depth=self.frame_connector_depth,
            interior_length=self.chamber_cut_length,
            interior_width=self.top_frame_interior_width,
            interior_offset=self.frame_hanger_offset,
            fillet_radius=self.fillet_radius,
            bracket_spacing=self.frame_bracket_spacing,
            bracket_width=self.bracket_width,
            filament_count=self.filament_count,
            wall_thickness=self.wall_thickness,
            minimum_thickness=self.minimum_thickness,
            tolerance=self.tolerance,
            click_fit_radius=self.frame_click_sphere_radius,
            groove_width=self.wall_thickness + self.tolerance,
            groove_depth=self.frame_tongue_depth + self.tolerance,
            groove_distance=self.sidewall_width + self.wall_thickness,
            base_depth=self.frame_base_depth,
            bracket_height=self.bracket_height,
            exterior_radius=self.frame_bracket_exterior_radius,
            interior_radius=self.wheel.radius,
            tube_radius=self.default_connector.tube.outer_radius,
            minimum_structural_thickness=self.minimum_structural_thickness,
            include_lock_clip=LockStyle.CLIP in self.frame_lock_style,
            include_lock_pin=LockStyle.PIN in self.frame_lock_style,
            wall_bracket_post_count=self.wall_bracket_post_count,
            lock_pin_tolerance=self.frame_lock_pin_tolerance,
            screw_head_radius=self.wall_bracket_screw_head_radius,
            screw_head_sink=self.wall_bracket_screw_head_sink,
            screw_shaft_radius=self.wall_bracket_screw_radius,
            m4_heatsink_radius=self.m4_heatsink_radius,
            m4_heatsink_depth=self.m4_heatsink_depth,
            m4_nut_radius=self.m4_nut_radius,
            m4_nut_depth=self.m4_nut_depth,
            m4_shaft_radius=self.m4_shaft_radius,
        )

    def filament_bracket_config(
        self, connector_index=0
    ) -> FilamentBracketConfig:
        return FilamentBracketConfig(
            stl_folder=self.stl_folder,
            wheel=self.wheel,
            connector=self.connectors[connector_index],
            bracket_depth=self.bracket_depth,
            bracket_height=self.bracket_height,
            bracket_width=self.bracket_width,
            exterior_radius=self.frame_bracket_exterior_radius,
            frame_bracket_exterior_x_distance=self.frame_bracket_exterior_x_distance(
                self.frame_base_depth
            ),
            fillet_radius=self.fillet_radius,
            frame_click_sphere_point=self.frame_click_sphere_point,
            frame_click_sphere_radius=self.frame_click_sphere_radius,
            frame_clip_depth_offset=self.frame_clip_depth_offset,
            frame_clip_point=self.frame_clip_point,
            frame_clip_rail_width=self.frame_clip_rail_width,
            frame_clip_width=self.frame_clip_width,
            frame_lock_pin_tolerance=self.frame_lock_pin_tolerance,
            frame_lock_style=self.frame_lock_style,
            lock_pin=self.lock_pin_config,
            minimum_structural_thickness=self.minimum_structural_thickness,
            minimum_thickness=self.minimum_thickness,
            sidewall_section_depth=self.sidewall_section_depth,
            sidewall_width=self.sidewall_width,
            tolerance=self.tolerance,
            wall_thickness=self.wall_thickness,
            wall_window_apothem=self.wall_window_apothem,
            wall_window_bar_thickness=self.wall_window_bar_thickness,
            wheel_support_height=self.wheel_support_height,
            bearing_shelf_height=self.bearing_shelf_height,
            channel_pair_direction=ChannelPairDirection.LEAN_FORWARD,
        )

    @property
    def lock_pin_config(self) -> LockPinConfig:
        return LockPinConfig(
            stl_folder=self.stl_folder,
            pin_length=self.frame_exterior_width,
            tolerance=self.frame_lock_pin_tolerance,
            height=self.minimum_structural_thickness,
        )

    def __init__(self, configuration: str = None, **kwargs):
        """initialize the configuration
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - kwargs: specific configuration values to override as key value pairs
        """
        if configuration:
            configuration = str(configuration)
            try:
                self.load_config(configuration)
            except Exception as e:
                raise ValueError(
                    f"Error loading configuration from {configuration}"
                ) from e
        else:
            for field in fields(self):
                setattr(
                    self, field.name, kwargs.get(field.name, field.default)
                )
            default_connector = ConnectorConfig()
            self.connectors = [default_connector]
            self.wheel = WheelConfig()

    def load_config(self, configuration: str):
        """
        loads a configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
        """
        configuration = str(configuration)
        if "\n" not in configuration:
            path = Path(configuration)
            if path.exists() and path.is_file():
                configuration = path.read_text()
        config_dict = yaml.safe_load(configuration)

        for field in fields(BenderConfig):
            if field.name in config_dict["BenderConfig"]:
                value = config_dict["BenderConfig"][field.name]
                if isinstance(field.type, type) and issubclass(
                    field.type, (Enum, Flag)
                ):
                    setattr(self, field.name, field.type[value.upper()])
                elif field.name == "wheel":
                    self.wheel = WheelConfig(**value)
                elif field.name == "connectors":
                    self.connectors = [
                        ConnectorConfig(
                            **{
                                **connector,
                                "tube": TubeConfig(**connector["tube"]),
                            }
                        )
                        for connector in value
                    ]

                else:
                    setattr(self, field.name, value)


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    test = BenderConfig(config_path)
    print(test.bracket_depth, test.bracket_height, test.bracket_width)
    print(test.sidewall_width)
    for connector in test.connectors:
        print(connector.tube.inner_diameter)
    print(test.default_connector.diameter)
    print(test.wheel.radius, test.wheel.bearing.depth)
    print(test.sidewall_section_depth)
    print(test.frame_bracket_exterior_radius)
    print(test.wheel.radius, test.bracket_depth, test.bracket_height)
    print(test.stl_folder)
    print(test.frame_lock_style)
