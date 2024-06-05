"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Axis, Box, Align, Cylinder,
                export_stl, offset, Polyline, Rectangle)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import curvebar

frame_configuration = BankConfig()

from filament_bracket import bottom_frame

angled_distance = (frame_configuration.wheel_radius+frame_configuration.connector_radius+frame_configuration.minimum_thickness)*sqrt(2)/2

with BuildPart() as demo:
    #add(bottom_frame().rotate(Axis.X, angle=90). \
    #    move(Location((0,frame_configuration.bracket_depth/2,0))))
    with BuildPart(Location((-frame_configuration.bracket_width/2-frame_configuration.top_frame_bracket_tolerance,0,0))):
        Box(frame_configuration.top_frame_wall_thickness,
            frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance*2,
            frame_configuration.bracket_height*.25,
            align=(Align.MAX, Align.CENTER, Align.MIN))
    with BuildPart(Location((0,frame_configuration.bracket_depth/2+frame_configuration.top_frame_bracket_tolerance+frame_configuration.top_frame_wall_thickness,-angled_distance/2+frame_configuration.bracket_height*.125), (90,0,0))):
        add(curvebar(frame_configuration.bracket_width+(frame_configuration.top_frame_bracket_tolerance+frame_configuration.top_frame_wall_thickness)*2,
             frame_configuration.bracket_height*.25, frame_configuration.top_frame_wall_thickness,
             angled_distance, 45).mirror(Plane.YZ))
    with BuildPart(Location((0,-frame_configuration.bracket_depth/2-frame_configuration.top_frame_bracket_tolerance,-angled_distance/2+frame_configuration.bracket_height*.125), (90,0,0))):
        add(curvebar(frame_configuration.bracket_width+(frame_configuration.top_frame_bracket_tolerance+frame_configuration.top_frame_wall_thickness)*2,
             frame_configuration.bracket_height*.25, frame_configuration.top_frame_wall_thickness,
             angled_distance, 45).mirror(Plane.YZ))
    with BuildPart():
        with BuildSketch(Location((angled_distance+frame_configuration.top_frame_bracket_tolerance*2,0,-angled_distance), (0,0,0))) as base:
            Rectangle(frame_configuration.top_frame_wall_thickness, frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance, align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((angled_distance+frame_configuration.top_frame_bracket_tolerance*2+frame_configuration.bracket_height*.25,0,-angled_distance+frame_configuration.bracket_height*.25), (0,0,0))):
            Rectangle(frame_configuration.top_frame_wall_thickness, frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance, align=(Align.MIN, Align.CENTER))
        loft()  
    with BuildPart(Location((-frame_configuration.bracket_width/2-frame_configuration.top_frame_wall_thickness-frame_configuration.top_frame_bracket_tolerance,0,0))):
        Box(frame_configuration.fillet_radius+frame_configuration.wheel_support_height,
            frame_configuration.bracket_depth+(frame_configuration.top_frame_bracket_tolerance+frame_configuration.top_frame_wall_thickness)*2,
            frame_configuration.top_frame_wall_thickness,
            align=(Align.MIN, Align.CENTER, Align.MAX))    
show(demo)
export_stl(demo.part, '../stl/frame_test.stl')