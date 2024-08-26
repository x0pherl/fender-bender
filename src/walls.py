"""
Generates the part for the chamber walls of the filament bank
"""
from build123d import (BuildPart, BuildSketch, Part, Cylinder,
                extrude, Mode, add, Location, loft, fillet, Axis,
                Box, Align, GridLocations, Plane, Rectangle,
                Sphere, export_stl)
from ocp_vscode import show, Camera
from bank_config import BankConfig
from basic_shapes import sidewall_shape
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
    return side.part

def sidewall_divots(length:float=config.sidewall_straight_depth):
    """
    positions the holes that get punched along a sidewall to connect to
    the front and back walls
    arguments:
    length: the length of the sidewall
    """
    with BuildPart() as divots:
        with BuildPart(Location((0,0,config.wall_thickness))):
            with GridLocations(config.sidewall_width-config.wall_thickness*2,length/2,2,2):
                Sphere(radius=config.frame_click_sphere_radius)
        with GridLocations(config.sidewall_width-config.wall_thickness*2,length/2,2,2):
            Sphere(radius=config.frame_click_sphere_radius)
    return divots.part

def sidewall(length:float=config.sidewall_section_depth, reinforce=False, flipped=False) -> Part:
    """
    returns a sidewall
    """
    with BuildPart() as wall:
        with BuildSketch(Plane.XY):
            add(sidewall_shape(inset=config.wall_thickness/2))
        with BuildSketch(Plane.XY.offset(config.wall_thickness/2)):
            add(sidewall_shape())
        with BuildSketch(Plane.XY.offset(config.wall_thickness)):
            add(sidewall_shape(inset=config.wall_thickness/2))
        loft(ruled=True)
        if reinforce:
            with BuildPart():
                with BuildSketch():
                    add(sidewall_shape(inset=config.wall_thickness/2, length=length,
                                       straignt_inset=config.minimum_structural_thickness))
                    with BuildSketch(mode=Mode.SUBTRACT):
                        add(sidewall_shape(inset=config.wall_thickness/2 + \
                            config.minimum_structural_thickness, length=length,
                            straignt_inset=config.minimum_structural_thickness))
                extrude(amount=config.minimum_structural_thickness)
        if not config.solid_walls:
            multiplier = 1 if reinforce else 0
            with BuildPart(mode=Mode.SUBTRACT):
                with BuildSketch():
                    add(sidewall_shape(inset=config.wall_thickness/2 + \
                        config.minimum_structural_thickness, length=length,
                        straignt_inset=config.minimum_structural_thickness*multiplier))
                extrude(amount=config.wall_thickness)
                with BuildPart(mode=Mode.INTERSECT):
                    hw=HexWall(width=length*2, length=config.sidewall_width,
                            height=config.wall_thickness,
                            apothem=config.wall_window_apothem,
                            wall_thickness=config.wall_window_bar_thickness, inverse=True,
                            align=(Align.CENTER, Align.CENTER, Align.MIN))
                    if flipped:
                        hw = hw.mirror(Plane.YZ)
                    add(hw)
        with BuildPart(Location((0,-config.sidewall_straight_depth/2,0)), mode=Mode.SUBTRACT):
            add(sidewall_divots(config.sidewall_straight_depth))

    return wall.part

def guide_wall(length:float,flipped=False) -> Part:
    """
    builds a wall with guides for each sidewall
    """
    base_length = length - config.wall_thickness
    with BuildPart() as wall:
        with BuildPart():
            Box(config.frame_exterior_width,
                base_length,
                config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        if config.solid_walls is False:
            with BuildPart(mode=Mode.SUBTRACT):
                hw=HexWall(config.frame_exterior_width - config.minimum_structural_thickness*2,
                        base_length - config.minimum_structural_thickness * 2,
                        config.wall_thickness, apothem=config.wall_window_apothem,
                        wall_thickness=config.wall_window_bar_thickness,
                        align=(Align.CENTER, Align.CENTER, Align.MIN), inverse=True)
                if flipped:
                    hw = hw.mirror(Plane.YZ)
                add(hw)
        with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
            add(straight_wall_tongue())
        with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
            add(straight_wall_tongue())
        with GridLocations(config.frame_bracket_spacing,0,
                            config.filament_count+1, 1):
            add(wall_channel(base_length))
        with GridLocations(config.frame_exterior_width - \
                            config.minimum_structural_thickness + config.frame_bracket_tolerance,0,2, 1):
            add(guide_side(base_length))
        fillet((wall.faces().sort_by(Axis.X)[0] + wall.faces().sort_by(Axis.X)[-1]).edges().filter_by(Axis.Y), config.wall_thickness/4)

    part = wall.part
    return part

if __name__ == '__main__':
    extension_parts = ()
    gwall_one=guide_wall(config.sidewall_straight_depth)
    side_wall = sidewall(length=config.sidewall_section_depth)
    export_stl(side_wall, '../stl/wall-side.stl')
    reinforced_side_wall = sidewall(length=config.sidewall_section_depth,
                                        reinforce=True)
    export_stl(reinforced_side_wall, '../stl/wall-side-reinforced.stl')
    if config.solid_walls:
        export_stl(gwall_one, '../stl/wall-guide.stl')
    else:
        gwall_two=guide_wall(config.sidewall_straight_depth,flipped=True)
        export_stl(gwall_one, '../stl/wall-guide-one.stl')
        export_stl(gwall_two, '../stl/wall-guide-two.stl')

    show(gwall_one.move(Location((0,-config.sidewall_straight_depth/2,0))),
        side_wall.move(Location((-config.frame_exterior_width/2-config.sidewall_width/2-1,
                            0,0))),
        reinforced_side_wall.move(
                Location((config.frame_exterior_width/2+config.sidewall_width/2+1,0,0))),
        extension_parts,
        reset_camera=Camera.KEEP
        )
