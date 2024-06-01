"""
Generates the part for the filament wheel of our filament bank design
"""
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, JernArc, BuildLine, Line, make_face, add,
                PolarLocations, RegularPolygon, sweep, Location)
from ocp_vscode import show
from bank_config import BankConfig

def spoke(config: BankConfig) -> Part:
    """
    returns the spoke Sketch for the filament wheel
    """
    spoke_outer_radius = (config.wheel_radius+config.bearing_radius+
                          config.rim_thickness)/2
    spoke_shift = (config.wheel_radius-config.bearing_radius-
                   config.rim_thickness)/2
    with BuildSketch() as sketch:
        with BuildLine():
            l1=CenterArc(center=((spoke_shift,0)), radius=spoke_outer_radius,
                         start_angle=0, arc_size=180)
            l2=CenterArc(center=((spoke_shift,0)), 
                         radius=spoke_outer_radius-config.rim_thickness,
                         start_angle=0, arc_size=180)
            Line(l1 @ 0, l2 @ 0)
            Line(l1 @ 1, l2 @ 1)
        make_face()
    return sketch

def diamond_torus(major_radius:float, minor_radius:float) -> Part:
    """
    sweeps a regular diamond along a circle defined by major_radius
    """
    with BuildPart() as torus:
        with BuildLine():
            l1 = JernArc(start=(major_radius, 0), tangent=(0, 1), radius=major_radius, arc_size=360)
        with BuildSketch(l1 ^ 0):
            RegularPolygon(radius=minor_radius, side_count=4)
        sweep()
    return torus.part

wheel_configuration = BankConfig()
with BuildPart() as filament_wheel:
    with BuildSketch():
        Circle(radius=wheel_configuration.wheel_radius)
        Circle(radius=wheel_configuration.wheel_radius-wheel_configuration.rim_thickness,
               mode=Mode.SUBTRACT)
    with BuildSketch():
        Circle(radius=wheel_configuration.bearing_radius+wheel_configuration.rim_thickness)
        Circle(radius=wheel_configuration.bearing_radius, mode=Mode.SUBTRACT)
    with PolarLocations(0, wheel_configuration.spoke_count):
        add(spoke(wheel_configuration))
    extrude(amount=wheel_configuration.bearing_depth)
    add(diamond_torus(wheel_configuration.wheel_radius, wheel_configuration.bearing_depth/2).
        move(Location((0,0,wheel_configuration.bearing_depth/2))), mode=Mode.SUBTRACT)

show(filament_wheel)
