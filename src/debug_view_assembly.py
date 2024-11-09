"""
displays aligned critical components of our filament bank design
useful for documentation and debugging
"""

from pathlib import Path

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

from bender_config import BenderConfig
from filament_bracket import FilamentBracket
from frame_top import TopFrame
from frame_bottom import BottomFrame
from frame_connector import ConnectorFrame
from lock_pin import LockPin
from sidewall import Sidewall
from guidewall import Guidewall
from tongue_groove import tongue_pair, groove_pair

_config_file = Path(__file__).parent / "../build-configs/debug.conf"
_config = BenderConfig(_config_file)
filamentbracket = FilamentBracket(_config_file)
topframe = TopFrame(_config.top_frame_config)
bottomframe = BottomFrame(_config.top_frame_config)
connectorframe = ConnectorFrame(_config.connector_frame_config)
sidewall = Sidewall(_config.sidewall_config)
guidewall = Guidewall(_config.guidewall_config)
lockpin = LockPin(_config.lock_pin_config)


def bracket() -> Part:
    """
    returns enough of the filament bracket to help display the frame alignment
    useful in debugging
    """
    with BuildPart() as fil_bracket:
        add(
            filamentbracket.bottom_bracket(draft=True)
            .rotate(axis=Axis.X, angle=90)
            .move(Location((0, _config.bracket_depth / 2, 0)))
        )
        add(
            filamentbracket.spoke_assembly()
            .rotate(axis=Axis.X, angle=90)
            .move(Location((0, _config.bracket_depth / 2, 0)))
        )
        add(
            filamentbracket.wheel_guide()
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
        add(topframe.top_frame())
        Box(
            1000,
            1000,
            1000,
            align=(Align.CENTER, Align.MIN, Align.CENTER),
            mode=Mode.SUBTRACT,
        )
    return half.part


def clip_test():
    """
    generates a useful part for testing the clip and pin mechanisms;
    the the egress side of the frame and bracket
    """
    with BuildPart() as testblock:
        add(topframe.top_frame())
        with BuildPart(
            Location((_config.frame_exterior_length / 4, 0, 0)),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel.diameter,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    _config.wheel.radius / 2
                    + _config.frame_base_depth
                    + _config.minimum_structural_thickness,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel.diameter,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(Location((_config.frame_exterior_length / 4 + 3, 0, 0))):
            Box(
                _config.minimum_structural_thickness,
                _config.frame_exterior_width,
                _config.wheel.radius / 2
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
        add(filamentbracket.bottom_bracket())
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_length,
                _config.frame_exterior_length,
                align=(Align.CENTER, Align.MAX, Align.CENTER),
            )
        with BuildPart(
            Location(
                (
                    _config.frame_exterior_length / 4 + 3 + _config.tolerance,
                    0,
                    0,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel.diameter,
                align=(Align.MAX, Align.MIN, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    _config.wheel.radius / 2 + _config.minimum_structural_thickness,
                    0,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                _config.frame_exterior_length,
                _config.frame_exterior_width,
                _config.wheel.diameter,
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
        add(topframe.top_frame())
        with BuildPart(
            Location(
                (
                    0,
                    -_config.frame_exterior_width / 2
                    + _config.wall_thickness
                    + _config.minimum_structural_thickness
                    + _config.bracket_depth / 2,
                    0,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(1000, 1000, 1000, align=(Align.CENTER, Align.MAX, Align.CENTER))
    show(
        cutframetest.part,
        filamentbracket.bottom_bracket()
        .rotate(Axis.X, 90)
        .move(
            Location(
                (
                    _config.tolerance,
                    _config.bracket_depth / 2,
                    _config.frame_base_depth,
                )
            )
        ),
        reset_camera=Camera.KEEP,
    )


def tongue_groove_test():
    """testing the tongue and groove fitting"""

    with BuildPart() as tongue:
        add(
            tongue_pair(
                tongue_distance=_config.sidewall_width,
                width=_config.wall_thickness,
                length=_config.top_frame_interior_width,
                depth=_config.frame_tongue_depth,
                tolerance=_config.tolerance,
                click_fit_distance=_config.top_frame_interior_width
                - _config.bracket_depth,
                click_fit_radius=_config.frame_click_sphere_radius,
            ).move(
                Location(
                    (
                        0,
                        0,
                        0,
                    )
                )
            )
        )
    with BuildPart() as groove:
        add(
            groove_pair(
                groove_distance=_config.sidewall_width,
                width=_config.wall_thickness,
                length=_config.top_frame_interior_width,
                depth=_config.frame_tongue_depth,
                tolerance=_config.tolerance,
                click_fit_distance=_config.top_frame_interior_width
                - _config.bracket_depth,
                click_fit_radius=_config.frame_click_sphere_radius,
            ).mirror()
        )
    show(tongue.part, groove.part, reset_camera=Camera.KEEP)


def generate_funnel_test_parts():
    bracket = FilamentBracket(Path(__file__).parent / "../build-configs/reference.conf")
    with BuildPart(Location((bracket._config.wheel.radius - 5, 0, 0))) as cutcube:
        Box(
            bracket._config.bracket_width,
            bracket._config.bracket_width,
            bracket._config.bracket_depth,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
    output_directory = Path(__file__).parent / bracket._config.stl_folder
    output_directory.mkdir(parents=True, exist_ok=True)

    # for i in range(len(bracket._config.connectors)):
    for i in range(
        len(bracket._config.connectors) - 1, len(bracket._config.connectors)
    ):
        with BuildPart() as bb:
            add(bracket.bottom_bracket(draft=False, connector_index=i))
            add(cutcube.part, mode=Mode.INTERSECT)
        show(bb.part, reset_camera=Camera.KEEP)
        export_stl(
            bb.part,
            str(
                output_directory
                / f"test{i}{bracket._config.connectors[i].file_suffix}.stl"
            ),
        )


if __name__ == "__main__":
    gw = Guidewall(_config.guidewall_config)
    sw = Sidewall(_config.sidewall_config)
    gw.compile()
    sw.compile()
    bwall = (
        gw.wall.rotate(Axis.Z, 90)
        .rotate(Axis.Y, 90)
        .move(
            Location(
                (
                    -_config.sidewall_width / 2
                    - _config.wall_thickness
                    + _config.frame_hanger_offset,
                    0,
                    -_config.sidewall_straight_depth / 2,
                )
            )
        )
    )
    fwall = (
        gw.wall.rotate(Axis.Z, 90)
        .rotate(Axis.Y, -90)
        .move(
            Location(
                (
                    _config.sidewall_width / 2
                    + _config.wall_thickness
                    + _config.frame_hanger_offset,
                    0,
                    -_config.sidewall_straight_depth / 2,
                )
            )
        )
    )
    swall = sw.reinforcedsidewall.rotate(Axis.X, 90).move(
        Location(
            (
                _config.frame_hanger_offset,
                -_config.top_frame_interior_width / 2
                - _config.minimum_structural_thickness
                - _config.wall_thickness / 2,
                0,
            )
        )
    )

    tf = TopFrame(_config.top_frame_config)
    tf.compile()

    topframe = tf._hybridframe

    bf = BottomFrame(_config.top_frame_config)
    bf.compile()
    bframe = bf._hybridframe.rotate(Axis.X, 180).move(
        Location(
            (
                0,
                0,
                -_config.sidewall_straight_depth
                - _config.frame_connector_depth
                - _config.sidewall_straight_depth,
            )
        )
    )

    cf = ConnectorFrame(_config.connector_frame_config)
    cf.compile()
    cframe = (
        cf._hanging_frame.move(
            Location(
                (
                    0,
                    0,
                    -_config.sidewall_straight_depth - _config.frame_connector_depth,
                )
            )
        ),
    )

    bkt = (
        filamentbracket.bottom_bracket()
        .rotate(Axis.X, 90)
        .move(Location((0, _config.bracket_depth / 2, _config.frame_base_depth)))
    )

    pin = lockpin.lock_pin(
        inset=_config.frame_lock_pin_tolerance / 2, tie_loop=True
    ).move(
        Location(
            (
                _config.wheel.radius + _config.bracket_depth / 2,
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
        pin,
        bframe,
        reset_camera=Camera.KEEP,
    )
