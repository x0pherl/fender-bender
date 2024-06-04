"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Axis, Box, Align, Cylinder,
                export_stl, offset, Polyline)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig

frame_configuration = BankConfig()

