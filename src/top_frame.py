"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt
#from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align,
                export_stl, Rectangle, Sphere)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import curvebar
from filament_bracket import bottom_frame, spoke_assembly, wheel_guide

frame_configuration = BankConfig()
# angled_distance = (frame_configuration.wheel_radius+frame_configuration.connector_radius+frame_configuration.minimum_thickness)*sqrt(2)/2

def support_bar(tolerance = 0) -> Part:
    """
    creates the bar to support the clip that holds the bracket in place
    """
    with BuildPart() as support:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((0,0),
                                radius=frame_configuration.clip_length - tolerance,
                                start_angle=45, arc_size=90)
                Line(arc @ 1, (0,0))
                Line(arc @ 0, (0,0))
            make_face()
        extrude(amount=frame_configuration.bracket_depth + \
                frame_configuration.top_frame_bracket_tolerance)
    part = support.part
    part.label = "support"
    return part

with BuildPart() as demo:
    right_bottom_bar_distance = -frame_configuration.spoke_climb/2 - \
        frame_configuration.spoke_bar_height/2
    right_bottom_intersection = frame_configuration.find_point_along_right(
                    right_bottom_bar_distance)
    right_top_intersection = frame_configuration.find_point_along_right(
                    right_bottom_bar_distance + frame_configuration.spoke_bar_height)
    with BuildPart(Location((-frame_configuration.bracket_width/2 - \
                    frame_configuration.top_frame_bracket_tolerance - \
                        frame_configuration.top_frame_wall_thickness,0,0))):
        Box(frame_configuration.top_frame_wall_thickness,
            frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance*2,
            frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2,
            align=(Align.MIN, Align.CENTER, Align.MIN))
        Box(frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
            frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
            frame_configuration.tube_outer_radius,
            frame_configuration.bracket_depth+(frame_configuration.top_frame_bracket_tolerance + \
            frame_configuration.top_frame_wall_thickness)*2,
            frame_configuration.top_frame_wall_thickness,
            align=(Align.MIN, Align.CENTER, Align.MAX))
    with BuildPart(Location((-frame_configuration.bracket_width/2 - \
                    frame_configuration.top_frame_bracket_tolerance - \
                    frame_configuration.top_frame_wall_thickness,
                    frame_configuration.bracket_depth/2 + \
                    frame_configuration.top_frame_bracket_tolerance,0))):
        Box(frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
            frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
            frame_configuration.tube_outer_radius,
            frame_configuration.top_frame_wall_thickness,
            frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2,
            align=(Align.MIN, Align.MIN, Align.MIN))
    with BuildPart(Location((-frame_configuration.bracket_width/2 - \
                    frame_configuration.top_frame_bracket_tolerance - \
                    frame_configuration.top_frame_wall_thickness,
                    -frame_configuration.bracket_depth/2 - \
                    frame_configuration.top_frame_bracket_tolerance,0))):
        Box(frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
            frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
            frame_configuration.tube_outer_radius,
            frame_configuration.top_frame_wall_thickness,
            frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2,
            align=(Align.MIN, Align.MAX, Align.MIN))

    with BuildPart(Location((0,frame_configuration.bracket_depth/2 + \
                             frame_configuration.top_frame_bracket_tolerance + \
                                frame_configuration.top_frame_wall_thickness,
                                0), (90,0,0))) as cb_back:
        add(curvebar(frame_configuration.spoke_length,
              frame_configuration.spoke_bar_height,
              frame_configuration.top_frame_wall_thickness,
              frame_configuration.spoke_climb, frame_configuration.spoke_angle))
        extrude(cb_back.faces().sort_by(Axis.X)[-1], amount=10)


    with BuildPart(Location((0,-frame_configuration.bracket_depth/2 - \
                             frame_configuration.top_frame_bracket_tolerance,
                             0), (90,0,0))) as cb_front:
        add(curvebar(frame_configuration.spoke_length,
              frame_configuration.spoke_bar_height,
              frame_configuration.top_frame_wall_thickness,
              frame_configuration.spoke_climb, frame_configuration.spoke_angle))
        extrude(cb_front.faces().sort_by(Axis.X)[-1], amount=10)
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(Location((right_bottom_intersection.x + \
                        frame_configuration.top_frame_bracket_tolerance,0,
                        right_bottom_intersection.y), (0,0,0))) as base:
            Rectangle(frame_configuration.bracket_width,
                      frame_configuration.bracket_depth*2 + \
                        frame_configuration.top_frame_bracket_tolerance*2,
                      align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((right_top_intersection.x + \
                        frame_configuration.top_frame_bracket_tolerance,0,
                        right_top_intersection.y), (0,0,0))):
            Rectangle(frame_configuration.bracket_width,
                    frame_configuration.bracket_depth*2 + \
                    frame_configuration.top_frame_bracket_tolerance*2,
                    align=(Align.MIN, Align.CENTER))
        loft()

    with BuildPart():
        with BuildSketch(Location((right_bottom_intersection.x + \
                    frame_configuration.top_frame_bracket_tolerance,0,
                    right_bottom_intersection.y), (0,0,0))) as base:
            Rectangle(frame_configuration.top_frame_wall_thickness,
                    frame_configuration.bracket_depth + \
                    (frame_configuration.top_frame_wall_thickness + \
                    frame_configuration.top_frame_bracket_tolerance)*2,
                    align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((right_top_intersection.x +\
                    frame_configuration.top_frame_bracket_tolerance,0,
                    right_top_intersection.y), (0,0,0))):
            Rectangle(frame_configuration.top_frame_wall_thickness,
                    frame_configuration.bracket_depth + \
                    (frame_configuration.top_frame_wall_thickness + \
                    frame_configuration.top_frame_bracket_tolerance)*2,
                    align=(Align.MIN, Align.CENTER))
        loft()
    fillet(demo.edges(),
           frame_configuration.top_frame_wall_thickness/frame_configuration.fillet_ratio)
    with BuildPart(Location((frame_configuration.frame_clip_point.x + \
            frame_configuration.top_frame_bracket_tolerance,
            frame_configuration.bracket_depth/2 + \
            frame_configuration.top_frame_bracket_tolerance,
            frame_configuration.frame_clip_point.y), (90,0,0))):
        add(support_bar(tolerance=frame_configuration.top_frame_bracket_tolerance))
    with BuildPart(Location((-frame_configuration.bracket_width/2 + \
                frame_configuration.fillet_radius + \
                frame_configuration.clip_length,
                frame_configuration.bracket_depth/2 - \
                frame_configuration.top_frame_bracket_tolerance,
                -frame_configuration.frame_clip_point.y + \
                frame_configuration.spoke_bar_height/2)), mode=Mode.ADD):
        Sphere(radius=frame_configuration.clip_length/3)
    with BuildPart(Location((-frame_configuration.bracket_width/2 + \
                frame_configuration.fillet_radius + \
                frame_configuration.clip_length,
                -frame_configuration.bracket_depth/2 + \
                frame_configuration.top_frame_bracket_tolerance,
                -frame_configuration.frame_clip_point.y + \
                frame_configuration.spoke_bar_height/2)), mode=Mode.ADD):
        Sphere(radius=frame_configuration.clip_length/3)

def bracket():
    with BuildPart() as show_bracket:
        add(bottom_frame().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(spoke_assembly().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(wheel_guide().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
    part = show_bracket
    part.label = "bracket"
    return part

show(demo)
#show(demo, bracket())

export_stl(demo.part, '../stl/frame_test.stl')
