


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
from top_frame import frame_side
from bank_config import BankConfig

bracket_config = BankConfig()

with BuildPart() as part:
    add(frame_side())
show(part)