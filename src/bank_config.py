"""
module for all of the configuration required to build a filament bank
"""

import configparser
from dataclasses import dataclass, fields
from enum import Flag, auto
from math import sqrt
from pathlib import Path

from shapely.geometry import Point

from geometry_utils import distance_to_circle_edge, point_distance


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


@dataclass
class BankConfig:
    """
    A dataclass for configuration values for our filament bank
    """

    bearing_diameter: float = 12.1
    bearing_inner_diameter:float = 6.1
    bearing_shelf_diameter:float = 8.5
    bearing_depth: float = 4

    wheel_diameter: float = 70
    wheel_spoke_count: int = 5
    wheel_lateral_tolerance: float = 0.6
    wheel_radial_tolerance: float = 0.2

    minimum_structural_thickness:float = 4
    minimum_thickness:float = 1

    connector_diameter: float = 10.3
    connector_length: float = 6.7
    connector_thread_pitch: float = 1
    connector_thread_angle: float = 30
    connector_thread_interference = 0.4

    tube_inner_diameter:float = 3.5
    tube_outer_diameter:float = 6.5

    fillet_ratio:float = 4
    tolerance:float = 0.2
    filament_count:int = 3

    frame_chamber_depth:float = 170 #240
    solid_walls:bool = False
    wall_window_apothem:float = 8
    wall_window_bar_thickness:float = 1.5
    wall_thickness:float = 3

    frame_tongue_depth:float = 4
    frame_lock_pin_tolerance:float = 0.3
    frame_lock_style:LockStyle = LockStyle.BOTH

    frame_clip_depth_offset:float = 10

    frame_style:FrameStyle = FrameStyle.HYBRID
    wall_bracket_screw_radius:float = 2.25
    wall_bracket_screw_head_radius:float = 4.5
    wall_bracket_screw_head_sink:float = 1.4
    wall_bracket_post_count:int = 3

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
        return (self.frame_chamber_depth - self.frame_connector_depth - self.frame_base_depth - \
             (self.frame_bracket_exterior_radius-self.wheel_radius))/2

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
            - self.wheel_radius
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
        return point_distance(
            Point(0, 0),
            Point(
                self.wheel_radius - self.bracket_depth / 2, self.bracket_height
            ),
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
    def frame_click_sphere_radius(self) -> Point:
        """
        the radius for the snap fit points
        """
        return self.minimum_thickness

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
        return distance_to_circle_edge(
            radius=self.wheel_radius
            + self.wheel_radial_tolerance
            + self.minimum_thickness,
            point=(self.wheel_radius - self.tube_outer_radius, 0),
            angle=90,
        )

    @property
    def sidewall_width(self) -> float:
        """
        returns the appropriate width for the sidewalls
        """
        return (
            self.wheel_diameter
            + (
                self.wheel_radial_tolerance
                + self.connector_diameter
                + self.fillet_radius
                + self.wall_thickness
                + self.tolerance
            )
            * 2
        )

    @property
    def bearing_shelf_radius(self) -> float:
        """
        returns the radius of the bearing shelf
        """
        return self.bearing_shelf_diameter / 2

    @property
    def bearing_shelf_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (self.bracket_depth - self.bearing_depth) / 2

    @property
    def wheel_radius(self) -> float:
        """
        returns the radius of the wheel
        """
        return self.wheel_diameter / 2

    @property
    def bearing_radius(self) -> float:
        """
        returns the radius of the bearing
        """
        return self.bearing_diameter / 2

    @property
    def bearing_inner_radius(self) -> float:
        """
        returns the inner_radius of the bearing
        """
        return self.bearing_inner_diameter / 2

    @property
    def connector_radius(self) -> float:
        """
        returns the radius of the connector
        """
        return self.connector_diameter / 2

    @property
    def tube_inner_radius(self) -> float:
        """
        returnes the inner radius of the tube
        """
        return self.tube_inner_diameter / 2

    @property
    def tube_outer_radius(self) -> float:
        """
        returnes the outer radius of the tube
        """
        return self.tube_outer_diameter / 2

    @property
    def rim_thickness(self) -> float:
        """
        returns the thickness of the rim
        """
        return self.bearing_depth

    @property
    def bracket_width(self) -> float:
        """
        returns the width of the bracket
        """
        return (
            self.wheel_diameter
            + self.wheel_support_height * 2
            + self.minimum_structural_thickness * 3
            + self.fillet_radius * 2
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
        return (
            self.wheel_radius
            + self.wheel_radial_tolerance
            + self.minimum_structural_thickness * 2
        )

    @property
    def bracket_depth(self) -> float:
        """
        returns the depth of the bracket
        """
        return max(
            self.bearing_depth
            + self.wheel_lateral_tolerance
            + self.minimum_structural_thickness * 2,
            self.connector_diameter + self.minimum_thickness * 2,
            self.tube_outer_diameter + self.minimum_thickness * 2,
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
            - self.bearing_depth
            - self.wheel_lateral_tolerance
        ) / 2

    def __init__(self, file_path: str = None, **kwargs):
        """initialize the configuration"""
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            try:
                self.load_config(file_path)
            except Exception as e:
                raise ValueError(f"Error loading configuration from {file_path}: {e}") from e
        else:
            for field in fields(self):
                setattr(self, field.name, kwargs.get(field.name, field.default))

    def load_config(self, file_path: str):
        """
        loads a configuration from a file
        """
        config = configparser.ConfigParser()
        config.read(file_path)
        config_dict = {}
        for field in fields(BankConfig):
            value = config['BankConfig'][field.name]
            if field.type == int:
                config_dict[field.name] = int(value)
            elif field.type == float:
                config_dict[field.name] = float(value)
            elif field.type == bool:
                config_dict[field.name] = value.lower() in ('true', 'yes', '1')
            elif field.type == LockStyle:
                config_dict[field.name] = LockStyle[value.upper()]
            elif field.type == FrameStyle:
                config_dict[field.name] = FrameStyle[value.upper()]
            else:
                config_dict[field.name] = value

        for key, value in config_dict.items():
            setattr(self, key, value)

if __name__ == '__main__':
    test = BankConfig("C:\\Users\\xopher\\code\\3d-print\\filament-bank\\src\\default.conf")
    # test = BankConfig('default.conf')
    print(test.frame_hanger_offset)
    print(test.filament_count)
    print(test.sidewall_straight_depth)
