"""
module for all of the configuration required to build a filament bank
"""
from dataclasses import dataclass
from math import sqrt
from build123d import CenterArc, Location, Locations
from shapely.geometry import Point, LineString
from geometry_utils import (distance_to_circle_edge, find_related_point_by_distance,
            point_distance, x_point_to_angle, y_point_to_angle)


@dataclass
class BankConfig:
    """
    A dataclass for configuration values for our filament bank
    """
    bearing_diameter: float = 12.1
    bearing_inner_diameter = 6.1
    bearing_shelf_diameter = 8.5
    bearing_depth: float = 4

    wheel_diameter:float = 70
    wheel_spoke_count: int = 5
    wheel_lateral_tolerance: float = 0.6
    wheel_radial_tolerance: float = 0.2

    minimum_structural_thickness = 4
    minimum_thickness = 1

    connector_diameter: float = 10.3
    connector_length: float = 6.7
    connector_thread_pitch:float = 1
    connector_thread_angle:float = 30
    connector_thread_interference = 0.4

    tube_inner_diameter = 3.5
    tube_outer_diameter = 6.5

    fillet_ratio = 4

    # filament_count = 3
    filament_count = 2

    # sidewall_section_depth = 240
    # extension_section_depth = 100
    sidewall_section_depth = 50
    extension_section_depth = 20
    solid_walls = False

    wall_thickness = 2
    frame_tongue_depth = 4
    frame_bracket_tolerance = 0.2

    frame_wall_bracket = True
    wall_bracket_screw_radius = 2.25
    wall_bracket_screw_head_radius=4.5

    @property
    def bottom_frame_depth(self) -> float:
        """
        the appropriate height for the bottom frame
        """
        return self.frame_tongue_depth + self.minimum_structural_thickness

    @property
    def buffer_frame_center_x(self) -> float:
        return (self.frame_back_distance + self.frame_front_bottom_distance) / 2

    @property
    def sidewall_center_x(self) -> float:
        return (self.frame_back_wall_center_distance + self.frame_front_wall_center_distance) / 2

    @property
    def bottom_frame_exterior_length(self) -> float:
        return abs(self.frame_front_bottom_distance) + \
            abs(self.frame_back_distance)

    @property
    def bottom_frame_interior_length(self) -> float:
        return abs(self.frame_back_wall_center_distance) + \
            abs(self.frame_front_wall_center_distance) - \
            self.wall_thickness - self.frame_bracket_tolerance - \
            self.minimum_thickness * 4

    @property
    def wall_window_apothem(self) -> float:
        return self.bracket_depth/3

    @property
    def front_wall_depth(self) -> float:
        """
        the calculated length for the front wall
        """
        return self.sidewall_section_depth - self.spoke_depth

    @property
    def back_wall_depth(self) -> float:
        """
        the calculated length for the front wall
        """
        return self.sidewall_section_depth - self.spoke_bar_height + \
                    self.frame_tongue_depth - self.frame_bracket_tolerance

    # @property
    # def frame_bracket_distance(self) -> tuple:
    #     """
    #     this is the distance to the bottom outmost corner of the exit bracket
    #     """
    #     #todo I don't like this value or name, it's confusing
    #     return(self.wheel_radius+self.connector_radius+self.minimum_thickness)*sqrt(2)/2

    @property
    def bracket_clip_point(self) -> Point:
        """
        returns the x,y coordinates 1/2-way along the edge of the exit tube
        which is where the filament buffer has a cut to clip into the top frame
        """
        # right_bottom_bar_distance = -self.spoke_climb/2-self.spoke_bar_height/2
        right_top_intersection = self.find_point_along_right(
                        -self.spoke_height/2 + self.spoke_bar_height)
        # right_bottom_bar_distance = -self.spoke_climb/2 - \
        #     self.spoke_bar_height/2
        # right_bottom_intersection = self.find_point_along_right(
        #                 right_bottom_bar_distance)
        # right_top_intersection = self.find_point_along_right(
        #                 right_bottom_bar_distance + self.spoke_bar_height)
        barpoint = find_related_point_by_distance(right_top_intersection,
                            self.clip_length-self.frame_bracket_tolerance/2, -135)
        return Point(barpoint.x, barpoint.y)
        #return Point(right_top_intersection.x, right_top_intersection.y)

    @property
    def frame_bracket_spacing(self) -> Point:
        """
        returns the distance between the sidewalls of the frame
        """
        return self.bracket_depth + self.wall_thickness + self.frame_bracket_tolerance * 2

    @property
    def sweep_cut_break_channel_locations(self) -> Locations:
        """
        The location (including angle) for the break point right before the click sphere
        """
        start_point = Point(self.frame_click_sphere_point.x,
                            self.frame_click_sphere_point.y - self.sweep_cut_width/2)
        base_angle = 180-x_point_to_angle(radius=self.sweep_cut_arc_radius,
                                x_position=start_point.x)
        return Locations(Location((start_point.x, start_point.y,
                                self.sweep_cut_width/2), (90,base_angle,0)),
                         Location((start_point.x, start_point.y,
                                self.bracket_depth-self.sweep_cut_width/2), (90,base_angle,0)))

    @property
    def sweep_cut_width(self) -> float:
        """
        the width (diameter) for the sphere and the sweep cut for the click bracket
        """
        return (self.frame_click_sphere_radius + \
                        self.frame_bracket_tolerance) * 2

    @property
    def sweep_cut_arc_radius(self) -> float:
        """
        the radius for the sweep cut (the distance from the front clip bar
        to the rear sphere clip point)
        """

        return point_distance(self.frame_click_sphere_point,
                self.bracket_clip_point)

    @property
    def sweep_cut_top_angle(self) -> float:
        """
        the angle from the front clip bar to the rear sphere clip point
        """
        x_distance = self.bracket_clip_point.x + \
            abs(self.frame_click_sphere_point.x)
        return 180-x_point_to_angle(radius=self.sweep_cut_arc_radius, x_position=x_distance)

    @property
    def sweep_cut_arc(self) -> CenterArc:
        """
        The complete arc for the click sphere to pass through on the bracket
        """

        arc_radius = point_distance(self.frame_click_sphere_point,
                self.bracket_clip_point)
        x_distance = self.bracket_clip_point.x + \
            abs(self.frame_click_sphere_point.x)
        top_angle = 180-x_point_to_angle(radius=arc_radius, x_position=x_distance)
        bottom_angle = 180-y_point_to_angle(radius=arc_radius,
        y_position=abs(self.bracket_clip_point.y))

        return CenterArc(center=(self.bracket_clip_point.x,
                        self.bracket_clip_point.y),
                        radius=arc_radius, start_angle=bottom_angle,
                        arc_size=-bottom_angle+top_angle)

    @property
    def frame_click_sphere_point(self) -> Point:
        """
        the x / y coordinates for the snap fit points
        """
        return Point(-self.bracket_width/2 + \
                        self.fillet_radius + \
                        self.clip_length,
                        -self.bracket_clip_point.y + \
                        self.spoke_bar_height/2)

    @property
    def frame_back_distance(self) -> float:
        """the distance from the center point to the back of the frame"""
        return -self.bracket_width/2 - \
                        self.frame_bracket_tolerance - \
                            self.minimum_structural_thickness * 2
    @property
    def frame_front_bottom_distance(self) -> float:
        """the distance from the center point to the front of the frame along the bottom"""
        right_bottom_intersection = self.find_point_along_right(
                        -self.spoke_height/2)
        return right_bottom_intersection.x + self.minimum_structural_thickness*2
    @property
    def frame_back_wall_center_distance(self) -> float:
        """the distance from the center of the frame to the center of the back wall"""
        return self.frame_back_distance + \
                    self.frame_back_foot_length + \
                    (self.wall_thickness+self.frame_bracket_tolerance)/2

    @property
    def frame_front_wall_center_distance(self) -> float:
        """the distance from the center of the frame to the center of the front wall"""
        right_bottom_intersection = self.find_point_along_right(
                        -self.spoke_height/2)
        return right_bottom_intersection.x + self.minimum_structural_thickness + \
                self.wall_thickness/2 + self.frame_bracket_tolerance

    @property
    def frame_back_foot_length(self) -> float:
        """
        the x dimension of the back foot of the frame
        """
        return self.minimum_structural_thickness*2

    @property
    def frame_click_sphere_radius(self) -> Point:
        """
        the radius for the snap fit points
        """
        return self.clip_length/3

    @property
    def top_frame_interior_width(self) -> float:
        """
        the overall interior width of the top frame
        """
        return ((self.bracket_depth + \
            self.wall_thickness + \
            self.frame_bracket_tolerance*2) * \
            self.filament_count) - \
            self.wall_thickness

    @property
    def frame_exterior_width(self) -> float:
        """
        the overall interior width of the top frame
        """
        return self.top_frame_interior_width + \
            (( self.minimum_structural_thickness + self.wall_thickness) *2)

    @property
    def exit_tube_entry_point(self) -> Point:
        """
        returns the x,y coordinates where the filament enters the outbound tube
        """
        angular_distance = self.wheel_radius*sqrt(2)/2
        return Point(angular_distance, -angular_distance)

    @property
    def exit_tube_exit_point(self) -> Point:
        """
        returns the x,y coordinates where the filament enters the outbound tube
        """
        return find_related_point_by_distance(self.exit_tube_entry_point, self.tube_length, 45)

    @property
    def connection_foundation_mid(self) -> float:
        """
        returns the distance from an edge to the
        midpoint for the foundation box supporting a tube/connector
        """
        return self.bracket_depth/2

    def find_point_along_right(self, y_point) -> Point:
        """
        returns the rightmost point of bracket based on a y value
        errors if lower than the right connector foundation or higher
        than the bracket
        """
        top_of_foundation = find_related_point_by_distance(self.exit_tube_exit_point,
                                        self.connection_foundation_mid, 135)
        base_of_foundation = find_related_point_by_distance(self.exit_tube_entry_point,
                                        self.connection_foundation_mid, -45)
        outer_top_of_foundation = find_related_point_by_distance(self.exit_tube_exit_point,
                                        self.connection_foundation_mid, -45)
        right_foundation_boundary = LineString([(base_of_foundation.x, base_of_foundation.y),
                        (outer_top_of_foundation.x, outer_top_of_foundation.y)])
        right_tip_boundary = LineString([(top_of_foundation.x, top_of_foundation.y),
                         (outer_top_of_foundation.x, outer_top_of_foundation.y)])
        y_line = LineString([(-self.bracket_width, y_point), (self.bracket_width, y_point)])
        if self.bracket_height >= y_point >= top_of_foundation.y:
            return self.bracket_width/2
        elif top_of_foundation.y > y_point >= outer_top_of_foundation.y:
            return y_line.intersection(right_tip_boundary)
        elif y_point >= base_of_foundation.y:
            return y_line.intersection(right_foundation_boundary)
        raise ValueError("unable to calculate the rightmost point at this distance")

    @property
    def sidewall_width(self) -> float:
        """
        returns the appropriate width for the sidewalls
        """
        right_bottom_intersection = self.find_point_along_right(
            -self.spoke_height/2)
        return self.bracket_width/2 + \
                right_bottom_intersection.x + \
                self.minimum_structural_thickness - \
                self.wall_thickness



    #todo -- spoke_length is a confusing name for this
    @property
    def spoke_length(self) -> float:
        return self.bracket_width + \
                    (self.frame_bracket_tolerance + \
                    self.wall_thickness)*2

    @property
    def spoke_bar_height(self) -> float:
        return self.bracket_height/3

    @property
    def spoke_depth(self) -> float:
        """
        this is the overall distance of the angled bar of the top frame
        """
        return self.wheel_radius*.8

    @property
    def spoke_angle(self) -> float:
        return 45

    @property
    def spoke_height(self) -> float:
        return self.spoke_depth + self.spoke_bar_height

    @property
    def clip_length(self) -> float:
        """
        returns the length of the clip that will hold in the bracket
        """
        #return (self.connector_radius-self.tube_outer_radius+self.minimum_thickness)
        return (self.bracket_depth/2-self.tube_outer_radius - \
                min(self.wheel_radial_tolerance, self.wheel_lateral_tolerance))

    @property
    def bearing_shelf_radius(self) -> float:
        """
        returns the radius of the bearing shelf
        """
        return self.bearing_shelf_diameter/2

    @property
    def bearing_shelf_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (self.bracket_depth - self.bearing_depth)/2

    @property
    def wheel_radius(self) -> float:
        """
        returns the radius of the wheel
        """
        return self.wheel_diameter/2

    @property
    def bearing_radius(self) -> float:
        """
        returns the radius of the bearing
        """
        return self.bearing_diameter/2

    @property
    def bearing_inner_radius(self) -> float:
        """
        returns the inner_radius of the bearing
        """
        return self.bearing_inner_diameter/2

    @property
    def connector_radius(self) -> float:
        """
        returns the radius of the connector
        """
        return self.connector_diameter/2

    @property
    def tube_inner_radius(self) -> float:
        """
        returnes the inner radius of the tube
        """
        return self.tube_inner_diameter/2

    @property
    def tube_outer_radius(self) -> float:
        """
        returnes the outer radius of the tube
        """
        return self.tube_outer_diameter/2

    @property
    def tube_length(self) -> float:
        """returns the length of the diagonal tube segment"""
        inner_edge_distance = self.wheel_radius-(self.connector_radius+self.minimum_thickness)
        inner_angled_distance = inner_edge_distance*sqrt(2)/2
        return distance_to_circle_edge(self.bracket_width/2,
                (inner_angled_distance, -inner_angled_distance), 45)

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
        #todo 5 feels like a magic value here
        return self.wheel_diameter+self.wheel_support_height*5+self.fillet_radius*2

    @property
    def bracket_height(self) -> float:
        """
        returns the height of the bracket
        """
        return self.wheel_radius+self.wheel_radial_tolerance+self.minimum_structural_thickness*2

    @property
    def bracket_depth(self) -> float:
        """
        returns the depth of the bracket
        """
        return max(self.bearing_depth+self.wheel_lateral_tolerance + \
                   self.minimum_structural_thickness*2,
                   self.connector_diameter+self.minimum_thickness*2,
                   self.tube_outer_diameter+self.minimum_thickness*2)

    @property
    def fillet_radius(self) -> float:
        """
        returns the fillet radis for bracket parts
        """
        return self.bracket_depth/self.fillet_ratio

    @property
    def wheel_support_height(self) -> float:
        """
        returns the appropriate height for the bearing shelf
        """
        return (self.bracket_depth - self.bearing_depth - self.wheel_lateral_tolerance)/2
