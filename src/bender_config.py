"""
module for all of the configuration required to build a filament bank
"""

import yaml
from dataclasses import dataclass, field, fields
from typing import Optional, List
from enum import Flag, auto
from math import cos, radians, sin, sqrt
from pathlib import Path

from shapely.geometry import Point


class LockStyle(Flag):
    """What sort of clip to have"""

    CLIP = auto()
    PIN = auto()
    BOTH = CLIP | PIN
    NONE = auto()


class FrameStyle(Flag):
    """What sort of frame to have"""

    HANGING = auto()
    STANDING = auto()
    HYBRID = HANGING | STANDING


def _distance_to_circle_edge(radius, point, angle) -> float:
    """
    for a circle with the given radius, find the distance from the
    given point to the edge of the circle in the direction determined
    by the given angle
    """
    x1, y1 = point
    theta = radians(angle)  # Convert angle to radians if it's given in degrees

    # Coefficients of the quadratic equation
    a = 1
    b = 2 * (x1 * cos(theta) + y1 * sin(theta))
    c = x1**2 + y1**2 - radius**2

    # Calculate the discriminant
    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return None  # No real intersection, should not happen

    # Solve the quadratic equation for t
    t1 = (-b + sqrt(discriminant)) / (2 * a)
    t2 = (-b - sqrt(discriminant)) / (2 * a)

    # We need the positive t, as we are extending outwards
    t = max(t1, t2)

    return t


@dataclass
class BearingConfig:
    diameter: float = 12.1
    inner_diameter: float = 6.1
    shelf_diameter: float = 8.5
    depth: float = 4

    @property
    def radius(self) -> float:
        """
        returns the radius of the bearing
        """
        return self.diameter / 2

    @property
    def inner_radius(self) -> float:
        """
        returns the inner_radius of the bearing
        """
        return self.inner_diameter / 2

    @property
    def shelf_radius(self) -> float:
        """
        returns the radius of the bearing shelf
        """
        return self.shelf_diameter / 2


@dataclass
class WheelConfig:
    diameter: float = 70
    spoke_count: int = 5
    lateral_tolerance: float = 0.6
    radial_tolerance: float = 0.2
    bearing: BearingConfig = field(default_factory=BearingConfig)

    @property
    def radius(self) -> float:
        """
        returns the radius of the wheel
        """
        return self.diameter / 2


@dataclass
class TubeConfig:
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


@dataclass
class ConnectorConfig:
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


@dataclass
class BenderConfig:
    """
    A dataclass for configuration values for our filament bank
    """

    stl_folder: str = "../stl/default"

    bearing: BearingConfig = field(default_factory=BearingConfig)

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
    solid_walls: bool = False
    wall_window_apothem: float = 8
    wall_window_bar_thickness: float = 1.5
    wall_thickness: float = 3

    frame_tongue_depth: float = 4
    frame_lock_pin_tolerance: float = 0.4
    frame_click_sphere_radius: float = 1
    frame_lock_style: LockStyle = LockStyle.BOTH

    frame_clip_depth_offset: float = 10

    frame_style: FrameStyle = FrameStyle.HYBRID
    wall_bracket_screw_radius: float = 2.25
    wall_bracket_screw_head_radius: float = 4.5
    wall_bracket_screw_head_sink: float = 1.4
    wall_bracket_post_count: int = 3

    @property
    def frame_clip_point(self) -> Point:
        """
        the x/y coordinates at which the center of the frame clip is positioned
        """
        return Point(
            _distance_to_circle_edge(
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
        return _distance_to_circle_edge(
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
            - self.minimum_structural_thickness * 1.5,
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

    @property
    def frame_exterior_length(self) -> float:
        """
        the overall interior length of the top frame
        """
        length = (
            self.frame_bracket_exterior_diameter
            + self.wall_thickness * 2
            + self.minimum_structural_thickness * 2.5
            + self.frame_hanger_offset * 2
        )
        return length

    @property
    def frame_hanger_offset(self) -> float:
        """
        the offset to adjust for a wall bracket if enabled
        """
        return (
            self.minimum_structural_thickness / 2
            if FrameStyle.HANGING in self.frame_style
            else 0
        )

    @property
    def frame_exterior_width(self) -> float:
        """
        the overall interior width of the top frame
        """
        return self.top_frame_interior_width + (
            (self.minimum_structural_thickness + self.wall_thickness) * 2
        )

    @property
    def filament_funnel_height(self) -> float:
        """
        calculates the appropriate filament funnel height
        to clear the filament wheel
        """
        return _distance_to_circle_edge(
            radius=self.wheel.radius
            + self.wheel.radial_tolerance
            + self.minimum_thickness,
            point=(
                self.wheel.radius - self.default_connector.tube.outer_radius,
                0,
            ),
            angle=90,
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
    def wheel_support_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (
            self.bracket_depth
            - self.wheel.bearing.depth
            - self.wheel.lateral_tolerance
        ) / 2

    def __init__(self, file_path: str = None, **kwargs):
        """initialize the configuration"""
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(
                    f"The file {file_path} does not exist."
                )
            try:
                self.load_config(file_path)
            except Exception as e:
                raise ValueError(
                    f"Error loading configuration from {file_path}: {e}"
                ) from e
        else:
            for field in fields(self):
                setattr(
                    self, field.name, kwargs.get(field.name, field.default)
                )
            default_connector = ConnectorConfig()
            self.connectors = [default_connector]
            self.wheel.bearing = BearingConfig()
            self.wheel = WheelConfig()

    def load_config(self, configuration_path: str):
        """
        loads a configuration from a file
        -------
        arguments:
            - configuration_path: the path to the configuration file
        """
        with open(configuration_path, "r") as stream:
            config_dict = yaml.safe_load(stream)

        for field in fields(BenderConfig):
            if field.name in config_dict["BenderConfig"]:
                value = config_dict["BenderConfig"][field.name]
                if field.name == "frame_lock_style":
                    setattr(self, field.name, LockStyle[value.upper()])
                elif field.name == "frame_style":
                    setattr(self, field.name, FrameStyle[value.upper()])
                elif field.name == "wheel":
                    if "bearing" in value:
                        value["bearing"] = BearingConfig(**value["bearing"])
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
    test = BenderConfig(Path(__file__).parent / "../build-configs/debug.conf")
    # test = BenderConfig()
    print(test.bracket_depth, test.bracket_height, test.bracket_width)
    print(test.sidewall_width)
    for connector in test.connectors:
        print(connector.tube.inner_diameter)
    print(test.default_connector.diameter)
    print(test.wheel.radius, test.wheel.bearing.depth)
