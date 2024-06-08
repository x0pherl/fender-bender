


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig
from geometry_utils import find_related_point_by_distance, find_related_point_by_y
from curvebar import curvebar

with BuildPart(Location((-10, 5, 2))) as test:
    add(Sphere(2))

show(test)