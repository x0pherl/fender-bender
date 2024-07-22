"""
displays aligned critical components of our filament bank design
useful for documentation and debugging
"""

from build123d import (BuildPart, Part, add, Location, Axis)
from ocp_vscode import show
from frames import top_frame, bottom_frame, connector_frame
from walls import back_wall, front_wall, sidewall
from bank_config import BankConfig
from filament_bracket import bottom_bracket_frame, spoke_assembly, wheel_guide

config = BankConfig()


def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(bottom_bracket_frame().rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
        add(spoke_assembly().rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
        add(wheel_guide().rotate(axis=Axis.X, angle=90).move(Location(
            (0,config.bracket_depth/2, 0))))
    part = fil_bracket.part
    part.label = "bracket"
    return part

right_bottom_intersection = config.find_point_along_right(
                        -config.spoke_height/2)

bwall = back_wall().rotate(Axis.Z, 90).rotate(Axis.Y, 90).move(
                Location((config.frame_back_wall_center_distance - \
                        config.wall_thickness/2,0,
                        -config.sidewall_section_length/2 - \
                        config.frame_bracket_tolerance)))
fwall = front_wall().rotate(Axis.Z, 90).rotate(Axis.Y, -90).move(Location((\
        config.frame_front_wall_center_distance + \
        config.wall_thickness/2, 0,
        -config.spoke_climb/2-config.spoke_bar_height/2 - \
        config.front_wall_length/2 + \
        config.frame_tongue_depth/2 - \
        config.frame_bracket_tolerance)))
swall = sidewall(length=config.sidewall_section_length) \
    .rotate(Axis.X, 90).move(Location((-config.wall_thickness-config.frame_bracket_tolerance*2,-config.top_frame_interior_width/2,-config.sidewall_section_length/2+config.frame_tongue_depth-config.frame_bracket_tolerance)))

topframe = top_frame()

bframe = bottom_frame().move(
            Location((-config.wall_offset/2,0,
                    -config.spoke_bar_height - \
                    config.front_wall_length - \
                    config.bottom_frame_height - \
                    config.extension_section_length)))

cframe = connector_frame().move(
            Location((-config.bottom_frame_offset/2,0,
                    -config.spoke_climb/2 - config.spoke_bar_height/2 - \
                    config.front_wall_length - \
                    config.bottom_frame_height*2))),

bkt = bracket()

# #show(topframe, bkt, bwall, fwall, swall, cframe)
show(topframe, bkt, bwall, fwall, swall, bframe)
