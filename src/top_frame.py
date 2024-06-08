"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import curvebar
from filament_bracket import bottom_frame, spoke_assembly, wheel_guide

frame_configuration = BankConfig()

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
                frame_configuration.top_frame_bracket_tolerance*2)
    part = support.part
    part.label = "support"
    return part

def frame_side() -> Part:
    """
    builds a side of the frame
    """
    with BuildPart() as cb:
        add(curvebar(frame_configuration.spoke_length,
              frame_configuration.spoke_bar_height,
              frame_configuration.top_frame_wall_thickness,
              frame_configuration.spoke_climb, frame_configuration.spoke_angle))
        extrude(cb.faces().sort_by(Axis.X)[-1], amount=10)
        bar_height = frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2+frame_configuration.top_frame_wall_thickness
        base_width = frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
                frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
                frame_configuration.tube_outer_radius +  bar_height/2 + frame_configuration.top_frame_wall_thickness
        with BuildPart(Location((-frame_configuration.spoke_length/2+base_width,-frame_configuration.top_frame_wall_thickness+bar_height,0))):
            add(curvebar(base_width*2,bar_height,
                frame_configuration.top_frame_wall_thickness,
                climb=bar_height).mirror(Plane.YZ))
        with BuildPart(mode=Mode.SUBTRACT):
            with BuildSketch():
                with BuildLine():
                    Polyline(
                        (right_bottom_intersection.x+frame_configuration.top_frame_bracket_tolerance, right_bottom_intersection.y),
                        (right_bottom_intersection.x+frame_configuration.top_frame_bracket_tolerance+frame_configuration.bracket_width,
                            right_bottom_intersection.y),
                        (right_top_intersection.x+frame_configuration.top_frame_bracket_tolerance+frame_configuration.bracket_width,
                            right_top_intersection.y),
                        (right_top_intersection.x+frame_configuration.top_frame_bracket_tolerance, right_top_intersection.y),
                        (right_bottom_intersection.x+frame_configuration.top_frame_bracket_tolerance, right_bottom_intersection.y)
                    )
                make_face()
            extrude(amount=frame_configuration.top_frame_wall_thickness)
    part = cb.part
    part.label = "frame side"
    return part.rotate(Axis.X, 90).move(
        Location((0,frame_configuration.top_frame_wall_thickness/2,0)))

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
            frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance*2,
            frame_configuration.top_frame_wall_thickness,
            align=(Align.MIN, Align.CENTER, Align.MAX))
    with GridLocations(0,frame_configuration.bracket_depth + \
                        frame_configuration.top_frame_wall_thickness + \
                    frame_configuration.top_frame_bracket_tolerance*2,
                    1,2):
        add(frame_side())


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
            frame_configuration.bracket_depth/2+frame_configuration.top_frame_bracket_tolerance,
            frame_configuration.frame_clip_point.y), (90,0,0))):
        add(support_bar(tolerance=frame_configuration.top_frame_bracket_tolerance))
    with BuildPart(Location((-frame_configuration.bracket_width/2 + \
                frame_configuration.fillet_radius + \
                frame_configuration.clip_length,
                0,
                -frame_configuration.frame_clip_point.y + \
                frame_configuration.spoke_bar_height/2)), mode=Mode.ADD):
        with GridLocations(0,frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance*2, 1, 2):
            Sphere(radius=frame_configuration.clip_length/4)
        with GridLocations(0,frame_configuration.bracket_depth+frame_configuration.top_frame_bracket_tolerance*2+frame_configuration.top_frame_wall_thickness*2, 1, 2):
            Sphere(radius=frame_configuration.clip_length/4)

def bracket():
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
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
