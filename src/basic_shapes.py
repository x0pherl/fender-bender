"""
utility for creating a bar with a zig-zag shape
"""

from build123d import (
    Align,
    Axis,
    Box,
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
    chamfer,
    fillet,
    loft,
)
from ocp_vscode import Camera, show

from bank_config import BankConfig

_config = BankConfig('../build-configs/default.conf')


def lock_pin(tolerance=_config.frame_lock_pin_tolerance / 2, tie_loop=False):
    """
    The pin shape for locking in the filament brackets if LockStyle.PIN is used
    """
    rail_height = _config.minimum_structural_thickness - tolerance
    with BuildPart() as pin:
        with BuildPart() as lower:
            Box(
                _config.minimum_structural_thickness - tolerance,
                _config.frame_exterior_width,
                rail_height / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            chamfer(
                lower.faces().sort_by(Axis.Z)[-1].edges().filter_by(Axis.Y),
                length=rail_height / 2 - abs(tolerance / 2),
                length2=_config.minimum_thickness,
            )
        with BuildPart(Plane.XY.offset(rail_height / 2)) as upper:
            Box(
                _config.minimum_structural_thickness - tolerance,
                _config.frame_exterior_width,
                rail_height / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            chamfer(
                upper.faces().sort_by(Axis.Z)[0].edges().filter_by(Axis.Y),
                length=rail_height / 2 - abs(tolerance / 2),
                length2=_config.minimum_thickness,
            )
        if tie_loop:
            with BuildPart(
                Location((0, _config.frame_exterior_width / 2, 0))
            ) as outer_loop:
                Box(
                    _config.minimum_structural_thickness * 2,
                    _config.minimum_structural_thickness * 2,
                    rail_height,
                    align=(Align.CENTER, Align.MIN, Align.MIN),
                )
                fillet(
                    outer_loop.faces()
                    .sort_by(Axis.Y)[-1]
                    .edges()
                    .filter_by(Axis.Z),
                    _config.minimum_structural_thickness - (abs(tolerance)),
                )
            with BuildPart(
                Location(
                    (
                        0,
                        _config.frame_exterior_width / 2
                        + _config.minimum_structural_thickness,
                        0,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                Cylinder(
                    radius=_config.minimum_structural_thickness
                    - _config.minimum_thickness,
                    height=rail_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
    return pin.part


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


def sidewall_shape(
    inset=0, length=_config.sidewall_section_depth, straignt_inset=0
) -> Sketch:
    """
    the shape of the sidewall at the defined length
    """
    with BuildSketch(mode=Mode.PRIVATE) as wall:
        Rectangle(
            width=_config.sidewall_width - inset * 2 - straignt_inset * 2,
            height=length
            - _config.wheel_radius
            - _config.frame_base_depth
            - inset * 2,
            align=(Align.CENTER, Align.MAX),
        )
        if inset > 0:
            Rectangle(
                width=_config.wheel_diameter - inset * 2,
                height=-inset,
                align=(Align.CENTER, Align.MIN),
            )
    with BuildSketch() as side:
        Circle(radius=_config.wheel_radius - inset)
        with BuildSketch(mode=Mode.SUBTRACT):
            Rectangle(
                _config.wheel_diameter * 2,
                _config.wheel_diameter * 2,
                align=(Align.CENTER, Align.MAX),
            )
        Rectangle(
            width=_config.wheel_diameter - inset * 2,
            height=_config.frame_base_depth,
            align=(Align.CENTER, Align.MAX),
        )
        add(wall.sketch.move(Location((0, -_config.frame_base_depth - inset))))
    return side.sketch.move(Location((0, _config.frame_base_depth)))


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


if __name__ == "__main__":
    show(
        sidewall_shape(),
        sidewall_shape(inset=9),
        sidewall_shape(inset=5),
        reset_camera=Camera.KEEP,
    )
