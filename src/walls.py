"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc, Cylinder,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline, Until, GeomType,
                Vector, chamfer, HexLocations, RegularPolygon)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import frame_side, top_cut_sidewall
from shapely.geometry import Point
from geometry_utils import find_related_point_by_distance
from hexwall import HexWall

bracket_config = BankConfig()

def wall_channel(length:float) -> Part:
    with BuildPart() as channel:
        with BuildPart() as base:
            Box(bracket_config.wall_thickness*3, length, bracket_config.wall_thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(bracket_config.wall_thickness)):
            Rectangle(bracket_config.wall_thickness*3, length)
        with BuildSketch(Plane.XY.offset(bracket_config.wall_thickness*3)):
            Rectangle(bracket_config.wall_thickness+bracket_config.top_frame_bracket_tolerance*2, length)
        loft()
        with BuildPart(Plane.XY.offset(bracket_config.wall_thickness), mode=Mode.SUBTRACT):
            Box(bracket_config.wall_thickness+bracket_config.top_frame_bracket_tolerance*2,
                length,
                bracket_config.wall_thickness*2,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = channel.part
    part.label = "wall channel guide"
    return part

def straight_wall_tongue() -> Part:
    with BuildPart() as tongue:
        Box(bracket_config.wall_thickness,
            bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4,
            bracket_config.frame_tongue_depth - bracket_config.wall_thickness/2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        extrude(tongue.faces().sort_by(Axis.Z)[-1], amount=bracket_config.wall_thickness/2, taper=44)
        with BuildPart(tongue.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
            with GridLocations(0,bracket_config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius*.75)
        with BuildPart(tongue.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
            with GridLocations(0,bracket_config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius)

    part = tongue.part
    part.label = "tongue"
    return part

def click_sides(scale = 1) -> Part:
    with BuildPart(Plane.XY.offset(bracket_config.wall_thickness*2)) as click_points:
        with GridLocations(bracket_config.wall_thickness+bracket_config.top_frame_bracket_tolerance*2,0,2,1):
            Sphere(bracket_config.frame_click_sphere_radius*scale)
    part = click_points.part
    part.label = "click points"
    return part

def guide_wall(length:float) -> Part:
    """
    builds a wall with guides for each sidewall
    """
    with BuildPart() as wall:
        with BuildPart() as base:
            Box(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4,
                length - \
                    ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2),
                bracket_config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            if bracket_config.solid_walls == False:
                with BuildPart(mode=Mode.SUBTRACT):
                    add(HexWall(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4 - bracket_config.minimum_structural_thickness*2,
                            length - bracket_config.minimum_structural_thickness * 2 - \
                            ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2),
                            bracket_config.wall_thickness, apothem=bracket_config.bracket_depth/4, wall_thickness=bracket_config.wall_thickness/2, align=(Align.CENTER, Align.CENTER, Align.MIN), inverse=True))
                
        with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
            add(straight_wall_tongue())
        with GridLocations(bracket_config.frame_bracket_spacing,0,bracket_config.filament_count+1, 1):
            add(wall_channel(length - ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2)))
        with GridLocations(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*3+bracket_config.top_frame_bracket_tolerance,0,2, 1):
            Box(bracket_config.wall_thickness - bracket_config.top_frame_bracket_tolerance,
                length - ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2),
                bracket_config.wall_thickness*3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(wall.faces().sort_by(Axis.X)[0].edges().filter_by(GeomType.LINE).filter_by(Axis.Y) + wall.faces().sort_by(Axis.X)[-1].edges().filter_by(GeomType.LINE).filter_by(Axis.Y), bracket_config.wall_thickness/4)
        with GridLocations(bracket_config.frame_bracket_spacing, length/2, bracket_config.filament_count+1, 2):
            add(click_sides(.75))
        # with BuildPart(Location((0,0,bracket_config.wall_thickness)), mode=Mode.ADD):
        #     with GridLocations(bracket_config.top_frame_interior_width/1.5,length-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2+bracket_config.top_frame_bracket_tolerance,2,2):
        #         Sphere(radius=bracket_config.frame_click_sphere_radius*.75)
        # with BuildPart(mode=Mode.SUBTRACT):
        #     with GridLocations(bracket_config.top_frame_interior_width/1.5,length-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2+bracket_config.top_frame_bracket_tolerance,2,2):
        #         Sphere(radius=bracket_config.frame_click_sphere_radius*.75)

    part = wall.part
    return part

def guide_wall_enforcement_template(length:float) -> Part:
    with BuildPart() as template:
        Box(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4 - bracket_config.minimum_structural_thickness*2,
            length - bracket_config.minimum_structural_thickness * 2 - \
                ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2),
            bracket_config.wall_thickness,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(bracket_config.frame_bracket_spacing,0,bracket_config.filament_count+1, 1):
                Box(bracket_config.wall_thickness*3,length - ((bracket_config.frame_tongue_depth + bracket_config.top_frame_bracket_tolerance)*2), bracket_config.wall_thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))

    part = template.part
    part.label = "cut template"
    return part


def front_wall() -> Part:
    """
    builds the front wall
    """
    # part = guide_wall(bracket_config.sidewall_section_length - bracket_config.frame_back_foot_length)
    part = guide_wall(bracket_config.front_wall_length)
    part.label = "front wall"
    return part

def back_wall() -> Part:
    """
    builds the back wall
    """
    part = guide_wall(bracket_config.sidewall_section_length)
    part.label = "back wall"
    return part

fwall=front_wall()
export_stl(fwall, '../stl/front_wall.stl')

bwall=back_wall()
export_stl(bwall, '../stl/back_wall.stl')

side_wall = top_cut_sidewall(length=bracket_config.sidewall_section_length)
export_stl(side_wall, '../stl/side_wall.stl')

show(fwall.move(Location((bracket_config.top_frame_exterior_width/2+bracket_config.sidewall_width/2,-bracket_config.spoke_climb/2,0))), 
     bwall.move(Location((-bracket_config.top_frame_exterior_width/2-bracket_config.sidewall_width/2,-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2,0))),
     side_wall
     )