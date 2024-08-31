"""
HexWall

name: hexwall.py
by:   Gumyr
date: March 22nd 2023

desc:
    This python module creates a hexagonal pattern within a box, resulting
    in a grid of hexagons.
"""

from math import sqrt
from typing import Union

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    HexLocations,
    Mode,
    Part,
    RegularPolygon,
    extrude,
)


def HexWall(
    length,
    width,
    height,
    apothem,
    wall_thickness: float,
    align: Union[Align, tuple[Align, Align, Align]] = (
        Align.CENTER,
        Align.CENTER,
        Align.CENTER,
    ),
    inverse=False,
) -> Part:
    """
    Part Object: hexwall

    Args:
        length (float): box size
        width (float): box size
        height (float): box size
        apothem (float): the distance between two paralel edges of the hexagon
        align (Union[Align, tuple[Align, Align, Align]], optional):
            align min, center, or max of object.
            Defaults to (Align.CENTER, Align.CENTER, Align.CENTER).
    """
    with BuildPart() as wall:
        Box(length=length, width=width, height=height, align=align)
        combine_mode = Mode.INTERSECT if inverse else Mode.SUBTRACT
        with BuildPart(mode=combine_mode):
            with BuildSketch(wall.faces().sort_by(Axis.Z)[0]) as sk:
                with HexLocations(
                    apothem=apothem,
                    x_count=int(length // ((sqrt(3) / 2 * apothem) / 2)) + 2,
                    y_count=int(width // apothem / 2) + 2,
                ):
                    RegularPolygon(
                        radius=apothem - wall_thickness / 2,
                        major_radius=False,
                        side_count=6,
                    )
            extrude(sk.sketch, -height)
    part = wall.part
    part.label = "hexwall"
    return part
