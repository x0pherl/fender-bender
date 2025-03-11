from build123d import (
    Part,
    BuildPart,
    PolarLocations,
    add,
    fillet,
    Align,
    Box,
    Cylinder,
    Location,
    Axis,
    GridLocations,
)
from fb_library import diamond_cylinder, diamond_torus


def wallslot(
    wall_thickness: float = 2,
    length: float = 180,
    interior_radius: float = 70,
    base_depth: float = 6,
) -> Part:
    with BuildPart() as cut:
        add(
            diamond_cylinder(
                wall_thickness / 4,
                length,
                stretch=(2, 1, 1),
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                rotation=(0, 90, 0),
            )
        )
        with PolarLocations(
            interior_radius,
            2,
        ):
            add(
                diamond_cylinder(
                    wall_thickness / 4,
                    base_depth,
                    stretch=(2, 1, 1),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            )
        with BuildPart(Location((0, 0, base_depth), (90, 0, 0))):
            add(
                diamond_torus(
                    interior_radius,
                    wall_thickness / 4,
                    (2, 1),
                )
            ).rotate(Axis.X, 90)
    return cut.part


def wallslots(
    wall_distance: float = 12.6,
    count: int = 5,
    wall_thickness: float = 2,
    length: float = 180,
    interior_radius: float = 70,
    base_depth: float = 6,
) -> Part:
    with BuildPart() as slots:
        with GridLocations(
            0,
            wall_distance,
            1,
            count,
        ):
            add(wallslot(wall_thickness, length, interior_radius, base_depth))
    return slots.part


def core_cut(interior_radius, width, base_depth) -> Part:
    """the cut required for the round extension of the walls"""
    with BuildPart(Location((0, 0, base_depth))) as cut:
        Cylinder(
            interior_radius,
            height=width,
            rotation=(90, 0, 0),
        )
        Box(
            interior_radius * 2,
            width,
            base_depth,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )
    return cut.part


def chamber_cut(
    length: float = 180,
    width: float = 12.6,
    depth: float = 10,
    fillet_radius: float = 2,
) -> Part:
    """
    a filleted box for a chamber in the lower connectors
    -------
    arguments:
        - length: the length of the chamber
        - width: the width of the chamber
        - depth: the depth of the chamber
        - fillet_radius: how much of a fillet
          radius to apply on the Z Axis
    """
    with BuildPart() as cut:
        Box(
            length,
            width,
            depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        fillet(
            cut.edges().filter_by(Axis.Z),
            radius=fillet_radius,
        )
    return cut.part


def chamber_cuts(
    count: int = 5,
    spacing: float = 14,
    length: float = 180,
    width: float = 12.6,
    depth: float = 10,
    fillet_radius: float = 2,
) -> Part:
    """
    a series of filleted boxes for each chamber in the lower connectors
    -------
    arguments:
        - count: the number of chamber cuts
        - spacing: the distance between the center of the cuts
        - length: the length of the chamber
        - width: the width of the chamber
        - depth: the depth of the chamber
        - fillet_radius: how much of a fillet
          radius to apply on the Z Axis
    """
    with BuildPart() as cuts:
        with GridLocations(0, spacing, 1, count):
            add(chamber_cut(length, width, depth, fillet_radius))
    return cuts.part
