"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline, Until, Cylinder)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import curvebar, frame_side, angle_bar, back_bar
from shapely.geometry import Point
from geometry_utils import find_related_point_by_distance
from filament_bracket import bottom_bracket_frame, spoke_assembly, wheel_guide
from walls import front_wall, back_wall, top_cut_sidewall

frame_configuration = BankConfig()

def support_bar(tolerance = 0) -> Part:
    """
    creates the bar to support the clip that holds the bracket in place
    """
    adjusted_radius = frame_configuration.clip_length - tolerance
    center = find_related_point_by_distance(Point(0,0), adjusted_radius, -135)
    with BuildPart() as support:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((center.x,center.y),
                                radius=adjusted_radius,
                                start_angle=45, arc_size=90)
                Line(arc @ 1, (center.x,center.y))
                Line(arc @ 0, (center.x,center.y))
            make_face()
        extrude(amount=frame_configuration.top_frame_interior_width + \
                frame_configuration.wall_thickness/frame_configuration.fillet_ratio*2)
    part = support.part
    part.label = "support"
    return part

def straight_wall_groove() -> Part:
    with BuildPart() as groove:
        Box(frame_configuration.wall_thickness+frame_configuration.frame_bracket_tolerance,
            frame_configuration.top_frame_interior_width+frame_configuration.wall_thickness*(frame_configuration.filament_count+1)+frame_configuration.frame_bracket_tolerance,
            frame_configuration.frame_tongue_depth-frame_configuration.wall_thickness/2+frame_configuration.frame_bracket_tolerance,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        extrude(groove.faces().sort_by(Axis.Z)[-1], amount=frame_configuration.wall_thickness/2, taper=44)
        with BuildPart(groove.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
            with GridLocations(0,frame_configuration.top_frame_interior_width/1.5,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius)
        with BuildPart(groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.top_frame_interior_width/1.5,1,2):
                Sphere(radius=frame_configuration.frame_click_sphere_radius*.75)
    part = groove.part
    part.label = "groove"
    return part

def backfloor() -> Part:
    with BuildPart() as floor:
        Box(frame_configuration.frame_tongue_depth+frame_configuration.minimum_structural_thickness,
            frame_configuration.frame_exterior_width,
            frame_configuration.frame_tongue_depth,
            align=(Align.MIN, Align.CENTER, Align.MAX))
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.frame_bracket_spacing,
                1,frame_configuration.filament_count+1):
                Box(frame_configuration.frame_tongue_depth+frame_configuration.minimum_structural_thickness,
                    frame_configuration.wall_thickness,
                    frame_configuration.frame_tongue_depth,
                    align=(Align.MIN, Align.CENTER, Align.MAX))

    part = floor.part
    return part

def frame() -> Part:
    with BuildPart() as top_frame:
        
        right_bottom_intersection = frame_configuration.find_point_along_right(
                        -frame_configuration.spoke_height/2)
        right_top_intersection = frame_configuration.find_point_along_right(
                        -frame_configuration.spoke_height/2 + frame_configuration.spoke_bar_height)

        add(angle_bar(depth = frame_configuration.frame_exterior_width))
        add(back_bar(depth = frame_configuration.frame_exterior_width))
        with BuildPart(Location((frame_configuration.frame_back_distance,0,0))) as back_drop:
            Box(frame_configuration.frame_back_foot_length,
                frame_configuration.frame_exterior_width,
                #todo this frame_bracket_tolerance*2 nonsense really bothers me track it down
                frame_configuration.spoke_climb-frame_configuration.spoke_bar_height/2+frame_configuration.frame_bracket_tolerance*2,
                align=(Align.MIN, Align.CENTER, Align.MAX))
                
        with BuildPart(Location((frame_configuration.frame_back_distance+frame_configuration.frame_back_foot_length,0,0))) as back_drop:
            add(backfloor())
    
        with GridLocations(0,frame_configuration.top_frame_interior_width+frame_configuration.minimum_structural_thickness+frame_configuration.wall_thickness*2, 1, 2):
           add(frame_side(frame_configuration.minimum_structural_thickness))

        fillet_edges = \
                top_frame.edges().filter_by_position(Axis.Y, minimum=frame_configuration.frame_exterior_width/2-.01, maximum=frame_configuration.frame_exterior_width/2+.02, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.Y, minimum=-frame_configuration.frame_exterior_width/2-.01, maximum=-frame_configuration.frame_exterior_width/2+.02, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=frame_configuration.frame_back_distance-.01, maximum=frame_configuration.frame_back_distance+.01, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.Z, minimum=right_bottom_intersection.y-.01, maximum=right_bottom_intersection.y+.01).filter_by_position(Axis.X, minimum=frame_configuration.frame_back_distance+frame_configuration.frame_back_foot_length-.01, maximum=frame_configuration.frame_back_distance+frame_configuration.frame_back_foot_length+.01, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=right_top_intersection.x+frame_configuration.minimum_structural_thickness*2+frame_configuration.frame_bracket_tolerance-.01, maximum=right_top_intersection.x+frame_configuration.minimum_structural_thickness*2+frame_configuration.frame_bracket_tolerance+.01, inclusive=(True,True)) + \
                top_frame.edges().filter_by_position(Axis.X, minimum=right_bottom_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.frame_bracket_tolerance-.01, maximum=right_bottom_intersection.x+frame_configuration.minimum_structural_thickness+frame_configuration.frame_bracket_tolerance+.01, inclusive=(True,True))

        fillet(fillet_edges, frame_configuration.minimum_structural_thickness/frame_configuration.fillet_ratio)
        
        with BuildPart(mode=Mode.ADD):
            with GridLocations(0,frame_configuration.frame_bracket_spacing,
                        1,frame_configuration.filament_count+1):
                add(frame_side(channel=True))
        
        with BuildPart(Location((right_top_intersection.x +\
                    frame_configuration.frame_bracket_tolerance,
                    frame_configuration.top_frame_interior_width/2+frame_configuration.wall_thickness/frame_configuration.fillet_ratio,
                    right_top_intersection.y), (90,0,0))):
            add(support_bar(tolerance=frame_configuration.frame_bracket_tolerance))
        
        with BuildPart(Location((frame_configuration.frame_front_wall_center_distance,
                                 0,right_bottom_intersection.y)),mode=Mode.SUBTRACT):
            add(straight_wall_groove().mirror(Plane.YZ))

        with BuildPart(Location((frame_configuration.frame_back_wall_center_distance,
                        0,-frame_configuration.frame_tongue_depth)),mode=Mode.SUBTRACT):
            add(straight_wall_groove())

        with BuildPart(Location((frame_configuration.frame_click_sphere_point.x,
                    frame_configuration.bracket_depth/2+frame_configuration.frame_bracket_tolerance,
                    frame_configuration.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,frame_configuration.frame_bracket_spacing, 1, frame_configuration.filament_count):
                Sphere(radius=frame_configuration.frame_click_sphere_radius*.75)
        with BuildPart(Location((frame_configuration.frame_click_sphere_point.x,
                    -frame_configuration.bracket_depth/2-frame_configuration.frame_bracket_tolerance,
                    frame_configuration.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,frame_configuration.frame_bracket_spacing, 1, frame_configuration.filament_count):
                Sphere(radius=frame_configuration.frame_click_sphere_radius*.75)
    part = top_frame.part
    return part

def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(bottom_bracket_frame().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(spoke_assembly().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
        add(wheel_guide().rotate(axis=Axis.X, angle=90).move(Location(
            (0,frame_configuration.bracket_depth/2, 0))))
    part = fil_bracket.part
    part.label = "bracket"
    return part

def diamond_cylinder(radius=1, height=10):
    with BuildPart() as cyl:
        with BuildSketch():
            RegularPolygon(radius=radius, side_count=4)
        extrude(amount=height/2, both=True)
    part = cyl.part
    return part

def channel_box(length, width, height: float, double:bool = False):
    with BuildPart() as part:
        Box(length, width, height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(mode=Mode.SUBTRACT):
            add(diamond_cylinder(width/2,length).rotate(Axis.Y, 90))
        if double:
            with BuildPart(Plane.XY.offset(height), mode=Mode.SUBTRACT):
                add(diamond_cylinder(width/2,length).rotate(Axis.Y, 90))
    return part.part

def flat_wall_grooves() -> Part:
    with BuildPart() as grooves:
        with BuildPart(Location((frame_configuration.frame_front_wall_center_distance,
                                 0,0),(180,0,0))):
            add(straight_wall_groove().mirror(Plane.YZ))

        with BuildPart(Location((frame_configuration.frame_back_wall_center_distance,
                        0,0),(180,0,0))):
            add(straight_wall_groove())
    return grooves.part

def connector_frame(bottom:bool = False) -> Part:
    
    connector_height = frame_configuration.bottom_frame_height if bottom else frame_configuration.bottom_frame_height*2
    with BuildPart() as bframe:
        Box(frame_configuration.bottom_frame_exterior_length,
            frame_configuration.frame_exterior_width,
            connector_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        bottom_face = bframe.faces().sort_by(Axis.Z)[0]
        top_face = bframe.faces().sort_by(Axis.Z)[-1]
        fillet(bframe.edges(), frame_configuration.minimum_structural_thickness/frame_configuration.fillet_ratio)
        with BuildPart(Location((-frame_configuration.wall_offset,0,0)), mode=Mode.SUBTRACT):
            with BuildSketch(Location((-frame_configuration.wall_offset,0,0))):
                Rectangle(frame_configuration.bottom_frame_interior_length+frame_configuration.minimum_thickness*2,
                frame_configuration.frame_exterior_width - frame_configuration.minimum_structural_thickness*2)
            if bottom:
                with BuildSketch(Location((-frame_configuration.wall_offset,0,connector_height))):
                    Rectangle(frame_configuration.bottom_frame_interior_length,
                    frame_configuration.frame_exterior_width - frame_configuration.minimum_structural_thickness*2)
            else:
                with BuildSketch(Location((-frame_configuration.wall_offset,0,connector_height/2))):
                    Rectangle(frame_configuration.bottom_frame_interior_length,
                    frame_configuration.frame_exterior_width - frame_configuration.minimum_structural_thickness*2)
                with BuildSketch(Location((-frame_configuration.wall_offset,0,connector_height))):
                    Rectangle(frame_configuration.bottom_frame_interior_length+frame_configuration.minimum_thickness*2,
                    frame_configuration.frame_exterior_width - frame_configuration.minimum_structural_thickness*2)
            loft()
        with BuildPart(Location((-frame_configuration.wall_offset,0,0)), mode=Mode.SUBTRACT):
            with GridLocations(0,frame_configuration.frame_bracket_spacing,
                1,frame_configuration.filament_count+1):
                Box(frame_configuration.bottom_frame_interior_length+frame_configuration.minimum_structural_thickness,
                    frame_configuration.wall_thickness,
                    connector_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Location((-frame_configuration.wall_offset,0,0)), mode=Mode.ADD):
            with GridLocations(0,frame_configuration.frame_bracket_spacing,
                1,frame_configuration.filament_count+1):
                add(channel_box(frame_configuration.bottom_frame_interior_length+frame_configuration.minimum_structural_thickness,
                    frame_configuration.wall_thickness,
                    connector_height, double=(not bottom)))
        with BuildPart(bottom_face, mode=Mode.SUBTRACT):
            add(flat_wall_grooves())
        with BuildPart(top_face, mode=Mode.SUBTRACT):
            add(flat_wall_grooves())
        # with BuildPart(Location((frame_configuration.frame_front_wall_center_distance,
        #                          0,0)),mode=Mode.SUBTRACT):
        #     add(straight_wall_groove().mirror(Plane.YZ))

        # with BuildPart(Location((frame_configuration.frame_back_wall_center_distance,
        #                 0,0)),mode=Mode.SUBTRACT):
        #     add(straight_wall_groove())
    part = bframe.part.mirror(Plane.XY).move(Location((0,0,frame_configuration.bottom_frame_height))).rotate(Axis.Z, 180)
    part.label = "bottom frame"
    return part

def bottom_frame() -> Part:
    return connector_frame(bottom=True)

topframe = frame()

right_bottom_intersection = frame_configuration.find_point_along_right(
                -frame_configuration.spoke_height/2)
right_top_intersection = frame_configuration.find_point_along_right(
                -frame_configuration.spoke_height/2 + frame_configuration.spoke_bar_height)

# bframe = bottom_frame()
# cframe = connector_frame()

show(topframe)
# show(topframe, bracket(), bwall, fwall, swall, cframe.move(Location((-frame_configuration.bottom_frame_offset/2,0,-frame_configuration.spoke_bar_height-frame_configuration.front_wall_length-frame_configuration.bottom_frame_height))), bframe.move(Location((-frame_configuration.wall_offset/2,0,-frame_configuration.spoke_bar_height-frame_configuration.front_wall_length-frame_configuration.bottom_frame_height-100))))
# export_stl(topframe, '../stl/top_frame.stl')
# export_stl(bframe, '../stl/bottom_frame.stl')
# export_stl(cframe, '../stl/connector_frame.stl')
