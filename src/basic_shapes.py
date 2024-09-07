"""
utility for creating a bar with a zig-zag shape
"""

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    Sketch,
    add,
    fillet,
    loft,
)

def rounded_cylinder(
    radius, height, align=(Align.CENTER, Align.CENTER, Align.CENTER)
) -> Part:
    """
    creates a rounded off cylinder
    """
    with BuildPart() as cylinder:
        Cylinder(radius=radius, height=height, align=align)
        fillet(
            cylinder.faces().sort_by(Axis.Z)[-1].edges()
            + cylinder.faces().sort_by(Axis.Z)[0].edges(),
            radius=radius,
        )
    return cylinder.part
