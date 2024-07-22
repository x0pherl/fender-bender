"""
Generates the part for the chamber walls of the filament bank
"""
from build123d import (BuildPart, BuildSketch, Part, Cylinder,
                extrude, Mode, add, Location, chamfer, offset,
                loft, fillet, Axis, Box, Align, GridLocations,
                Plane, Rectangle, Sphere, export_stl)
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import side_line
from hexwall import HexWall

config = BankConfig()

def wall_channel(length:float) -> Part:
    """
    creates a channel with tapered sides and snap click points for locking in side walls
    """
    with BuildPart() as channel:
        with BuildPart():
            Box(config.wall_thickness*3, length, config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(config.wall_thickness)):
            Rectangle(config.wall_thickness*3, length)
        with BuildSketch(Plane.XY.offset(config.wall_thickness*3)):
            Rectangle(config.wall_thickness+config.frame_bracket_tolerance*2,
                      length)
        loft()
        with BuildPart(Plane.XY.offset(config.wall_thickness), mode=Mode.SUBTRACT):
            Box(config.wall_thickness+config.frame_bracket_tolerance*2,
                length,
                config.wall_thickness*2,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Plane.XY.offset(config.wall_thickness*2)):
            with GridLocations(config.wall_thickness + \
                           config.frame_bracket_tolerance*2,
                           (length+config.wall_thickness/2)/2,2,2):
                Sphere(config.frame_click_sphere_radius*.75)
    part = channel.part
    part.label = "wall channel guide"
    return part

