"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline, Until, GeomType,
                Vector, chamfer)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import frame_side
from shapely.geometry import Point
from geometry_utils import find_related_point_by_distance

bracket_config = BankConfig()

def top_cut_sidewall() -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    with BuildPart() as wall:
        Box(bracket_config.sidewall_width, bracket_config.sidewall_section_length, bracket_config.wall_thickness)
        with BuildPart(Location((0,
                            bracket_config.sidewall_section_length/2 - bracket_config.spoke_bar_height/2,
                            0)), mode=Mode.SUBTRACT) as cut:
            add(frame_side(thickness=bracket_config.wall_thickness, 
                            extend=bracket_config.sidewall_width).part.rotate(
                            Axis.X, -90))
            with BuildSketch(Location((0,
                            bracket_config.sidewall_section_length/2 - bracket_config.spoke_bar_height/2,
                            0))) as sketch:
                with BuildLine():
                    Polyline(
                            (-bracket_config.spoke_climb/2, bracket_config.spoke_climb/2),
                            (bracket_config.spoke_climb/2, -bracket_config.spoke_climb/2),
                            (bracket_config.sidewall_width, -bracket_config.spoke_climb/2),
                            (bracket_config.sidewall_width, bracket_config.spoke_climb/2),
                            (-bracket_config.spoke_climb/2, bracket_config.spoke_climb/2)                
                        )
                make_face()

            extrude(amount=bracket_config.wall_thickness/2, both=True)
        chamfer(wall.faces().filter_by(Axis.Z).edges(), length=bracket_config.wall_thickness/2-bracket_config.top_frame_bracket_tolerance)

        #for x in wall.faces().filter_by(Axis.Z, reverse=True).filter_by(GeomType.PLANE):
        #    extrude(x, amount=bracket_config.wall_thickness/2, taper=44)
        # for x in wall.faces().filter_by(Axis.Z, reverse=True).filter_by(GeomType.PLANE, reverse=True):
        #     extrude(x, amount=bracket_config.wall_thickness/2, taper=44, dir=Vector(0, 1, 0))
    part = wall.part
    part.label = "sidewall"
    return part

def wall_channel() -> Part:
    with BuildPart() as channel:
        with BuildSketch() as base:
            Rectangle(bracket_config.wall_thickness*3, bracket_config.sidewall_section_length - bracket_config.top_frame_bracket_tolerance*2)
        with BuildSketch(Plane.XY.offset(bracket_config.wall_thickness*2)):
            Rectangle(bracket_config.wall_thickness+bracket_config.top_frame_bracket_tolerance*2, bracket_config.sidewall_section_length - bracket_config.top_frame_bracket_tolerance*2)
        loft()
        with BuildPart(mode=Mode.SUBTRACT):
            Box(bracket_config.wall_thickness+bracket_config.top_frame_bracket_tolerance*2,
                bracket_config.sidewall_section_length - bracket_config.top_frame_bracket_tolerance*2,
                bracket_config.wall_thickness*2,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = channel.part
    part.label = "wall channel guide"
    return part

def straight_wall_tongue() -> Part:
    with BuildPart() as tongue:
        Box(bracket_config.wall_thickness,
            bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4,
            bracket_config.frame_tongue_depth)
        extrude(tongue.faces().sort_by(Axis.Z)[-1], amount=bracket_config.wall_thickness, taper=44)
    part = tongue.part
    part.label = "tongue"
    return part

def front_wall() -> Part:
    """
    builds the front wall
    """
    with BuildPart() as wall:
        Box(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4,
            bracket_config.sidewall_section_length,
            bracket_config.wall_thickness,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Z)[-1]):
            with GridLocations(bracket_config.frame_bracket_spacing,0,bracket_config.filament_count+1, 1):
                add(wall_channel())
    part = wall.part
    part.label = "front wall"
    return part


#show(straight_wall_tongue())
wall=front_wall()
show(wall)
export_stl(wall, '../stl/front_wall.stl')

export_stl(top_cut_sidewall(), '../stl/side_wall.stl')