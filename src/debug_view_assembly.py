"""
displays aligned critical components of our filament bank design
useful for documentation and debugging
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Location,
    Mode,
    Part,
    add,
    export_stl,
)
from ocp_vscode import Camera, show

from bank_config import BankConfig, FrameStyle
from filament_bracket import bottom_bracket, spoke_assembly, wheel_guide
from frames import bottom_frame, connector_frame, lock_pin, top_frame
from walls import guide_wall, sidewall

_config = BankConfig('../build-configs/default.conf')


def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(
            bottom_bracket(draft=True)
            .rotate(axis=Axis.X, angle=90)
            .move(Location((0, _config.bracket_depth / 2, 0)))
        )
        add(
            spoke_assembly()
            .rotate(axis=Axis.X, angle=90)
            .move(Location((0, _config.bracket_depth / 2, 0)))
        )
        add(
            wheel_guide()
            .rotate(axis=Axis.X, angle=90)
            .move(Location((0, _config.bracket_depth / 2, 0)))
        )
    part = fil_bracket.part
    part.label = "bracket"
    return part


def half_top() -> Part:
    """
    returns half of the top frame
    """
    with BuildPart() as half:
        add(top_frame())
        Box(
            1000,
            1000,
            1000,
            align=(Align.CENTER, Align.MIN, Align.CENTER),
            mode=Mode.SUBTRACT,
        )
    return half.part


bwall = (
    guide_wall(_config.sidewall_straight_depth)
    .rotate(Axis.Z, 90)
    .rotate(Axis.Y, 90)
    .move(
        Location(
            (
                -_config.sidewall_width / 2 - _config.wall_thickness,
                0,
                -_config.sidewall_straight_depth / 2,
            )
        )
    )
)
fwall = (
    guide_wall(_config.sidewall_straight_depth)
    .rotate(Axis.Z, 90)
    .rotate(Axis.Y, -90)
    .move(
        Location(
            (
                _config.sidewall_width / 2 + _config.wall_thickness,
                0,
                -_config.sidewall_straight_depth / 2,
            )
        )
    )
)
swall = (
    sidewall(length=_config.sidewall_section_depth, reinforce=True)
    .rotate(Axis.X, 90)
    .move(Location((0, -_config.top_frame_interior_width / 2, 0)))
)

topframe = top_frame()


def clip_test():
    """
    generates a useful part for testing the clip and pin mechanisms;
    the the egress side of the frame and bracket
    """
    with BuildPart() as testblock:
        add(top_frame())
        with BuildPart(
            Location((_config.frame_exterior_length / 4, 0, 0)),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel_diameter,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    _config.wheel_radius / 2
                    + _config.frame_base_depth
                    + _config.minimum_structural_thickness,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel_diameter,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(Location((_config.frame_exterior_length / 4 + 3, 0, 0))):
            Box(
                _config.minimum_structural_thickness,
                _config.frame_exterior_width,
                _config.wheel_radius / 2
                + _config.frame_base_depth
                + _config.minimum_structural_thickness,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
            Box(
                _config.minimum_structural_thickness,
                _config.frame_exterior_width,
                _config.frame_base_depth,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )

    with BuildPart() as testbracket:
        add(bottom_bracket())
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_length,
                _config.frame_exterior_length,
                align=(Align.CENTER, Align.MAX, Align.CENTER),
            )
        with BuildPart(
            Location(
                (_config.frame_exterior_length / 4 + 3 + _config.tolerance, 0, 0)
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel_diameter,
                align=(Align.MAX, Align.MIN, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    _config.wheel_radius / 2
                    + _config.minimum_structural_thickness,
                    0,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel_diameter,
                align=(Align.CENTER, Align.MIN, Align.MIN),
            )

    show(
        testblock.part,
        testbracket.part.move(Location((0, 0, -_config.bracket_depth / 2)))
        .rotate(Axis.X, 90)
        .move(Location((0, 0, _config.frame_base_depth))),
        reset_camera=Camera.KEEP,
    )
    export_stl(testblock.part, "../stl/test-frame.stl")
    export_stl(testbracket.part, "../stl/test-bracket.stl")

def cut_frame_test():
    """
    a view with the placement of the bracket easily visible
    """
    with BuildPart() as cutframetest:
        add(top_frame())
        with BuildPart(Location((0,-_config.frame_exterior_width/2+_config.wall_thickness+_config.minimum_structural_thickness+_config.bracket_depth/2,0)), mode=Mode.SUBTRACT):
            Box(1000, 1000, 1000, align=(Align.CENTER, Align.MAX, Align.CENTER))
    show(cutframetest.part, bkt.move(Location((_config.frame_hanger_offset,-_config.frame_bracket_spacing,0))), reset_camera=Camera.KEEP)


if __name__ == "__main__":

    ROTATION_VALUE = 180 if FrameStyle.HANGING in _config.frame_style else 0
    DEPTH_SHIFT_VALUE = (
        -_config.sidewall_straight_depth
        - _config.frame_connector_depth
        - _config.sidewall_straight_depth
        if FrameStyle.STANDING in _config.frame_style
        else 0
    )
    bframe = (
        bottom_frame()
        .rotate(Axis.X, ROTATION_VALUE)
        .move(
            Location(
                (
                    0,
                    0,
                    -_config.sidewall_straight_depth * 2
                    - _config.frame_connector_depth
                    + DEPTH_SHIFT_VALUE,
                )
            )
        )
    )

    cframe = (
        connector_frame().move(
            Location(
                (0, 0, -_config.sidewall_straight_depth - _config.frame_connector_depth)
            )
        ),
    )

    bkt = bracket().move(Location((0, 0, _config.frame_base_depth)))

    lockpin = lock_pin(
        tolerance=_config.frame_lock_pin_tolerance / 2, tie_loop=True
    ).move(
        Location(
            (
                _config.wheel_radius + _config.bracket_depth / 2,
                _config.frame_exterior_width / 2,
                _config.bracket_depth
                + _config.minimum_structural_thickness / 2
                + _config.frame_base_depth
                + _config.frame_lock_pin_tolerance / 2,
            )
        )
    )

    show(
        topframe,
        bkt,
        bwall,
        cframe,
        fwall,
        swall,
        lockpin,
        bframe,
        reset_camera=Camera.KEEP,
    )
