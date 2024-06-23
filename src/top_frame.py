"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline, Until)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import curvebar
from shapely.geometry import Point
from geometry_utils import find_related_point_by_distance
from filament_bracket import bottom_frame, spoke_assembly, wheel_guide

frame_configuration = BankConfig()

def support_bar(tolerance = 0) -> Part:
    """
    creates the bar to support the clip that holds the bracket in place
    """
    center = find_related_point_by_distance(Point(0,0), frame_configuration.clip_length - tolerance, -135)
    with BuildPart() as support:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((center.x,center.y),
                                radius=frame_configuration.clip_length - tolerance,
                                start_angle=45, arc_size=90)
                Line(arc @ 1, (center.x,center.y))
                Line(arc @ 0, (center.x,center.y))
            make_face()
        extrude(amount=frame_configuration.top_frame_interior_width + \
                frame_configuration.wall_thickness/frame_configuration.fillet_ratio*2)
    part = support.part
    part.label = "support"
    return part

def frame_side(thickness=frame_configuration.wall_thickness) -> Part:
    """
    builds a side of the frame
    """
    with BuildPart() as side:
        with BuildPart() as cb:
            add(curvebar(frame_configuration.spoke_length/2,
                frame_configuration.spoke_bar_height,
                thickness,
                frame_configuration.spoke_climb, frame_configuration.spoke_angle).rotate(Axis.X, 90).move(Location((0,thickness/2,0))))
        add(angle_bar(thickness).move(Location((-frame_configuration.minimum_structural_thickness,0,0))))
        extrude(cb.faces().sort_by(Axis.X)[-1], until=Until.NEXT)
        extrude(cb.faces().sort_by(Axis.X)[0], amount=frame_configuration.spoke_length/4)
        bar_height = frame_configuration.spoke_climb/2 -\
            frame_configuration.spoke_bar_height/2
        base_width = frame_configuration.fillet_radius+frame_configuration.minimum_thickness + \
                frame_configuration.wheel_support_height+frame_configuration.connector_radius - \
                frame_configuration.tube_outer_radius +  bar_height/2 + frame_configuration.wall_thickness
        with BuildPart(Location((-frame_configuration.spoke_length/2+base_width*1.25,
                                 0,bar_height))):
            add(curvebar(base_width*2.5,bar_height,
                thickness,
                climb=bar_height).mirror(Plane.YZ).rotate(Axis.X, 90).move(Location((0,thickness/2,0))))

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
            Rectangle(frame_configuration.minimum_structural_thickness,
                    depth,
                    align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((right_top_intersection.x +\
                    frame_configuration.top_frame_bracket_tolerance,0,
                    right_top_intersection.y), (0,0,0))):
            Rectangle(frame_configuration.minimum_structural_thickness,
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

def demo() -> Part:
    with BuildPart() as test:
        add(frame_side())
    return test.part

def frame() -> Part:
    with BuildPart() as top_frame:
        
        right_bottom_intersection = frame_configuration.find_point_along_right(
                        -frame_configuration.spoke_height/2)
        right_top_intersection = frame_configuration.find_point_along_right(
                        -frame_configuration.spoke_height/2 + frame_configuration.spoke_bar_height)

        add(angle_bar(depth = frame_configuration.top_frame_exterior_width))
        add(back_bar(depth = frame_configuration.top_frame_exterior_width))
        with BuildPart(Location((-frame_configuration.bracket_width/2 - \
                        frame_configuration.top_frame_bracket_tolerance - \
                            frame_configuration.minimum_structural_thickness,0,0))) as back_drop:
            Box(frame_configuration.frame_back_foot_length,
                frame_configuration.top_frame_exterior_width,
                #todo this frame_bracket_tolerance*2 nonsense really bothers me track it down
                frame_configuration.spoke_climb-frame_configuration.spoke_bar_height/2+frame_configuration.top_frame_bracket_tolerance*2,
                align=(Align.MIN, Align.CENTER, Align.MAX))
        with GridLocations(0,frame_configuration.top_frame_interior_width+frame_configuration.minimum_structural_thickness, 1, 2):
           add(frame_side(frame_configuration.minimum_structural_thickness))
        fillet_edges = \
                top_frame.edges().filter_by_position(Axis.Y, minimum=frame_configuration.top_frame_exterior_width/2-.01, maximum=frame_configuration.top_frame_exterior_width/2+.02, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.Y, minimum=-frame_configuration.top_frame_exterior_width/2-.01, maximum=-frame_configuration.top_frame_exterior_width/2+.02, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=-frame_configuration.spoke_length/2-frame_configuration.minimum_structural_thickness-.01, maximum=-frame_configuration.spoke_length/2+.01, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=right_top_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.top_frame_bracket_tolerance-.01, maximum=right_top_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.top_frame_bracket_tolerance+.01, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=right_bottom_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.top_frame_bracket_tolerance-.01, maximum=right_bottom_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.top_frame_bracket_tolerance+.01, inclusive=(True,True))

        fillet(fillet_edges, frame_configuration.minimum_structural_thickness/frame_configuration.fillet_ratio)

        with BuildPart(Location((right_top_intersection.x +\
                    frame_configuration.top_frame_bracket_tolerance,
                    frame_configuration.top_frame_interior_width/2+frame_configuration.wall_thickness/frame_configuration.fillet_ratio,
                    right_top_intersection.y), (90,0,0))):
            add(support_bar(tolerance=frame_configuration.top_frame_bracket_tolerance))
        
        with GridLocations(0,frame_configuration.bracket_depth + \
                    frame_configuration.wall_thickness + \
                    frame_configuration.top_frame_bracket_tolerance*2,
                    1,frame_configuration.filament_count+1):
            add(frame_side())

        with BuildPart(Location((frame_configuration.frame_click_sphere_point.x,
                    frame_configuration.bracket_depth/2+frame_configuration.top_frame_bracket_tolerance,
                    frame_configuration.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,frame_configuration.bracket_depth+frame_configuration.wall_thickness+frame_configuration.top_frame_bracket_tolerance*2, 1, frame_configuration.filament_count):
                Sphere(radius=frame_configuration.clip_length/4)
        with BuildPart(Location((frame_configuration.frame_click_sphere_point.x,
                    -frame_configuration.bracket_depth/2-frame_configuration.top_frame_bracket_tolerance,
                    frame_configuration.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,frame_configuration.bracket_depth+frame_configuration.wall_thickness+frame_configuration.top_frame_bracket_tolerance*2, 1, frame_configuration.filament_count):
                Sphere(radius=frame_configuration.clip_length/4)
    part = top_frame.part
    return part

def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(bottom_frame().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(spoke_assembly().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(wheel_guide().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
    part = fil_bracket.part
    part.label = "bracket"
    return part

#frame()
show(frame(), bracket())
#show(frame())

export_stl(frame(), '../stl/top_frame.stl')
