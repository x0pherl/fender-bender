"""
utility for creating a bar with a zig-zag shape
"""
from build123d import (BuildPart, BuildSketch, BuildLine, Polyline,
                       make_face, fillet, extrude, Axis, add, Location,
                       Until, Plane, Part, Rectangle, Align, Box, loft,
                       Mode, chamfer, Sketch, GridLocations, Sphere)
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

def side_line(bottom_adjust=0) -> Sketch:
    """
    
    """
    right_bottom_intersection = frame_configuration.find_point_along_right(
            -frame_configuration.spoke_height/2)
    right_top_intersection = frame_configuration.find_point_along_right(
                    -frame_configuration.spoke_height/2 + frame_configuration.spoke_bar_height)
    with BuildSketch() as sketch:
        x_distance = find_angle_intersection(frame_configuration.spoke_climb/2, frame_configuration.spoke_angle)
        angled_bar_width = find_angle_intersection(frame_configuration.spoke_bar_height/2, frame_configuration.spoke_angle)/2
        with BuildLine() as ln:
            Polyline(
                #todo figure out magic numbers like 3 and 8
                (right_top_intersection.x+frame_configuration.minimum_structural_thickness,right_top_intersection.y),
                (right_bottom_intersection.x+frame_configuration.minimum_structural_thickness,right_bottom_intersection.y+bottom_adjust),
                (x_distance+angled_bar_width-frame_configuration.spoke_bar_height/2,-frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2+bottom_adjust),
                (-x_distance+angled_bar_width-frame_configuration.spoke_bar_height/2,frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2+bottom_adjust),
                (-x_distance+angled_bar_width-frame_configuration.spoke_bar_height/2-8,frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2+bottom_adjust),
                (-frame_configuration.spoke_length/2+frame_configuration.spoke_bar_height,bottom_adjust-frame_configuration.frame_tongue_depth),
                (-frame_configuration.spoke_length/2,bottom_adjust-frame_configuration.frame_tongue_depth),
                (-frame_configuration.spoke_length/2,frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2),
                (-x_distance-angled_bar_width+frame_configuration.spoke_bar_height/2,frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2),
                (x_distance-angled_bar_width+frame_configuration.spoke_bar_height/2, -frame_configuration.spoke_climb/2+frame_configuration.spoke_bar_height/2),
                (right_top_intersection.x+frame_configuration.minimum_structural_thickness,right_top_intersection.y)
            )
        make_face()
        fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                minimum=-frame_configuration.spoke_length/4,
                maximum=frame_configuration.spoke_length/4,
                inclusive=(False, False)), frame_configuration.spoke_bar_height/2)

        fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                minimum=-frame_configuration.spoke_length/2+1,
                maximum=-frame_configuration.spoke_length/4,
                inclusive=(False, False)), frame_configuration.spoke_bar_height/4)
    return sketch.sketch

def frame_side(thickness=frame_configuration.wall_thickness, channel=False) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    channel: (boolean) -- determines whether to cut a channel in the bottom part of the frame
    """
    mid_adjustor = thickness/2 if channel else 0
    with BuildPart() as side:
        with BuildPart() as cb:
            with BuildSketch(Plane.XY.offset(-thickness/2)):
                add(side_line(bottom_adjust=0))
            with BuildSketch():
                add(side_line(bottom_adjust=mid_adjustor))
            with BuildSketch(Plane.XY.offset(thickness/2)):
                add(side_line(bottom_adjust=0))
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
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

def top_cut_sidewall(length:float) -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    sidewall_length = length + frame_configuration.frame_tongue_depth
    with BuildPart() as wall:
        Box(frame_configuration.sidewall_width, sidewall_length, frame_configuration.wall_thickness)
        with BuildPart(Location((0,
                            sidewall_length/2 - frame_configuration.spoke_bar_height/2,
                            0)), mode=Mode.SUBTRACT) as cut:
            add(frame_side(thickness=frame_configuration.wall_thickness).rotate(
                            Axis.X, -90))
            # add(frame_side(thickness=frame_configuration.wall_thickness, 
            #                 extend=frame_configuration.sidewall_width).part.rotate(
            #                 Axis.X, -90))
            with BuildSketch(Location((0,
                            sidewall_length/2 - frame_configuration.spoke_bar_height/2,
                            0))) as sketch:
                with BuildLine():
                    Polyline(
                            (-frame_configuration.spoke_climb/2, frame_configuration.spoke_climb/2),
                            (frame_configuration.spoke_climb/2, -frame_configuration.spoke_climb/2),
                            (frame_configuration.sidewall_width, -frame_configuration.spoke_climb/2),
                            (frame_configuration.sidewall_width, frame_configuration.spoke_climb/2),
                            (-frame_configuration.spoke_climb/2, frame_configuration.spoke_climb/2)                
                        )
                make_face()

            extrude(amount=frame_configuration.wall_thickness/2, both=True)
        chamfer(wall.faces().filter_by(Axis.Z).edges(),
                length=frame_configuration.wall_thickness/2-frame_configuration.top_frame_bracket_tolerance)
        with BuildPart(Location((frame_configuration.sidewall_width/2-frame_configuration.wall_thickness,-frame_configuration.spoke_climb/2,frame_configuration.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.front_wall_length/2,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius)
        with BuildPart(Location((-frame_configuration.sidewall_width/2+frame_configuration.wall_thickness,-frame_configuration.frame_tongue_depth-frame_configuration.wall_thickness/2,frame_configuration.wall_thickness/2,frame_configuration.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.sidewall_section_length/2,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius).mirror(Plane.XY)
        with BuildPart(Location((frame_configuration.sidewall_width/2-frame_configuration.wall_thickness,-frame_configuration.spoke_climb/2,-frame_configuration.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.front_wall_length/2,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius)
        with BuildPart(Location((-frame_configuration.sidewall_width/2+frame_configuration.wall_thickness,-frame_configuration.frame_tongue_depth-frame_configuration.wall_thickness/2,frame_configuration.wall_thickness/2,-frame_configuration.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.sidewall_section_length/2,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius).mirror(Plane.XY)
    part = wall.part
    part.label = "sidewall"
    return part

from ocp_vscode import show
show(top_cut_sidewall(length=frame_configuration.sidewall_section_length))
# show(side_line())