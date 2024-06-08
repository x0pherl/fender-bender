"""
module for all of the configuration required to build a filament bank
"""
from dataclasses import dataclass
from math import sqrt
from shapely.geometry import Point, LineString
from geometry_utils import distance_to_circle_edge, find_related_point_by_distance, find_related_point_by_y


@dataclass
class BankConfig:
    """
    A dataclass for configuration values for our filament bank
    """
    bearing_diameter: float = 12
    bearing_inner_diameter = 6.1
    bearing_shelf_diameter = 8.5
    bearing_depth: float = 4

    wheel_diameter:float = 70
    spoke_count: int = 5
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

    top_frame_wall_thickness = 2
    top_frame_bracket_tolerance = 0.2

    @property
    def frame_bracket_distance(self) -> tuple:
        """
        this is the distance to the bottom outmost corner of the exit bracket
        """
        #todo I don't like this value or name, it's confusing
        return(self.wheel_radius+self.connector_radius+self.minimum_thickness)*sqrt(2)/2



    @property
    def frame_clip_point(self) -> Point:
        """
        returns the x,y coordinates 1/2-way along the edge of the exit tube
        """
        right_bottom_bar_distance = -self.spoke_climb/2-self.spoke_bar_height/2
        right_top_intersection = self.find_point_along_right(right_bottom_bar_distance + self.spoke_bar_height)
    
        barpoint = find_related_point_by_y(right_top_intersection, -self.clip_length, 225)
        return Point(barpoint.x, barpoint.y)

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
    def spoke_length(self) -> float:
        return self.bracket_width + \
                    (self.top_frame_bracket_tolerance + \
                    self.top_frame_wall_thickness)*2

    @property
    def spoke_bar_height(self) -> float:
        return self.bracket_height/3
    
    @property
    def spoke_climb(self) -> float:
        return self.wheel_radius*.8
    
    @property
    def spoke_angle(self) -> float:
        return 45

    @property
    def clip_length(self) -> float:
        """
        returns the length of the clip that will hold in the bracket
        """
        #return (self.connector_radius-self.tube_outer_radius+self.minimum_thickness)
        return (self.bracket_depth/2-self.tube_outer_radius-min(self.wheel_radial_tolerance, self.wheel_lateral_tolerance))
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