


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location, Locations,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector, sweep, GeomType,
                Until, Sketch,chamfer)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig
from geometry_utils import point_distance, y_point_to_angle, x_point_to_angle, find_related_point_by_distance, distance_to_circle_edge
from curvebar import curvebar
from bank_config import BankConfig

bracket_config = BankConfig()

length = 100
climb = 30
bar_width=10
angle=45
depth=2

def find_angle_intersection(known_distance, angle):
    """
    given an angle and the length along the adjascent axis, 
    calculates the distance along the opposite axis
    """
    return known_distance * tan(radians(angle))

def test(input:Sketch, depth:float) -> Part:
    with BuildPart() as out:
        with BuildSketch():
            add(input)
        with BuildSketch(Plane.XY.offset(depth/2)) as mid:
            add(input)
            offset(mid.sketch, amount=depth/2)
        loft()
    return out.part

def simpletest(depth:float) -> Part:
    with BuildPart() as out:
        with BuildSketch():
            Circle(4)
        with BuildSketch(Plane.XY.offset(depth/2)) as mid:
            Circle(4)
            offset(mid.sketch, amount=depth/2)
        loft()
    return out.part

#show(simpletest(2))

with BuildPart() as out:
    with BuildSketch() as layer1:
        x_distance = find_angle_intersection(climb/2, angle)
        angled_bar_width = find_angle_intersection(bar_width/2, angle)/2
        with BuildLine():
            Polyline(
                (length/2,-climb/2+bar_width/2),
                (length/2,-climb/2-bar_width/2),
                (x_distance+angled_bar_width-bar_width/2,-climb/2-bar_width/2),
                (-x_distance+angled_bar_width-bar_width/2,climb/2-bar_width/2),
                (-x_distance-angled_bar_width+bar_width/2,climb/2+bar_width/2),
                (x_distance-angled_bar_width+bar_width/2, -climb/2+bar_width/2),
                (length/2,-climb/2+bar_width/2),
            )
        make_face()
        fillet(layer1.vertices(), radius=4)
    extrude(amount=depth)
    # for x in out.faces().filter_by(Axis.Z).filter_by(GeomType.PLANE):
    #     chamfer()
    chamfer(out.faces().filter_by(Axis.Z).edges(), length=depth/2-.01)
    #chamfer(out.faces().filter_by(Axis.Z)[-1].edges(), length=depth/2)
show(out)



# def tapered_loft(sketch:Sketch, depth=10) -> Part:
#     show(sketch)
#     with BuildPart() as lofted:
#         with BuildSketch():
#             add(Sketch(sketch))
#             #Circle(2)
#         with BuildSketch(Plane.XY.offset(depth/2)):
#             #add(sketch)
#             offset(amount=depth/2)
#         #with BuildSketch(Plane.XY.offset(depth)):
#         #    add(sketch)
#         loft()
#     return lofted.part

# with BuildPart() as curve_part:
#     with BuildSketch() as sketch:
#         x_distance = find_angle_intersection(climb/2, angle)
#         angled_bar_width = find_angle_intersection(bar_width/2, angle)/2
#         with BuildLine():
#             Polyline(
#                 (length/2,-climb/2+bar_width/2),
#                 (length/2,-climb/2-bar_width/2),
#                 (x_distance+angled_bar_width-bar_width/2,-climb/2-bar_width/2),
#                 (-x_distance+angled_bar_width-bar_width/2,climb/2-bar_width/2),
#                 (-length/2,climb/2-bar_width/2),
#                 (-length/2,climb/2+bar_width/2),
#                 (-x_distance-angled_bar_width+bar_width/2,climb/2+bar_width/2),
#                 (x_distance-angled_bar_width+bar_width/2, -climb/2+bar_width/2),
#                 (length/2,-climb/2+bar_width/2),
#             )
#         make_face()
#         fillet(sketch.vertices().filter_by_position(axis=Axis.X,
#                 minimum=-length/2,
#                 maximum=length/2,
#                 inclusive=(False, False)), bar_width/2)
#     # extrude(amount=depth)
#     # for x in curve_part.faces().filter_by(Axis.Z, reverse=True).filter_by(GeomType.PLANE):
#     #     extrude(x, amount=depth/2, taper=44)
#     #show(sketch)
#     show(tapered_loft(sketch, depth))

