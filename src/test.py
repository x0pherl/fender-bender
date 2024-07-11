


from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from shapely import LineString, Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location, Locations,
                Plane, loft, fillet, Axis, Box, Align, Cylinder, Sphere,
                export_stl, offset, Polyline, Rectangle, Vector, sweep, GeomType,
                Until, Sketch,chamfer,RegularPolygon)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig
from curvebar import frame_side
from bank_config import BankConfig

bracket_config = BankConfig()

def diamond_cylinder(radius=1, height=10):
    with BuildPart() as cyl:
        with BuildSketch():
            RegularPolygon(radius=radius, side_count=4)
        extrude(amount=height/2, both=True)
    part = cyl.part
    return part

def top_channel_box(length, width, height: float):
    with BuildPart() as part:
        Box(length, width, height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(Location((0,0,height)), mode=Mode.SUBTRACT):
            add(diamond_cylinder(width/2,length).rotate(Axis.Y, 90))
    return part.part

show(top_channel_box(40,2,10))