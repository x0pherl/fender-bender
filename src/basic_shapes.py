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
    Line,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    RadiusArc,
    RegularPolygon,
    RotationLike,
    Sketch,
    Sphere,
    add,
    extrude,
    fillet,
    loft,
    make_face,
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


def circular_intersection(radius: float, coordinate: float) -> float:
    """
    given a positive position along the axis of a circle, find the intersection
    along the other axis of the perimeter of the circle
    -------
    arguments:
        - radius: the radius of the circle
        - coordinate: a coordinate along one axis of the circle (must be a
            positive value less than the radius)
    """
    if 0 > coordinate > radius:
        raise ValueError("The x-coordinate cannot be greater than the radius.")
    return sqrt(radius**2 - coordinate**2)


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
    side_divots=True,
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
        if side_divots:
            with BuildPart(
                Location((-length / 2, 0, (depth - inset) / 2)),
                mode=Mode.SUBTRACT,
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


def heatsink_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20,
) -> Part:
    """
    template for the cutout for a heatsink and bolt
    """
    with BuildPart() as cut:
        Cylinder(
            radius=head_radius,
            height=head_depth,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )
        Cylinder(
            radius=shaft_radius,
            height=shaft_length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    return cut.part.move(Location((0, 0, head_depth)))


def nut_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20,
) -> Part:
    """
    template for the cutout for a heatsink and bolt
    """
    with BuildPart() as cut:
        with BuildSketch():
            RegularPolygon(radius=head_radius, side_count=6)
        extrude(amount=-head_depth)
        Cylinder(
            radius=shaft_radius,
            height=shaft_length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    return cut.part.move(Location((0, 0, head_depth)))


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


def teardrop_sketch(
    radius: float,
    peak_distance: float,
    align: Align | tuple[Align, Align] = (
        Align.CENTER,
        Align.CENTER,
    ),
) -> Sketch:
    from math import sqrt

    x = radius * sqrt(1 - (radius**2 / peak_distance**2))
    y = radius**2 / peak_distance

    with BuildSketch() as teardrop:
        with BuildLine() as outline:
            Line((-x, -y), (0, -peak_distance))
            Line((0, -peak_distance), (x, -y))
            RadiusArc((x, -y), (-x, -y), radius, short_sagitta=False)
        make_face()
    movex = 0
    if align[0] == Align.MAX:
        movex = -radius
    elif align[0] == Align.MIN:
        movex = radius
    movey = -(peak_distance - radius) / 2
    if align[1] == Align.MAX:
        movey = -peak_distance
    elif align[0] == Align.MIN:
        movey = radius

    return teardrop.sketch.move(Location((movex, movey)))


def teardrop_cylinder(
    radius: float,
    peak_distance: float,
    height: float,
    rotation: RotationLike = (0, 0, 0),
    align: Align | tuple[Align, Align, Align] = (
        Align.CENTER,
        Align.CENTER,
        Align.CENTER,
    ),
    mode: Mode = Mode.ADD,
):
    with BuildPart() as cylinder:
        with BuildSketch():
            add(teardrop_sketch(radius, peak_distance, align))
        extrude(amount=height)
    if align[2] == Align.MAX:
        cylinder.part.move(Location((0, 0, -height)))
    elif align[2] == Align.CENTER:
        cylinder.part.move(Location((0, 0, -height / 2)))
    return (
        cylinder.part.rotate(Axis.X, rotation[0])
        .rotate(Axis.Y, rotation[1])
        .rotate(Axis.Z, rotation[2])
    )


if __name__ == "__main__":
    # show(rail_block_template(), reset_camera=Camera.KEEP)

    show(
        teardrop_cylinder(
            10, 11, 10, align=(Align.CENTER, Align.CENTER, Align.MIN)
        ),
        reset_camera=Camera.KEEP,
    )
