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
from ocp_vscode import Camera, show

from bank_config import BankConfig

_config = BankConfig('../build-configs/debug.conf')


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


def frame_flat_sidewall_cut(thickness=_config.wall_thickness) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    """
    mid_adjustor = thickness / 2
    with BuildPart() as side:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(-thickness / 4)):
                Rectangle(
                    width=_config.sidewall_width,
                    height=1,
                    align=(Align.CENTER, Align.MAX),
                )
            with BuildSketch():
                Rectangle(
                    width=_config.sidewall_width,
                    height=1 + mid_adjustor,
                    align=(Align.CENTER, Align.MAX),
                )
            with BuildSketch(Plane.XY.offset(thickness / 4)):
                Rectangle(
                    width=_config.sidewall_width,
                    height=1,
                    align=(Align.CENTER, Align.MAX),
                )
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
    part.label = "Frame Side"
    return part


def frame_cut_sketch(inset=0) -> Sketch:
    """
    the overall shape of the sidewall with the arch
    """
    with BuildSketch(mode=Mode.PRIVATE) as wall:
        Rectangle(
            width=_config.sidewall_width,
            height=1 - inset * 2,
            align=(Align.CENTER, Align.MAX),
        )
    with BuildSketch() as side:
        Circle(radius=_config.wheel_radius - inset)
        Rectangle(
            width=_config.wheel_diameter - inset * 2,
            height=_config.frame_base_depth,
            align=(Align.CENTER, Align.MAX),
        )
        add(wall.sketch.move(Location((0, -_config.frame_base_depth - inset))))
    return side.sketch.move(Location((0, _config.frame_base_depth)))


def frame_arched_sidewall_cut(thickness=_config.wall_thickness) -> Part:
    """
    a template to subtract in order to create the groove
    for fitting the side wall
    arguments:
        - thickness: determines the depth of the wall
    """
    mid_adjustor = thickness / 4
    with BuildPart() as side:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(-thickness / 4)):
                add(frame_cut_sketch(inset=0))
            with BuildSketch():
                add(frame_cut_sketch(inset=-mid_adjustor))
            with BuildSketch(Plane.XY.offset(mid_adjustor)):
                add(frame_cut_sketch(inset=0))
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
    part.label = "Frame Side"
    return part
