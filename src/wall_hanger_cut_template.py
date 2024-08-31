"""
this unit generates a shape that can be used to cut a part into two pieces
that slide together, allowing for a part to be hung on a wall
"""

from build123d import (
    BuildPart,
    BuildSketch,
    Part,
    add,
    Location,
    loft,
    Axis,
    Box,
    Align,
    GridLocations,
    Plane,
    chamfer,
    Rectangle,
    Mode,
)
from ocp_vscode import show, Camera


def wall_slot(width, height, depth) -> Part:
    """
    creates the basic interlocking shape for connecting the two parts
    """
    with BuildPart() as slot:
        with BuildSketch():
            Rectangle(height, width)
        with BuildSketch(Plane.XY.offset(depth)):
            Rectangle(height, width + depth * 2)
        loft()
    return slot.part


def wall_hanger_cut_template(
    length,
    width,
    height: float,
    bottom: bool = True,
    post_count=2,
    tolerance: float = 0.2,
) -> Part:
    """returns a template for splitting a box along the y axis for hanging
    on a wall"""
    effective_tolerance = -tolerance / 2 if bottom else tolerance / 2
    cut_unit = length / 4
    with BuildPart() as cut:
        Box(
            length,
            width,
            cut_unit * 2 + effective_tolerance,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        )
        with BuildPart(
            Location(
                (
                    length / 2 + cut_unit - effective_tolerance,
                    0,
                    cut_unit * 2 + effective_tolerance,
                )
            )
        ) as lip:
            Box(
                cut_unit + effective_tolerance,
                width,
                cut_unit,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            chamfer(
                lip.faces().sort_by(Axis.Z)[-1].edges().sort_by(Axis.X)[0],
                cut_unit / 2,
            )
        with BuildPart(
            Location((0, 0, cut_unit * 2 + effective_tolerance))
        ) as back_edge:
            Box(
                cut_unit * 2 + effective_tolerance,
                width,
                height - cut_unit * 4,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            chamfer(
                back_edge.faces()
                .sort_by(Axis.Z)[-1]
                .edges()
                .sort_by(Axis.X)[0],
                cut_unit,
            )
        with BuildPart(back_edge.faces().sort_by(Axis.X)[-1]):
            with GridLocations(0, width / post_count, 1, post_count):
                add(
                    wall_slot(
                        width / (post_count + 3 - effective_tolerance * 2),
                        height - cut_unit * 4,
                        cut_unit + effective_tolerance,
                    )
                )
    return cut.part


with BuildPart() as hanger:
    Box(9, 80, 40, align=(Align.MIN, Align.CENTER, Align.MIN))
    with BuildPart(mode=Mode.INTERSECT):
        add(
            wall_hanger_cut_template(
                6.0, 59.0, 43.2, bottom=True, post_count=3, tolerance=0.2
            )
        )

with BuildPart() as hung:
    Box(9, 80, 40, align=(Align.MIN, Align.CENTER, Align.MIN))
    with BuildPart(mode=Mode.SUBTRACT):
        add(
            wall_hanger_cut_template(
                6.0, 59.0, 43.2, bottom=False, post_count=3, tolerance=0.2
            )
        )

if __name__ == "__main__":
    show(
        hanger.part,
        hung.part.move(Location((0, 0, 40))),
        reset_camera=Camera.KEEP,
    )
