


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location, Locations,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector, sweep)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig
from geometry_utils import point_distance, y_point_to_angle, x_point_to_angle, find_related_point_by_distance, distance_to_circle_edge
from curvebar import curvebar
from bank_config import BankConfig

bracket_configuration = BankConfig()

def sweep_cut() -> Part:
    arc_radius = point_distance(bracket_configuration.frame_click_sphere_point,
                bracket_configuration.frame_clip_point)
    x_distance = bracket_configuration.frame_clip_point.x + \
        abs(bracket_configuration.frame_click_sphere_point.x)
    top_angle = 180-x_point_to_angle(radius=arc_radius, x_position=x_distance)
    bottom_angle = 180-y_point_to_angle(radius=arc_radius,
    y_position=abs(bracket_configuration.frame_clip_point.y))
    cut_radius = bracket_configuration.frame_click_sphere_radius + bracket_configuration.top_frame_bracket_tolerance
    print(top_angle, bottom_angle)
    with BuildPart() as cut:
        with BuildLine():
            ln=CenterArc(center=(bracket_configuration.frame_clip_point.x,
                        bracket_configuration.frame_clip_point.y),
                        radius=arc_radius, start_angle=bottom_angle,
                        arc_size=-bottom_angle+top_angle)
        with BuildSketch(Plane(origin=ln @ 0, z_dir=ln % 0)):
            Circle(cut_radius)
        sweep()
        with BuildPart(Location((bracket_configuration.frame_click_sphere_point.x,
                        bracket_configuration.frame_click_sphere_point.y,
                        0))):
            Sphere(radius=cut_radius)
    return cut.part

def divot() -> Part:
    cut_radius = bracket_configuration.frame_click_sphere_radius + bracket_configuration.top_frame_bracket_tolerance
    with BuildPart(Location((0,0,0),(0,90,0)), mode=Mode.PRIVATE) as prvate:
        Cylinder(radius=cut_radius, height=bracket_configuration.bracket_width*2)
    with BuildPart(Location((0,0,0),(0,0,0)), mode=Mode.PRIVATE) as bump:
        add(private)
    
    return bump.part

    
with BuildPart() as main:
    #Cylinder(bracket_configuration.bracket_width/2, bracket_configuration.bracket_depth, align=(Align.CENTER, Align.CENTER, Align.MAX))
    with Locations(Location((0,0,0)), Location((0,0,-bracket_configuration.bracket_depth))):
        add(divot())
        
    # add(sweep_cut())
    # add(sweep_cut().move(Location((0,0,-bracket_configuration.bracket_depth))))

show(main)