"""
Useful geometry utilities for design
"""
from math import sqrt, radians, cos, sin, atan2, degrees, tan
from shapely.geometry import Point

def find_angle_intersection(known_distance, angle):
    """
    given an angle and the length along the adjascent axis, 
    calculates the distance along the opposite axis
    """
    return known_distance * tan(radians(angle))

def find_related_point_by_distance(origin:Point, distance:float, angle:float) -> Point:
    """
    from a given origin, find the point along a given angle and distance
    """
    return Point(origin.x + (distance * cos(radians(angle))),
            origin.y + (distance * sin(radians(angle))))

def find_related_point_by_y(origin:Point, y_distance:float, angle:float) -> Point:
    """
    from a given origin, find the point along a given angle using the
    y distance from the origin
    """
    total_distance = y_distance / sin(radians(angle))
    return Point(origin.x + total_distance * cos(radians(angle)), origin.y + y_distance)

def find_related_point_by_x(origin:Point, x_distance:float, angle:float) -> Point:
    """
    from a given origin, find the point along a given angle using the
    x distance from the origin
    """
    total_distance = x_distance / cos(radians(angle))
    return Point(origin.x + x_distance, origin.y + total_distance * sin(radians(angle)))

def point_distance(origin: Point, destination: Point) -> float:
    """
    returns the distance between two points
    """
    return origin.distance(destination)

def x_point_to_angle(radius, x_position) -> float:
    """
    for a circle with a given radius, given an x axis position,
    returns the angle at which an intersection will occur with the
    circle's edge
    """
    y_position = distance_to_circle_edge(radius, (x_position, 0), 90)
    return degrees(atan2(y_position, x_position))

def y_point_to_angle(radius, y_position) -> float:
    """
    for a circle with a given radius, given a y axis position,
    returns the angle at which an intersection will occur with the
    circle's edge
    """
    x_position = distance_to_circle_edge(radius, (0, y_position), 90)
    return degrees(atan2(y_position, x_position))

def distance_to_circle_edge(radius, point, angle) -> float:
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
        return None  # No real intersection, should not happen as point is within the circle

    # Solve the quadratic equation for t
    t1 = (-b + sqrt(discriminant)) / (2 * a)
    t2 = (-b - sqrt(discriminant)) / (2 * a)

    # We need the positive t, as we are extending outwards
    t = max(t1, t2)

    return t
