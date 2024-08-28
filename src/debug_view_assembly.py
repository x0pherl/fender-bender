"""
displays aligned critical components of our filament bank design
useful for documentation and debugging
"""

from build123d import (BuildPart, Part, add, Location, Axis, Mode, Align, Box, export_stl)
from ocp_vscode import show, Camera
from frames import top_frame, bottom_frame, connector_frame
from walls import guide_wall, sidewall
from bank_config import BankConfig
from filament_bracket import bottom_bracket, spoke_assembly, wheel_guide

config = BankConfig()


def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(bottom_bracket(draft=True).rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
        add(spoke_assembly().rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
        add(wheel_guide().rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
    part = fil_bracket.part
    part.label = "bracket"
    return part

def half_top() -> Part:
    with BuildPart() as half:
        add(top_frame())
        Box(1000,1000,1000, align=(Align.CENTER,Align.MIN, Align.CENTER), mode=Mode.SUBTRACT)
    return half.part

bwall = guide_wall(config.sidewall_straight_depth).rotate(Axis.Z, 90).rotate(Axis.Y, 90).move(
                Location((-config.sidewall_width/2-config.wall_thickness,0,
                        -config.sidewall_straight_depth/2)))
fwall = guide_wall(config.sidewall_straight_depth).rotate(
        Axis.Z, 90).rotate(Axis.Y, -90).move(Location((\
        config.sidewall_width/2+config.wall_thickness, 0,
        -config.sidewall_straight_depth/2)))
swall = sidewall(length=config.sidewall_section_depth, reinforce=True) \
    .rotate(Axis.X, 90).move(Location((0,-config.top_frame_interior_width/2,0)))

topframe = top_frame()

def clip_test():
    with BuildPart() as testblock:
        add(top_frame())
        with BuildPart(Location((config.frame_exterior_length/4,0,0)),
                       mode=Mode.SUBTRACT):
            Box(config.frame_exterior_length, config.frame_exterior_width, config.wheel_diameter,
                align=(Align.MAX,Align.CENTER,Align.MIN))
        with BuildPart(Location((0,0,config.wheel_radius/2+config.frame_base_depth)),
                       mode=Mode.SUBTRACT):
            Box(config.frame_exterior_length, config.frame_exterior_width,
            config.wheel_diameter,
                align=(Align.CENTER,Align.CENTER,Align.MIN))
        with BuildPart(Location((config.frame_exterior_length/4+3,0,0))):
            Box(config.minimum_structural_thickness, config.frame_exterior_width,
                config.wheel_radius/2+config.frame_base_depth,
                align=(Align.MAX,Align.CENTER,Align.MIN))
            Box(config.minimum_structural_thickness, config.frame_exterior_width,
                config.frame_base_depth,
                align=(Align.MIN,Align.CENTER,Align.MIN))

    with BuildPart() as testbracket:
        from filament_bracket import bottom_bracket
        add(bottom_bracket())
        with BuildPart(mode=Mode.SUBTRACT):
            Box(config.frame_exterior_length, config.frame_exterior_length,
                config.frame_exterior_length,
                    align=(Align.CENTER, Align.MAX, Align.CENTER))
        with BuildPart(Location((config.frame_exterior_length/4 + 3 + \
                            config.frame_bracket_tolerance,0,0)), mode=Mode.SUBTRACT):
            Box(config.frame_exterior_length, config.frame_exterior_width,
                config.wheel_diameter,
                align=(Align.MAX,Align.MIN,Align.MIN))
        with BuildPart(Location((0,config.wheel_radius/2,0)), mode=Mode.SUBTRACT):
            Box(config.frame_exterior_length, config.frame_exterior_width,
                config.wheel_diameter,
                align=(Align.CENTER,Align.MIN,Align.MIN))

    show(testblock.part, testbracket.part.move(Location((0,0,-config.bracket_depth/2))).rotate(Axis.X,90).move(Location((0,0,config.frame_base_depth))), reset_camera=Camera.KEEP)
    export_stl(testblock.part, '../stl/test-frame.stl')
    export_stl(testbracket.part, '../stl/test-bracket.stl')

ROTATION_VALUE = 180 if config.frame_wall_bracket else 0
DEPTH_SHIFT_VALUE = 0 if config.frame_wall_bracket else -config.sidewall_straight_depth - \
        config.connector_depth - config.sidewall_straight_depth
bframe = bottom_frame().rotate(Axis.X, ROTATION_VALUE).move(
            Location((0,0,
                    -config.sidewall_straight_depth*2-config.connector_depth+DEPTH_SHIFT_VALUE)))

cframe = connector_frame().move(
            Location((0,0,
                    -config.sidewall_straight_depth-config.connector_depth))),

bkt = bracket().move(Location((0,0,config.frame_base_depth)))

# show(topframe, bkt, bwall, cframe, fwall, swall, bframe, reset_camera=Camera.KEEP)
clip_test()