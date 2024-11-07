"""
Creates a bearing that is designed to be printed in place
"""

import math
from build123d import (
    BuildPart,
    Cylinder,
    Align,
    Mode,
    Cone,
    Axis,
    Location,
    Plane,
    add,
    Box,
    chamfer,
    loft,
    PolarLocations,
    Sphere,
)
from build123d.build_enums import GeomType
from build123d.build_sketch import BuildSketch
from build123d.objects_sketch import Circle
from ocp_vscode import show, Camera


def _bowed_cylinder(radius, height, pinch_distance, inset=0):
    """
    returns a cylinder with pinched ends
    -------
    arguments:
        - radius: the radius of the center of the cylinder
        - height: the height of the cylinder
        - pinch_distance: the distance to pinch the radius at the ends of the cylinder
        - inset: an amount to shrink each radius of the cylinder
    """
    loft_unit = height / 12
    with BuildPart() as part:
        with BuildSketch():
            Circle(radius - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 3)):
            Circle(radius - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 5)):
            Circle(radius - pinch_distance - inset)
        loft(ruled=True)

        with BuildSketch(Plane.XY.offset(loft_unit * 5)):
            Circle(radius - pinch_distance - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 7)):
            Circle(radius - pinch_distance - inset)
        loft(ruled=True)

        with BuildSketch(Plane.XY.offset(loft_unit * 7)):
            Circle(radius - pinch_distance - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 9)):
            Circle(radius - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 11)):
            Circle(radius - inset)
        with BuildSketch(Plane.XY.offset(loft_unit * 12)):
            Circle(radius - inset)
        loft(ruled=True)

    return part.part


def _rolling_element(height, hollow_core=True, inset=0):
    """
    returns a single rolling element for our bearing
    -------
    arguments:
        - height: the height of the bearing
        - hollow_core: a hole in the center of the element improves printing accuracy
        - inset: an amount to shrink the radius of the element
    """
    with BuildPart() as element:
        add(_bowed_cylinder(height / 2, height, height / 4, inset))
        # chamfer(element.faces().filter_by(GeomType.PLANE).edges(), height / 32)
        if hollow_core:
            Cylinder(
                height / 6,
                height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
    return element.part


def _guide_ring(mid_radius, height, roller_count, tolerance=0.2):
    """returns a ring with appropriate cut-outs to keep the rolling
    elements properly aligned
    -------
    arguments:
        - mid_radius: the center-line radius to align the rolling elements
        - height: the height of the bearing
        - roller_count: the number of rolling elements to generate
        - tolerance (optional): the clearance between parts
    """
    with BuildPart() as ring:
        add(
            _bowed_cylinder(
                mid_radius + height / 2 - tolerance,
                height,
                height / 4,
            )
        )
        add(
            _bowed_cylinder(
                mid_radius - height / 2 + tolerance,
                height,
                -height / 4,
            ),
            mode=Mode.SUBTRACT,
        )

        with BuildPart(mode=Mode.SUBTRACT):
            with PolarLocations(mid_radius, roller_count):
                add(
                    _rolling_element(
                        height, hollow_core=False, inset=-tolerance * 2
                    ),
                )

    return ring.part


def print_in_place_bearing(
    outer_radius, inner_radius, height, tolerance=0.2, floating_ring=True
):
    """returns a print-in-place bearing with the given dimensions
    -------
    arguments:
        - outer_radius: the outer radius of the bearing
        - inner_radius: the inner radius of the bearing
        - height: the height of the bearing
        - tolerance (optional): the clearance between parts
    notes:
        - the difference between the outer and inner radius must
        be larger than the height of the bearing
    """
    if outer_radius - inner_radius < height / 2:
        raise ValueError(
            "outer_radius - inner_radius must be greater than height"
        )
    mid_radius = (outer_radius + inner_radius) / 2
    roller_count = int((math.pi * mid_radius * 2) // (height + tolerance / 2))
    if floating_ring:
        roller_count = math.floor(roller_count * 0.8)
    with BuildPart() as bearing:
        Cylinder(
            outer_radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        with BuildPart(mode=Mode.SUBTRACT):
            add(
                _bowed_cylinder(
                    mid_radius + height / 2 + tolerance,
                    height,
                    height / 4,
                )
            )
        add(
            _bowed_cylinder(
                mid_radius - height / 2 - tolerance,
                height,
                -height / 4,
            )
        )
        Cylinder(
            inner_radius,
            height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
        with PolarLocations(mid_radius, roller_count):
            add(_rolling_element(height))
        if floating_ring:
            add(_guide_ring(mid_radius, height, roller_count, tolerance))
    return bearing.part


if __name__ == "__main__":
    inner_diameter = 3.05
    depth = 4
    ring = print_in_place_bearing(
        inner_diameter * depth, inner_diameter, depth
    )
    show(ring, reset_camera=Camera.KEEP)
