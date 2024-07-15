"""
Generates the part for the filament bracket of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, CenterArc, Cylinder,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                loft, fillet, Axis, Box, Align, GridLocations, Plane,
                export_stl, Rectangle, Sphere, Polyline, Until, GeomType,
                Vector, chamfer, HexLocations, RegularPolygon, offset,
                Kind, mirror)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import frame_side, side_line
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
            Rectangle(bracket_config.wall_thickness+bracket_config.frame_bracket_tolerance*2, length)
        loft()
        with BuildPart(Plane.XY.offset(bracket_config.wall_thickness), mode=Mode.SUBTRACT):
            Box(bracket_config.wall_thickness+bracket_config.frame_bracket_tolerance*2,
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

def top_cut_sidewall_base(length:float, depth:float=bracket_config.wall_thickness, inset: float=0) -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    sidewall_length = length + bracket_config.frame_tongue_depth
    with BuildPart() as wall:
        with BuildSketch() as sk:
            Rectangle(bracket_config.sidewall_width, sidewall_length)
            with BuildSketch(mode=Mode.SUBTRACT):
                add(side_line(bottom_adjust=0,right_adjust=bracket_config.sidewall_width).move(Location((bracket_config.wall_thickness/2, sidewall_length/2 - bracket_config.spoke_bar_height/2))))
                add(side_line(bottom_adjust=0,right_adjust=bracket_config.sidewall_width).move(Location((bracket_config.wall_thickness/2, sidewall_length/2 + bracket_config.spoke_bar_height/2))))
            offset(amount = -inset)
        extrude(amount=depth/2, both=True)
        
    part = wall.part
    part.label = "top cut sidewall base"
    return part

def top_cut_sidewall(length:float, reinforce=False) -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    with BuildPart() as wall:
        add(top_cut_sidewall_base(length))
        chamfer(wall.faces().filter_by(Axis.Z).edges(),
               length=bracket_config.wall_thickness/2-bracket_config.frame_bracket_tolerance)
        
        if reinforce:
            with BuildPart():
                add(top_cut_sidewall_base(length, depth=bracket_config.minimum_structural_thickness,inset=bracket_config.wall_thickness/2-bracket_config.frame_bracket_tolerance).move(Location((0,0,bracket_config.minimum_structural_thickness/2))))
                with BuildPart(mode=Mode.SUBTRACT):
                   add(top_cut_sidewall_base(length, depth=bracket_config.minimum_structural_thickness, inset=bracket_config.wall_thickness/2-bracket_config.frame_bracket_tolerance+bracket_config.minimum_structural_thickness*2).move(Location((0,0,bracket_config.minimum_structural_thickness/2))))
                with BuildPart(mode=Mode.INTERSECT):
                    Box(bracket_config.sidewall_width-(bracket_config.wall_thickness/2-bracket_config.frame_bracket_tolerance+bracket_config.minimum_structural_thickness)*2, length*2, bracket_config.minimum_structural_thickness*2)
        if not bracket_config.solid_walls:
            inset_distance = bracket_config.wall_thickness/2-bracket_config.frame_bracket_tolerance+bracket_config.minimum_structural_thickness
            if reinforce:
                inset_distance += bracket_config.minimum_structural_thickness
            with BuildPart(mode=Mode.SUBTRACT):
                add(top_cut_sidewall_base(length, inset=inset_distance))
                with BuildPart(mode=Mode.INTERSECT):
                    add(HexWall(width=length, length=bracket_config.sidewall_width,
                            height=bracket_config.wall_thickness, apothem=bracket_config.wall_window_apothem, wall_thickness=bracket_config.wall_thickness/2, inverse=True))
        with BuildPart(Location((-bracket_config.sidewall_width/2+bracket_config.minimum_structural_thickness+bracket_config.wall_thickness/2,0,bracket_config.wall_thickness/2+bracket_config.frame_bracket_tolerance))):
            add(fitted_connector(base_unit=bracket_config.wall_thickness, tolerance=bracket_config.frame_bracket_tolerance/2).rotate(Axis.Z,90))
        with BuildPart(Location((bracket_config.sidewall_width/2-bracket_config.wall_thickness,-bracket_config.spoke_climb/2,bracket_config.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,bracket_config.front_wall_length/2,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius)
        with BuildPart(Location((bracket_config.sidewall_width/2-bracket_config.wall_thickness,-bracket_config.spoke_climb/2,-bracket_config.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,bracket_config.front_wall_length/2,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius)
        with BuildPart(Location((-bracket_config.sidewall_width/2+bracket_config.wall_thickness,-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2,bracket_config.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,bracket_config.sidewall_section_length/2,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius)
        with BuildPart(Location((-bracket_config.sidewall_width/2+bracket_config.wall_thickness,-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2,-bracket_config.wall_thickness/2)), mode=Mode.SUBTRACT):
            with GridLocations(0,bracket_config.sidewall_section_length/2,1,2):
                Sphere(radius=bracket_config.frame_click_sphere_radius)
    part = wall.part
    part.label = "sidewall"
    return part


def click_sides(scale = 1) -> Part:
    with BuildPart(Plane.XY.offset(bracket_config.wall_thickness*2)) as click_points:
        with GridLocations(bracket_config.wall_thickness+bracket_config.frame_bracket_tolerance*2,0,2,1):
            Sphere(bracket_config.frame_click_sphere_radius*scale)
    part = click_points.part
    part.label = "click points"
    return part


def guide_side(length:float) -> Part:
    with BuildPart() as side:
        Box(bracket_config.minimum_structural_thickness - bracket_config.frame_bracket_tolerance,
                length, bracket_config.wall_thickness*3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(side.edges().filter_by(Axis.Y), bracket_config.wall_thickness/4)
    return side.part

def guide_wall(length:float) -> Part:
    """
    builds a wall with guides for each sidewall
    """
    wall_width = bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4
    with BuildPart() as wall:
        with BuildPart() as base:
            Box(wall_width,
                length - \
                    ((bracket_config.frame_tongue_depth + bracket_config.frame_bracket_tolerance)*2),
                bracket_config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        if bracket_config.solid_walls is False:
            with BuildPart(mode=Mode.SUBTRACT):
                add(HexWall(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*4 - bracket_config.minimum_structural_thickness*2,
                        length - bracket_config.minimum_structural_thickness * 2 - \
                        ((bracket_config.frame_tongue_depth + bracket_config.frame_bracket_tolerance)*2),
                        bracket_config.wall_thickness, apothem=bracket_config.bracket_depth/4, wall_thickness=bracket_config.wall_thickness/2, align=(Align.CENTER, Align.CENTER, Align.MIN), inverse=True))
                
        with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
            add(straight_wall_tongue())
        with GridLocations(bracket_config.frame_bracket_spacing,0,bracket_config.filament_count+1, 1):
            add(wall_channel(length - ((bracket_config.frame_tongue_depth + bracket_config.frame_bracket_tolerance)*2)))
        with GridLocations(bracket_config.top_frame_interior_width+bracket_config.frame_bracket_tolerance+bracket_config.minimum_structural_thickness*2,0,2, 1):
            add(guide_side(length - ((bracket_config.frame_tongue_depth + bracket_config.frame_bracket_tolerance)*2)))
        fillet(wall.faces().sort_by(Axis.Z)[0].edges().filter_by(Axis.Y), bracket_config.wall_thickness/4)
        with BuildPart(mode=Mode.SUBTRACT):
            with GridLocations(bracket_config.top_frame_interior_width+bracket_config.wall_thickness*3+bracket_config.frame_bracket_tolerance*4,0,2, 1):
                    add(fitted_slot(bracket_config.wall_thickness, tolerance=bracket_config.frame_bracket_tolerance/2).rotate(Axis.Y, 90).rotate(Axis.X, -90).move(Location((-bracket_config.wall_thickness/2,0,bracket_config.wall_thickness*3))))
        with GridLocations(bracket_config.frame_bracket_spacing, length/2, bracket_config.filament_count+1, 2):
            add(click_sides(.75))
    part = wall.part
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

def fitted_slot(base_unit:float, tolerance: float) -> Part:
    with BuildPart() as slot:
        with BuildSketch():
            with BuildLine():
                Polyline((
                    (-base_unit*1.5-tolerance,0),
                    (-base_unit*1.5-tolerance,base_unit-tolerance),
                    (-base_unit*2.5-tolerance,base_unit-tolerance),
                    (-base_unit*1.5-tolerance,base_unit*2+tolerance),
                    (base_unit*1.5+tolerance,base_unit*2+tolerance),
                    (base_unit*2.5+tolerance,base_unit-tolerance),
                    (base_unit*1.5+tolerance,base_unit-tolerance),
                    (base_unit*1.5+tolerance,0),
                    (-base_unit*1.5-tolerance,0)
                ))
            make_face()
        extrude(amount=base_unit+tolerance)
    return slot.part

def fitted_connector(base_unit:float, tolerance: float) -> Part:
    with BuildPart() as connector:
        with BuildSketch():
            with BuildLine():
                Polyline((
                    (base_unit/2,0),
                    (base_unit/2,base_unit*2-tolerance),
                    (base_unit*1.5-tolerance,base_unit*2-tolerance),
                    (base_unit*2-tolerance,base_unit+tolerance),
                    (base_unit*1.5-tolerance,base_unit+tolerance),
                    (base_unit*1.5-tolerance,0),
                    (base_unit/2,0)
                ))
            make_face()     
        extrude(amount=base_unit-tolerance*2)
        add(connector.part.mirror(Plane.ZY))
    
    return connector.part.move(Location((0,0,tolerance)))


if __name__ == '__main__':
    fwall=front_wall()
    export_stl(fwall, '../stl/front_wall.stl')

    bwall=back_wall()
    export_stl(bwall, '../stl/back_wall.stl')

    side_wall = top_cut_sidewall(length=bracket_config.sidewall_section_length)
    export_stl(side_wall, '../stl/side_wall.stl')

    left_side_wall = top_cut_sidewall(length=bracket_config.sidewall_section_length,reinforce=True)
    export_stl(left_side_wall, '../stl/left_reinforced_wall.stl')

    right_side_wall = left_side_wall.mirror(Plane.XY).rotate(Axis.Y, 180)
    export_stl(right_side_wall, '../stl/right_reinforced_wall.stl')

    show(fwall.move(Location((bracket_config.frame_exterior_width/2+bracket_config.sidewall_width/2,-bracket_config.spoke_climb/2,0))), 
        bwall.move(Location((-bracket_config.frame_exterior_width/2-bracket_config.sidewall_width/2,-bracket_config.frame_tongue_depth-bracket_config.wall_thickness/2,0))),
        side_wall,
        left_side_wall.move(Location((bracket_config.sidewall_width/2+1,bracket_config.spoke_climb/2+bracket_config.sidewall_section_length,0))),
        right_side_wall.move(Location((-bracket_config.sidewall_width/2-1,bracket_config.spoke_climb/2+bracket_config.sidewall_section_length,0)))
        )