def straight_wall_tongue() -> Part:
    """
    creates a tongue for locking in wall parts, companion to straight_wall_groove
    """
    with BuildPart() as tongue:
        Box(config.wall_thickness,
            config.top_frame_interior_width-config.frame_bracket_tolerance*2,
            config.frame_tongue_depth - config.wall_thickness/2,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        extrude(tongue.faces().sort_by(Axis.Z)[-1],
                amount=config.wall_thickness/2, taper=44)
        with BuildPart(tongue.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius*.75)
        with BuildPart(tongue.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
            with GridLocations(0,config.top_frame_interior_width/1.5,1,2):
                Sphere(radius=config.frame_click_sphere_radius)

        #this center cut guides the alignment when assembling,
        #and provides additional stability to the hold
        with BuildPart(mode=Mode.SUBTRACT):
            Box(config.wall_thickness,
                    config.wall_thickness/2+config.frame_bracket_tolerance,
                    config.frame_tongue_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildPart(Location((0,0,config.wall_thickness))):
                Sphere(radius=config.wall_thickness*.75)
                Cylinder(radius=config.wall_thickness*.5,
                    height=config.wall_thickness,
                    rotation=(0,0,0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

    part = tongue.part
    part.label = "tongue"
    return part

def guide_side(length:float) -> Part:
    """
    defines the outer sides of the sidewall with appropriate structural
    reinforcements
    """
    with BuildPart() as side:
        Box(config.minimum_structural_thickness - config.frame_bracket_tolerance,
                length, config.wall_thickness*3,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(side.edges().filter_by(Axis.Y), config.wall_thickness/4)
    return side.part

def sidewall_base(length:float, depth:float=config.wall_thickness,
                top_cut=True, inset: float=0) -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    with BuildPart() as wall:
        with BuildSketch():
            Rectangle(config.sidewall_width, length)
            if top_cut:
                with BuildSketch(mode=Mode.SUBTRACT):
                    add(side_line(bottom_adjust=0,right_adjust=config.sidewall_width) \
                        .move(Location((config.wall_thickness, length/2 - \
                                        config.spoke_bar_height/2+config.frame_bracket_tolerance*2))))
                    add(side_line(bottom_adjust=0,right_adjust=config.sidewall_width) \
                        .move(Location((config.wall_thickness, length/2 + \
                                        config.spoke_bar_height/2+config.frame_bracket_tolerance*2))))
            offset(amount = -inset)
        extrude(amount=depth/2, both=True)
    part = wall.part
    part.label = "top cut sidewall base"
    return part

def sidewall_divots(length:float):
    """
    positions the holes that get punched along a sidewall to connect to
    the front and back walls
    arguments:
    length: the length of the sidewall
    """
    with BuildPart() as divots:
        with BuildPart(Location((0,0,config.wall_thickness/2))):
            with GridLocations(0,length/2,1,2):
                Sphere(radius=config.frame_click_sphere_radius)
        with BuildPart(Location((0,0,-config.wall_thickness/2))):
            with GridLocations(0,length/2,1,2):
                Sphere(radius=config.frame_click_sphere_radius)
    return divots.part

def sidewall(length:float, top_cut=True, reinforce=False) -> Part:
    """
    Defines the shape of the sidewall with the correct shape for the
    sides
    """
    with BuildPart() as wall:
        add(sidewall_base(length, top_cut=top_cut))
        chamfer(wall.faces().filter_by(Axis.Z).edges(),
               length=config.wall_thickness/2-config.frame_bracket_tolerance)

        if reinforce:
            with BuildPart():
                add(sidewall_base(length, depth=config.minimum_structural_thickness,
                            top_cut=top_cut,
                            inset=config.wall_thickness/2 - \
                            config.frame_bracket_tolerance).move(
                            Location((0,0,config.minimum_structural_thickness/2))))
                with BuildPart(mode=Mode.SUBTRACT):
                    add(sidewall_base(length, depth=config.minimum_structural_thickness,
                            top_cut=top_cut,
                            inset=config.wall_thickness/2 - \
                            config.frame_bracket_tolerance + \
                            config.minimum_structural_thickness*2).move(
                            Location((0,0,config.minimum_structural_thickness/2))))
                with BuildPart(mode=Mode.INTERSECT):
                    Box(config.sidewall_width - \
                        (config.wall_thickness/2 - \
                        config.frame_bracket_tolerance +\
                        config.minimum_structural_thickness)*2,
                        length*2, config.minimum_structural_thickness*2)
        if not config.solid_walls:
            inset_distance = config.wall_thickness/2 - \
                config.frame_bracket_tolerance + \
                config.minimum_structural_thickness
            if reinforce:
                inset_distance += config.minimum_structural_thickness
            with BuildPart(mode=Mode.SUBTRACT):
                add(sidewall_base(length, top_cut=top_cut,inset=inset_distance))
                with BuildPart(mode=Mode.INTERSECT):
                    add(HexWall(width=length, length=config.sidewall_width,
                            height=config.wall_thickness,
                            apothem=config.wall_window_apothem,
                            wall_thickness=config.wall_thickness/2, inverse=True))
        left_length = config.back_wall_depth-config.frame_tongue_depth*2+config.frame_bracket_tolerance*2 if top_cut else length
        right_length = config.front_wall_depth-config.frame_tongue_depth*2+config.frame_bracket_tolerance*2 if top_cut else length
        right_offset = -config.spoke_depth/2 if top_cut else 0
        left_offset =-config.frame_tongue_depth-config.wall_thickness/2-config.frame_bracket_tolerance*2 if top_cut else 0
        with BuildPart(Location((config.sidewall_width/2-config.wall_thickness,
                                right_offset,0)), mode=Mode.SUBTRACT):
            add(sidewall_divots(right_length))
        with BuildPart(Location((-config.sidewall_width/2+config.wall_thickness,
                                left_offset,0)), mode=Mode.SUBTRACT):
            add(sidewall_divots(left_length))
    part = wall.part
    part.label = "sidewall"
    return part

def guide_wall(length:float) -> Part:
    """
    builds a wall with guides for each sidewall
    """
    base_length = length - config.wall_thickness/2
    with BuildPart() as wall:
        with BuildPart():
            Box(config.frame_exterior_width,
                base_length,
                config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        if config.solid_walls is False:
            with BuildPart(mode=Mode.SUBTRACT):
                add(HexWall(config.frame_exterior_width - config.minimum_structural_thickness*2,
                        base_length - config.minimum_structural_thickness * 2,
                        config.wall_thickness, apothem=config.wall_window_apothem,
                        wall_thickness=config.wall_thickness/2,
                        align=(Align.CENTER, Align.CENTER, Align.MIN), inverse=True))
        with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
            add(straight_wall_tongue())
        with GridLocations(config.frame_bracket_spacing,0,
                            config.filament_count+1, 1):
            add(wall_channel(base_length))
        with GridLocations(config.top_frame_interior_width + \
                            config.frame_bracket_tolerance + \
                            config.minimum_structural_thickness*2,0,2, 1):
            add(guide_side(base_length))
    part = wall.part
    return part

def front_wall() -> Part:
    """
    builds the front wall
    """
    part = guide_wall(config.front_wall_depth)
    part.label = "front wall"
    return part

def back_wall() -> Part:
    """
    builds the back wall
    """
    part = guide_wall(config.back_wall_depth)
    part.label = "back wall"
    return part

if __name__ == '__main__':
    extension_parts = ()
    if config.extension_section_depth != 0:
        extension_guide = guide_wall(config.extension_section_depth)
        export_stl(extension_guide, '../stl/extension_frontback.stl')
        extension_side = sidewall(config.extension_section_depth, top_cut=False)
        export_stl(extension_side, '../stl/extension_side_wall.stl')
        reinforced_extension_side = sidewall(config.extension_section_depth, False, True)
        export_stl(reinforced_extension_side, '../stl/reinforced_extension_side_wall.stl')
        extension_shift = -config.back_wall_depth - config.extension_section_depth - 3
        extension_parts += (extension_side.move(Location((
            -config.sidewall_width/2-config.frame_exterior_width/2-1,extension_shift,0))),
            extension_guide.move(Location((0,extension_shift,0))),
            reinforced_extension_side.move(
                Location((config.sidewall_width/2+config.frame_exterior_width/2+1,extension_shift,0))))
    fwall=front_wall()
    export_stl(fwall, '../stl/front_wall.stl')
    bwall=back_wall()
    export_stl(bwall, '../stl/back_wall.stl')
    side_wall = sidewall(length=config.sidewall_section_depth)
    export_stl(side_wall, '../stl/side_wall.stl')
    left_side_wall = sidewall(length=config.sidewall_section_depth,reinforce=True)
    export_stl(left_side_wall, '../stl/left_reinforced_wall.stl')

    right_side_wall = left_side_wall.mirror(Plane.XY).rotate(Axis.Y, 180)
    export_stl(right_side_wall, '../stl/right_reinforced_wall.stl')

    show(fwall.move(Location((config.frame_exterior_width/2 + \
                            config.sidewall_width/2+1,
                            -config.spoke_depth/2,0))),
        bwall.move(Location((-config.frame_exterior_width/2 - \
                            config.sidewall_width/2-1,
                            -config.frame_tongue_depth-config.wall_thickness/2,0))),
        side_wall,
        left_side_wall.move(Location((config.sidewall_width/2+1,
                            config.spoke_depth/2 + \
                            config.sidewall_section_depth,0))),
        right_side_wall.move(Location((-config.sidewall_width/2-1,
                            config.spoke_depth/2 + \
                            config.sidewall_section_depth,0))),
        extension_parts
        )
