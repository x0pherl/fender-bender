from math import sqrt
from build123d import (
    Align,
    Axis,
    BuildPart,
    Box,
    Cylinder,
    GridLocations,
    Location,
    PolarLocations,
    Mode,
    Part,
    Sphere,
)
from ocp_vscode import show, Camera


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


if __name__ == "__main__":
    show(rail_block_template(), reset_camera=Camera.KEEP)
