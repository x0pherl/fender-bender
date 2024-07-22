"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc, Cylinder,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                Rectangle, Sphere, RegularPolygon, Circle, export_stl)
from ocp_vscode import show
from shapely.geometry import Point
from bank_config import BankConfig
from curvebar import frame_side
from geometry_utils import find_related_point_by_distance
from wall_cut_template import wall_cut_template

config = BankConfig()

def support_bar(tolerance = 0) -> Part:
    """
    creates the bar to support the clip that holds the bracket in place
    """
    adjusted_radius = config.clip_length - tolerance
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
        extrude(amount=config.top_frame_interior_width + \
                config.wall_thickness/config.fillet_ratio*2)
    part = support.part
    part.label = "support"
    return part

def straight_wall_groove() -> Part:
    """
    builds the socket for the side walls to fit into
    """
    with BuildPart() as groove:
        Box(config.wall_thickness+config.frame_bracket_tolerance,
            config.top_frame_interior_width+config.frame_bracket_tolerance,
            config.frame_tongue_depth-config.wall_thickness/2+config.frame_bracket_tolerance,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        extrude(groove.faces().sort_by(Axis.Z)[-1], amount=config.wall_thickness/2, taper=44)
        with BuildPart(groove.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius)
        with BuildPart(groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius*.75)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(config.wall_thickness+config.frame_bracket_tolerance, config.wall_thickness/2,
                    config.frame_tongue_depth+config.frame_bracket_tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildPart(Location((0,0,config.wall_thickness))):
                Sphere(radius=config.wall_thickness*.5)
    part = groove.part
    part.label = "groove"
    return part

def backfloor() -> Part:
    with BuildPart() as floor:
        Box(config.frame_tongue_depth+config.minimum_structural_thickness,
            config.frame_exterior_width,
            config.frame_tongue_depth,
            align=(Align.MIN, Align.CENTER, Align.MAX))
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(0,config.frame_bracket_spacing,
                1,config.filament_count+1):
                Box(config.frame_tongue_depth+config.minimum_structural_thickness,
                    config.wall_thickness,
                    config.frame_tongue_depth,
                    align=(Align.MIN, Align.CENTER, Align.MAX))

    part = floor.part
    return part

def top_frame() -> Part:

    with BuildPart() as tframe:

        right_bottom_intersection = config.find_point_along_right(
                        -config.spoke_height/2)
        right_top_intersection = config.find_point_along_right(
                        -config.spoke_height/2 + config.spoke_bar_height)

        add(angle_bar(depth = config.frame_exterior_width))
        add(back_bar(depth = config.frame_exterior_width))
        with BuildPart(Location((config.frame_back_distance,0,0))) as back_drop:
            Box(config.frame_back_foot_length,
                config.frame_exterior_width,
                #todo this frame_bracket_tolerance*2 nonsense really bothers me track it down
                config.spoke_depth-config.spoke_bar_height/2+config.frame_bracket_tolerance*2,
                align=(Align.MIN, Align.CENTER, Align.MAX))

        with BuildPart(Location((config.frame_back_distance+config.frame_back_foot_length,0,0))) as back_drop:
            add(backfloor())

        with GridLocations(0,config.top_frame_interior_width+config.minimum_structural_thickness+config.wall_thickness*2, 1, 2):
            add(frame_side(config.minimum_structural_thickness))

        fillet_edges = \
                tframe.edges().filter_by_position(Axis.Y, minimum=config.frame_exterior_width/2-.01,
                        maximum=config.frame_exterior_width/2+.02, inclusive=(True,True)) + \
                tframe.edges().filter_by_position(Axis.Y, minimum=-config.frame_exterior_width/2-.01,
                        maximum=-config.frame_exterior_width/2+.02, inclusive=(True,True)) + \
                tframe.edges().filter_by_position(Axis.X, minimum=config.frame_back_distance-.01,
                        maximum=config.frame_back_distance+.01, inclusive=(True,True)) + \
                tframe.edges().filter_by_position(Axis.Z, minimum=right_bottom_intersection.y-.01,
                        maximum=right_bottom_intersection.y+.01).filter_by_position(Axis.X, minimum=config.frame_back_distance+config.frame_back_foot_length-.01, maximum=config.frame_back_distance+config.frame_back_foot_length+.01, inclusive=(True,True)) + \
                tframe.edges().filter_by_position(Axis.X, minimum=right_top_intersection.x+config.minimum_structural_thickness*2+config.frame_bracket_tolerance-.01, maximum=right_top_intersection.x+config.minimum_structural_thickness*2+config.frame_bracket_tolerance+.01, inclusive=(True,True)) + \
                tframe.edges().filter_by_position(Axis.X, minimum=right_bottom_intersection.x+config.minimum_structural_thickness+config.frame_bracket_tolerance-.01, maximum=right_bottom_intersection.x+config.minimum_structural_thickness+config.frame_bracket_tolerance+.01, inclusive=(True,True))

        fillet(fillet_edges, config.minimum_structural_thickness/config.fillet_ratio)

        with BuildPart(mode=Mode.ADD):
            with GridLocations(0,config.frame_bracket_spacing,
                        1,config.filament_count+1):
                add(frame_side(channel=True))

        with BuildPart(Location((right_top_intersection.x +\
                    config.frame_bracket_tolerance,
                    config.top_frame_interior_width/2+config.wall_thickness/config.fillet_ratio,
                    right_top_intersection.y), (90,0,0))):
            add(support_bar(tolerance=config.frame_bracket_tolerance))

        with BuildPart(Location((config.frame_front_wall_center_distance,
                                 0,right_bottom_intersection.y)),mode=Mode.SUBTRACT):
            add(straight_wall_groove().mirror(Plane.YZ))

        with BuildPart(Location((config.frame_back_wall_center_distance,
                        0,-config.frame_tongue_depth)),mode=Mode.SUBTRACT):
            add(straight_wall_groove())

        with BuildPart(Location((config.frame_click_sphere_point.x,
                    config.bracket_depth/2+config.frame_bracket_tolerance,
                    config.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,config.frame_bracket_spacing, 1, config.filament_count):
                Sphere(radius=config.frame_click_sphere_radius*.75)
        with BuildPart(Location((config.frame_click_sphere_point.x,
                    -config.bracket_depth/2-config.frame_bracket_tolerance,
                    config.frame_click_sphere_point.y)), mode=Mode.ADD):
            with GridLocations(0,config.frame_bracket_spacing, 1, config.filament_count):
                Sphere(radius=config.frame_click_sphere_radius*.75)
        if config.frame_wall_bracket:
            with BuildPart(Location((config.frame_back_distance+config.frame_back_foot_length/2,0,-config.spoke_depth/2-config.spoke_bar_height/2)), mode=Mode.SUBTRACT):
                add(wall_cut_template(config.frame_back_foot_length,config.frame_exterior_width,config.spoke_depth+config.spoke_bar_height,bottom=False, post_count=config.filament_count))
    part = tframe.part
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
            add(diamond_cylinder(width/4,length).rotate(Axis.Y, 90))
        if double:
            with BuildPart(Plane.XY.offset(height), mode=Mode.SUBTRACT):
                add(diamond_cylinder(width/4,length).rotate(Axis.Y, 90))
    return part.part

def flat_wall_grooves() -> Part:
    with BuildPart() as grooves:
        with BuildPart(Location((config.frame_front_wall_center_distance-config.buffer_frame_center_x,
                                 0,0),(180,0,0))):
            add(straight_wall_groove().mirror(Plane.YZ))

        with BuildPart(Location((config.frame_back_wall_center_distance-config.buffer_frame_center_x,
                        0,0),(180,0,0))):
            add(straight_wall_groove())
    return grooves.part

def connector_frame(bottom:bool = False) -> Part:
    connector_height = config.bottom_frame_depth if bottom else config.bottom_frame_depth*2
    with BuildPart(Location((config.buffer_frame_center_x,0,0))) as bframe:
        Box(config.bottom_frame_exterior_length,
            config.frame_exterior_width,
            connector_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        bottom_face = bframe.faces().sort_by(Axis.Z)[0]
        top_face = bframe.faces().sort_by(Axis.Z)[-1]
        fillet(bframe.edges(), config.minimum_structural_thickness/config.fillet_ratio)
        with BuildPart(mode=Mode.SUBTRACT):
            with BuildSketch(Location((config.sidewall_center_x,0,0))):
                Rectangle(config.bottom_frame_interior_length+config.minimum_thickness*2,
                config.frame_exterior_width - config.minimum_structural_thickness*2)
            if bottom:
                with BuildSketch(Location((config.sidewall_center_x,0,connector_height))):
                    Rectangle(config.bottom_frame_interior_length,
                    config.frame_exterior_width - config.minimum_structural_thickness*2)
            else:
                with BuildSketch(Location((config.sidewall_center_x,0,connector_height/2))):
                    Rectangle(config.bottom_frame_interior_length,
                    config.frame_exterior_width - config.minimum_structural_thickness*2)
                with BuildSketch(Location((config.sidewall_center_x,0,connector_height))):
                    Rectangle(config.bottom_frame_interior_length+config.minimum_thickness*2,
                    config.frame_exterior_width - config.minimum_structural_thickness*2)
            loft()
        with BuildPart(Location((config.sidewall_center_x,0,0)), mode=Mode.SUBTRACT):
            with GridLocations(0,config.frame_bracket_spacing,
                1,config.filament_count+1):
                Box(config.bottom_frame_interior_length+config.minimum_structural_thickness,
                    config.wall_thickness,
                    connector_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Location((config.sidewall_center_x,0,0)), mode=Mode.ADD):
            with GridLocations(0,config.frame_bracket_spacing,
                1,config.filament_count+1):
                add(channel_box(config.bottom_frame_interior_length+config.minimum_structural_thickness,
                    config.wall_thickness,
                    connector_height, double=(not bottom)))
        with BuildPart(bottom_face, mode=Mode.SUBTRACT):
            add(flat_wall_grooves())
        if not bottom:
            with BuildPart(top_face, mode=Mode.SUBTRACT):
                add(flat_wall_grooves())
    part = bframe.part.rotate(axis=Axis.X, angle=180).move(Location((0,0,connector_height)))
    part.label = "bottom frame"
    return part

def bottom_frame() -> Part:
    return connector_frame(bottom=True)

#todo -- there is a bug with even numbers of filaments where the hole isn't at the center -- that needs to be fixed
def wall_bracket() -> Part:
    with BuildPart() as bracket:
        Box(config.frame_back_foot_length,config.frame_exterior_width,config.spoke_depth+config.spoke_bar_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(bracket.edges(), config.minimum_structural_thickness/config.fillet_ratio)
        with BuildPart(mode=Mode.INTERSECT):
            add(wall_cut_template(config.frame_back_foot_length,config.frame_exterior_width,config.spoke_depth+config.spoke_bar_height,bottom=True, post_count=config.filament_count, tolerance=config.frame_bracket_tolerance))
        with BuildPart(Location((config.frame_back_foot_length/4+config.frame_bracket_tolerance,0,(config.spoke_depth+config.spoke_bar_height)/2),(0,-90,0)), mode=Mode.SUBTRACT):
            add(screw_head())
    return bracket.part

def screw_head() -> Part:
    with BuildPart() as head:
        with BuildSketch():
            Circle(config.wall_bracket_screw_head_radius)
        with BuildSketch(Plane.XY.offset(1.4)):
            Circle(config.wall_bracket_screw_head_radius)
        with BuildSketch(Plane.XY.offset(1.4+config.wall_bracket_screw_head_radius-config.wall_bracket_screw_radius)):
            Circle(config.wall_bracket_screw_radius)
        with BuildSketch(Plane.XY.offset(config.frame_back_foot_length)):
            Circle(config.wall_bracket_screw_radius)
        loft(ruled=True)
    return head.part
    #wall_bracket_screw_radius = 2.25
    #wall_bracket_screw_head_radius=4.5


def angle_bar(depth: float) -> Part:
    """
    properly positioned front bar for the frame
    """
    right_bottom_intersection = config.find_point_along_right(
            -config.spoke_height/2)
    right_top_intersection = config.find_point_along_right(
                    -config.spoke_height/2 + config.spoke_bar_height)
    with BuildPart() as foot_bar:
        with BuildSketch(Location((right_bottom_intersection.x + \
                    config.frame_bracket_tolerance,0,
                    right_bottom_intersection.y), (0,0,0))) as base:
            Rectangle(config.minimum_structural_thickness*2,
                    depth,
                    align=(Align.MIN, Align.CENTER))
        with BuildSketch(Location((right_top_intersection.x +\
                    config.frame_bracket_tolerance,0,
                    right_top_intersection.y), (0,0,0))):
            Rectangle(config.minimum_structural_thickness*2,
                    depth,
                    align=(Align.MIN, Align.CENTER))
        loft()
        with BuildPart(Location((right_bottom_intersection.x,0,right_bottom_intersection.y)), mode=Mode.SUBTRACT):
            with GridLocations(0,config.frame_bracket_spacing,
                    1,config.filament_count+1):
                Cylinder(radius=config.wall_thickness/2, height=config.minimum_structural_thickness*2, rotation=(90,90,0))

    part = foot_bar.part
    part.label = "angle bar"
    return part

def back_bar(depth: float) -> Part:
    """
    properly positioned back bar for the frame
    """
    with BuildPart(Location((config.frame_back_distance,0,
                        -config.wall_thickness))) as bar:
        Box(config.minimum_structural_thickness*2,
            depth,
            config.spoke_depth/2+config.spoke_bar_height/2+config.wall_thickness,
            align=(Align.MIN, Align.CENTER, Align.MIN))
    part = bar.part
    part.label = "back bar"
    return part

if __name__ == '__main__':
    topframe = top_frame()
    bottomframe = bottom_frame()
    export_stl(topframe, '../stl/top_frame.stl')
    export_stl(bottomframe, '../stl/bottom_frame.stl')
    export_stl(connector_frame(), '../stl/connector_frame.stl')
    export_stl(wall_bracket(), '../stl/wall_bracket.stl')
    show(topframe,
        bottomframe.rotate(axis=Axis.X,angle=90).move(Location((0,0,
            -config.spoke_depth-config.minimum_structural_thickness*2)))
        )
