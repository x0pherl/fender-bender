


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location, Locations,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector, sweep, GeomType,
                Until, Sketch,chamfer,RegularPolygon,PolarLocations,Solid)
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

right_bottom_intersection = frame_configuration.find_point_along_right(
                        -frame_configuration.spoke_height/2)

bwall = back_wall().rotate(Axis.Z, 90).rotate(Axis.Y, 90).move(
                Location((frame_configuration.frame_back_wall_center_distance-frame_configuration.wall_thickness/2,0,
                        -frame_configuration.sidewall_section_length/2 - frame_configuration.frame_bracket_tolerance)))
fwall = front_wall().rotate(Axis.Z, 90).rotate(Axis.Y, -90).move(Location((\
        frame_configuration.frame_front_wall_center_distance + frame_configuration.wall_thickness/2,
        0,
        -frame_configuration.spoke_climb/2-frame_configuration.spoke_bar_height/2 - frame_configuration.front_wall_length/2 + frame_configuration.frame_tongue_depth/2 - frame_configuration.frame_bracket_tolerance)))
swall = top_cut_sidewall(length=frame_configuration.sidewall_section_length).rotate(Axis.X, 90).move(Location((-frame_configuration.wall_thickness-frame_configuration.frame_bracket_tolerance*2,-frame_configuration.top_frame_interior_width/2,-frame_configuration.sidewall_section_length/2+frame_configuration.frame_tongue_depth-frame_configuration.frame_bracket_tolerance)))

topframe = frame()
#show(topframe)
bframe = bottom_frame()# .move(
#             Location((-frame_configuration.wall_offset/2,0,
#                     -frame_configuration.spoke_bar_height-frame_configuration.front_wall_length - \
#                         frame_configuration.bottom_frame_height-100)))

cframe = connector_frame().move(
            Location((-frame_configuration.bottom_frame_offset/2,0,
                    -frame_configuration.spoke_climb/2 - frame_configuration.spoke_bar_height/2 - \
                    frame_configuration.front_wall_length - \
                    frame_configuration.bottom_frame_height*2))),

bkt = bracket()

#show(topframe, bkt, bwall, fwall, swall, cframe)
show(topframe, bkt, bwall, fwall, swall)

# show(topframe,
#         bframe.rotate(axis=Axis.X,angle=-90).move(Location((0,0,
#             -frame_configuration.spoke_climb-frame_configuration.minimum_structural_thickness*2))),
#         swall
# )
