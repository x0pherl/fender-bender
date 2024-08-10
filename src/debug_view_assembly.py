"""
displays aligned critical components of our filament bank design
useful for documentation and debugging
"""

from build123d import (BuildPart, Part, add, Location, Axis)
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

bwall = guide_wall(config.sidewall_straight_depth).rotate(Axis.Z, 90).rotate(Axis.Y, 90).move(
                Location((-config.sidewall_width/2-config.wall_thickness,0,
                        -config.sidewall_straight_depth/2)))
fwall = guide_wall(config.sidewall_straight_depth).rotate(Axis.Z, 90).rotate(Axis.Y, -90).move(Location((\
        config.sidewall_width/2+config.wall_thickness, 0,
        -config.sidewall_straight_depth/2)))
swall = sidewall(length=config.sidewall_section_depth) \
    .rotate(Axis.X, 90).move(Location((0,-config.top_frame_interior_width/2,0)))

topframe = top_frame()

bframe = bottom_frame().rotate(Axis.X, 180).move(
            Location((0,0,
                    -config.sidewall_straight_depth*2-config.connector_depth)))

cframe = connector_frame().move(
            Location((0,0,
                    -config.sidewall_straight_depth-config.connector_depth))),

bkt = bracket().move(Location((0,0,config.frame_base_depth)))

show(topframe, bkt, bwall, cframe, fwall, swall, bframe, reset_camera=Camera.KEEP)
