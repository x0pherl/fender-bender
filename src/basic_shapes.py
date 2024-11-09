"""
utility for creating a bar with a zig-zag shape
"""

from math import sqrt, radians, cos, sin

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    JernArc,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    RegularPolygon,
    Sphere,
    extrude,
    fillet,
    loft,
    scale,
    sweep,
)
from ocp_vscode import Camera, show


def distance_to_circle_edge(radius, point, angle) -> float:
    """
    for a circle with the given radius, find the distance from the
    given point to the edge of the circle in the direction determined
    by the given angle
    """
    x1, y1 = point
    theta = radians(angle)

    a = 1
    b = 2 * (x1 * cos(theta) + y1 * sin(theta))
    c = x1**2 + y1**2 - radius**2

    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        raise ValueError(
            f"Error: discriminant calculated as < 0 ({discriminant})"
        )
    t1 = (-b + sqrt(discriminant)) / (2 * a)
    t2 = (-b - sqrt(discriminant)) / (2 * a)

    t = max(t1, t2)

    return t


def diamond_torus(
    major_radius: float, minor_radius: float, stretch: tuple = (1, 1)
) -> Part:
    """
    sweeps a regular diamond along a circle defined by major_radius
    -------
    arguments:
        - major_radius: the radius of the circle to sweep the diamond along
        - minor_radius: the radius of the diamond
    """
    with BuildPart() as torus:
        with BuildLine():
            l1 = JernArc(
                start=(major_radius, 0),
                tangent=(0, 1),
                radius=major_radius,
                arc_size=360,
            )
        with BuildSketch(l1 ^ 0):
            RegularPolygon(radius=minor_radius, side_count=4)
            scale(by=(stretch[0], stretch[1], 1))
        sweep()
    return torus.part


def rounded_cylinder(
    radius, height, align=(Align.CENTER, Align.CENTER, Align.CENTER)
) -> Part:
    """
    creates a rounded off cylinder
    -------
    arguments:
        - radius: the radius of the cylinder
        - height: the height of the cylinder
        - align: the alignment of the cylinder (default
                is (Align.CENTER, Align.CENTER, Align.CENTER) )
    """
    if height <= radius * 2:
        raise ValueError("height must be greater than radius * 2")
    with BuildPart() as cylinder:
        Cylinder(radius=radius, height=height, align=align)
        fillet(
            cylinder.faces().sort_by(Axis.Z)[-1].edges()
            + cylinder.faces().sort_by(Axis.Z)[0].edges(),
            radius=radius,
        )
    return cylinder.part


def diamond_cylinder(
    radius: float,
    height: float,
    rotation: tuple = (0, 0, 0),
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER),
    stretch: tuple = (1, 1, 1),
) -> Part:
    with BuildPart() as tube:
        with BuildSketch():
            RegularPolygon(
                radius=radius, side_count=4, align=(align[0], align[1])
            )
            scale(by=stretch)
        extrude(amount=height * stretch[2])
    z_move = 0
    if align[2] == Align.MAX:
        z_move = -height
    elif align[2] == Align.CENTER:
        z_move = -height / 2
    return (
        tube.part.move(Location((0, 0, z_move)))
        .rotate(Axis.X, rotation[0])
        .rotate(Axis.Y, rotation[1])
        .rotate(Axis.Z, rotation[2])
    )


def rail_block_template(
    width=10,
    length=20,
    depth=5,
    radius=1,
    inset=0.2,
    rail_width=1,
) -> Part:

    radial_inset = inset if inset > 0 else inset * 4

    with BuildPart() as rail_block:
        Box(
            length - inset,
            width - inset,
            depth - inset,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        with BuildPart(rail_block.faces().sort_by(Axis.Z)[-1]):
            with GridLocations(0, width - inset, 1, 2):
                Box(
                    length - inset,
                    rail_width / sqrt(2) * 2,
                    rail_width / sqrt(2) * 2,
                    rotation=(45, 0, 0),
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        with BuildPart(Location((-length / 2, 0, 0))):
            Cylinder(
                radius=(depth - inset) / 2,
                height=width - inset,
                rotation=(90, 0, 0),
                align=(Align.CENTER, Align.MIN, Align.CENTER),
            )
        with BuildPart(
            Location((-length / 2, 0, (depth - inset) / 2)), mode=Mode.SUBTRACT
        ):
            with GridLocations(0, width - inset, 1, 2):
                Sphere(radius=radius + radial_inset)
        with BuildPart(Location((-radius * 2.2, 0, (depth - inset)))):
            with PolarLocations((width - inset) / 2, 2, 90):
                Cylinder(
                    radius=rail_width,
                    height=(radius + radial_inset) * 2,
                    rotation=(0, 90, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )
        with BuildPart(mode=Mode.INTERSECT):
            Box(
                (length - inset) * 2,
                width - inset,
                (depth - inset) * 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    return rail_block.part


def screw_cut(
    head_radius: float = 4.5,
    head_sink: float = 1.4,
    shaft_radius: float = 2.25,
    shaft_length: float = 20,
    bottom_clearance: float = 20,
) -> Part:
    """
    template for the cutout for a screwhead
    """
    if head_radius <= shaft_radius:
        raise ValueError("head_radius must be larger than shaft_radius")
    with BuildPart() as head:
        with BuildSketch(Plane.XY.offset(-bottom_clearance)):
            Circle(head_radius)
        with BuildSketch():
            Circle(head_radius)
        with BuildSketch(Plane.XY.offset(head_sink)):
            Circle(head_radius)
        with BuildSketch(
            Plane.XY.offset(head_sink + head_radius - shaft_radius)
        ):
            Circle(shaft_radius)
        with BuildSketch(Plane.XY.offset(shaft_length)):
            Circle(shaft_radius)
        loft(ruled=True)
    return head.part


if __name__ == "__main__":
    show(screw_cut(), reset_camera=Camera.KEEP)
