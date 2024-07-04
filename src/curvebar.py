"""
utility for creating a bar with a zig-zag shape
"""
from build123d import (BuildPart, BuildSketch, BuildLine, Polyline,
                       make_face, fillet, extrude, Axis, add, Location,
                       Until, Plane, Part, Rectangle, Align, Box, loft)
from geometry_utils import find_angle_intersection
from bank_config import BankConfig

frame_configuration = BankConfig()

def curvebar(length, bar_width, depth, climb, angle=45):
    """
    returns a zig-zag ish line
    """
    with BuildPart() as curve_part:
        with BuildSketch() as sketch:
            x_distance = find_angle_intersection(climb/2, angle)
            angled_bar_width = find_angle_intersection(bar_width/2, angle)/2
            with BuildLine():
                Polyline(
                    (length/2,-climb/2+bar_width/2),
                    (length/2,-climb/2-bar_width/2),
                    (x_distance+angled_bar_width-bar_width/2,-climb/2-bar_width/2),
                    (-x_distance+angled_bar_width-bar_width/2,climb/2-bar_width/2),
                    (-length/2,climb/2-bar_width/2),
                    (-length/2,climb/2+bar_width/2),
                    (-x_distance-angled_bar_width+bar_width/2,climb/2+bar_width/2),
                    (x_distance-angled_bar_width+bar_width/2, -climb/2+bar_width/2),
                    (length/2,-climb/2+bar_width/2),
                )
            make_face()
            fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                    minimum=-length/2,
                    maximum=length/2,
                    inclusive=(False, False)), bar_width/2)
        extrude(amount=depth)
    curve = curve_part.part
    curve.label = "curvebar"
    return curve

def frame_side(thickness=frame_configuration.wall_thickness, extend=0) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    extend: extends each side of the frame side out by this additional ammount
    """
    with BuildPart() as side:
        with BuildPart() as cb:
            add(curvebar(frame_configuration.spoke_length/2,
                frame_configuration.spoke_bar_height,
                thickness,
                frame_configuration.spoke_climb, 
                frame_configuration.spoke_angle).rotate(Axis.X, 90) \
                    .move(Location((0,thickness/2,0))))
        add(angle_bar(thickness).move(Location(
            (-frame_configuration.minimum_structural_thickness+extend,0,0))))
        extrude(cb.faces().sort_by(Axis.X)[-1], until=Until.NEXT)
        extrude(cb.faces().sort_by(Axis.X)[0], amount=frame_configuration.spoke_length/4+extend)
        bar_height = frame_configuration.spoke_climb/2 -\
            frame_configuration.spoke_bar_height/2
        base_width = frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
                frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
                frame_configuration.tube_outer_radius +  \
                bar_height/2 + frame_configuration.wall_thickness
        with BuildPart(Location((-frame_configuration.spoke_length/2+base_width*1.25,
                                 0,bar_height))) as bottom_curve:
            add(curvebar(base_width*2.5,bar_height,
                thickness,
                climb=bar_height).mirror(Plane.YZ).rotate(Axis.X, 90) \
                        .move(Location((0,thickness/2,0))))
            if extend > 0:
                extrude(bottom_curve.faces().sort_by(Axis.X)[0], amount=extend)

    part = side
    part.label = "Frame Side"
    return part

def angle_bar(depth: float) -> Part:
    right_bottom_intersection = frame_configuration.find_point_along_right(
            -frame_configuration.spoke_height/2)
    right_top_intersection = frame_configuration.find_point_along_right(
                    -frame_configuration.spoke_height/2 + frame_configuration.spoke_bar_height)
    with BuildPart() as foot_bar:
        with BuildSketch(Location((right_bottom_intersection.x + \
                    frame_configuration.top_frame_bracket_tolerance,0,
                    right_bottom_intersection.y), (0,0,0))) as base:
            Rectangle(frame_configuration.minimum_structural_thickness*2,
                    depth,
                    align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((right_top_intersection.x +\
                    frame_configuration.top_frame_bracket_tolerance,0,
                    right_top_intersection.y), (0,0,0))):
            Rectangle(frame_configuration.minimum_structural_thickness*2,
                    depth,
                    align=(Align.MIN, Align.CENTER))
        loft()
    part = foot_bar.part
    part.label = "angle bar"
    return part

def back_bar(depth: float) -> Part:
    with BuildPart(Location((-frame_configuration.bracket_width/2 - \
                        frame_configuration.top_frame_bracket_tolerance,0,
                        -frame_configuration.wall_thickness))) as bar:
        Box(frame_configuration.minimum_structural_thickness,
            depth,
            frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2+frame_configuration.wall_thickness,
            align=(Align.MAX, Align.CENTER, Align.MIN))
    part = bar.part
    part.label = "back bar"
    return part
