


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location, Locations,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector, sweep, GeomType,
                Until, Sketch,chamfer,RegularPolygon)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from frames import frame, bottom_frame, connector_frame, straight_wall_groove
from walls import back_wall, front_wall, top_cut_sidewall, straight_wall_tongue
from bank_config import BankConfig
from filament_bracket import bottom_bracket_frame, spoke_assembly, wheel_guide
from curvebar import frame_side
from bank_config import BankConfig

frame_configuration = BankConfig()


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

# right_bottom_intersection = frame_configuration.find_point_along_right(
#                         -frame_configuration.spoke_height/2)

# bwall = back_wall().rotate(Axis.Z, 90).rotate(Axis.Y, 90).move(Location((-frame_configuration.bracket_width/2 - \
#                         frame_configuration.frame_bracket_tolerance - \
#                             frame_configuration.minimum_structural_thickness + frame_configuration.frame_back_foot_length + frame_configuration.frame_bracket_tolerance/2,0,-frame_configuration.sidewall_section_length/2 - frame_configuration.frame_bracket_tolerance)))
# fwall = front_wall().rotate(Axis.Z, 90).rotate(Axis.Y, -90).move(Location((\
#     right_bottom_intersection.x + frame_configuration.minimum_structural_thickness + frame_configuration.minimum_thickness + frame_configuration.wall_thickness/2,
#         0,
#         -frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2 - frame_configuration.front_wall_length/2 + frame_configuration.frame_tongue_depth)))
# swall = top_cut_sidewall(length=frame_configuration.sidewall_section_length).rotate(Axis.X, 90).move(Location((-frame_configuration.wall_thickness/2,-frame_configuration.frame_exterior_width/2-frame_configuration.wall_thickness,-frame_configuration.sidewall_section_length/2+frame_configuration.frame_tongue_depth*1.5)))

# topframe = frame()
# show(topframe)
# bframe = bottom_frame()
# cframe = connector_frame()

# show(topframe, bracket(), bwall, fwall, swall, cframe.move(Location((-frame_configuration.bottom_frame_offset/2,0,-frame_configuration.spoke_bar_height-frame_configuration.front_wall_length-frame_configuration.bottom_frame_height))), bframe.move(Location((-frame_configuration.wall_offset/2,0,-frame_configuration.spoke_bar_height-frame_configuration.front_wall_length-frame_configuration.bottom_frame_height-100))))

show(straight_wall_tongue(), straight_wall_groove().move(Location((4,0,0))))