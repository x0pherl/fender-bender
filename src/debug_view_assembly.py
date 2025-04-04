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
    BuildSketch,
    Cylinder,
    Location,
    Mode,
    Part,
    Text,
    add,
    export_stl,
    extrude,
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
from sidewall_config import WallStyle
from tongue_groove import tongue_pair, groove_pair

config_path = Path(__file__).parent / "../build-configs/debug.conf"
if not config_path.exists() or not config_path.is_file():
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
_config = BenderConfig(config_path)
filamentbracket = FilamentBracket(_config.filament_bracket_config())
topframe = TopFrame(_config.frame_config)
bottomframe = BottomFrame(_config.frame_config)
connectorframe = ConnectorFrame(_config.frame_config)
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
        with BuildPart(
            Location((_config.frame_exterior_length / 4 + 3, 0, 0))
        ):
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
                    _config.wheel.radius / 2
                    + _config.minimum_structural_thickness,
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


def wall_fit_test():
    """testing the fit of the sidewall and guidewall into the frame"""
    reference_config = (
        Path(__file__).parent / "../build-configs/reference.conf"
    )
    bender_config = BenderConfig(reference_config)
    sidewall = Sidewall(bender_config.sidewall_config)
    guidewall = Guidewall(bender_config.guidewall_config)
    topframe = TopFrame(bender_config.frame_config)
    topframe.compile()
    sidewall.compile()
    guidewall.compile()
    top_frame = topframe._standingframe
    side_wall = sidewall.sidewall.rotate(Axis.X, 90).move(
        Location(
            (
                0,
                -topframe._config.interior_width / 2,
                -sidewall._config.wall_thickness * 0.25,
            )
        )
    )
    guide_wall = (
        guidewall.wall.rotate(Axis.X, -90)
        .rotate(Axis.Z, 90)
        .move(
            Location(
                (
                    topframe._config.groove_distance / 2
                    + guidewall._config.wall_thickness / 2,
                    0,
                    -guidewall._config.core_length / 2,
                )
            )
        )
    )


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
            Box(
                1000, 1000, 1000, align=(Align.CENTER, Align.MAX, Align.CENTER)
            )
    show(
        cutframetest.part,
        filamentbracket.bottom_bracket()
        .rotate(Axis.X, 90)
        .move(
            Location(
                (
                    _config.frame_hanger_offset + _config.tolerance,
                    _config.bracket_depth / 2,
                    _config.frame_base_depth + _config.tolerance,
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
                click_fit_distance=_config.click_fit_distance,
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
                click_fit_distance=_config.click_fit_distance,
                click_fit_radius=_config.frame_click_sphere_radius,
            ).mirror()
        )
    show(tongue.part, groove.part, reset_camera=Camera.KEEP)


def generate_funnel_test_parts():
    bender_config = BenderConfig(
        Path(__file__).parent / "../build-configs/debug.conf"
    )

    with BuildPart(
        Location((bender_config.wheel.radius - 5, 0, 0))
    ) as cutcube:
        Box(
            bender_config.bracket_width,
            bender_config.bracket_width,
            bender_config.bracket_depth,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
    output_directory = Path(__file__).parent / bender_config.stl_folder
    output_directory.mkdir(parents=True, exist_ok=True)

    # for i in range(len(bracket._config.connectors)):
    for i in range(len(bender_config.connectors)):
        with BuildPart() as bb:
            bracket = FilamentBracket(bender_config.filament_bracket_config(i))
            add(bracket.bottom_bracket(force_draft=False))
            add(cutcube.part, mode=Mode.INTERSECT)
        show(bb.part, reset_camera=Camera.KEEP)
        export_stl(
            bb.part,
            str(
                output_directory / f"test{i}{bracket._config.file_suffix}.stl"
            ),
        )


from fb_library import teardrop_cylinder


def test_tubes():
    base_radius = 3.125
    # 6.35, 6.375, 6.4, 6.425, 6.45
    output_directory = Path(__file__).parent / "../stl"

    for i in range(5):
        current_radius = base_radius + (i * 0.0125)
        print(i, current_radius, current_radius * 2)
        with BuildPart() as tube_test:
            Box(14, 70, 14, align=(Align.CENTER, Align.MIN, Align.MIN))
            with BuildPart(Location((0, 0, 7)), mode=Mode.SUBTRACT):
                add(
                    teardrop_cylinder(
                        radius=current_radius,
                        peak_distance=current_radius * 1.1,
                        height=60,
                        rotation=(90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                        mode=Mode.ADD,
                    )
                )
                add(
                    teardrop_cylinder(
                        radius=1.5,
                        peak_distance=1.65,
                        height=70,
                        rotation=(90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                        mode=Mode.ADD,
                    )
                )
                # Cylinder(
                #     radius=current_radius,
                #     height=60,
                #     rotation=(90, 0, 0),
                #     align=(Align.CENTER, Align.CENTER, Align.MAX),
                #     mode=Mode.ADD,
                # )
                # Cylinder(
                #     radius=1.5,
                #     height=70,
                #     rotation=(90, 0, 0),
                #     align=(Align.CENTER, Align.CENTER, Align.MAX),
                #     mode=Mode.ADD,
                # )
            with BuildPart(mode=Mode.SUBTRACT):
                with BuildSketch(tube_test.faces().sort_by(Axis.Z)[-1]):
                    Text(
                        f"{current_radius*2:.3f} mm",
                        5,
                        align=(Align.CENTER, Align.CENTER),
                        rotation=(0, 0, 90),
                    )
                extrude(amount=-0.5)
        show(tube_test.part, reset_camera=Camera.KEEP)
        export_stl(
            tube_test.part,
            str(output_directory / f"tube-test-{current_radius*2:.3f}.stl"),
        )


if __name__ == "__main__":
    gw = Guidewall(_config.guidewall_config)
    sw = Sidewall(_config.sidewall_config)
    rswconfig = _config.sidewall_config
    rswconfig.reinforced = True
    rsw = Sidewall(rswconfig)
    gw.compile()
    sw.compile()
    rsw.compile()
    bwall = (
        gw.parts[0]
        .part.rotate(Axis.Z, 90)
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
        gw.parts[0]
        .part.rotate(Axis.Z, 90)
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
    swall = (
        rsw.parts[0]
        .part.rotate(Axis.X, 90)
        .move(
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
    )

    tf = TopFrame(_config.frame_config)
    tf.compile()

    topframe = tf.parts[0].part

    bf = BottomFrame(_config.frame_config)
    bf.compile()
    bframe = (
        bf.parts[0]
        .part.rotate(Axis.X, 180)
        .move(
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
    )

    cf = ConnectorFrame(_config.frame_config)
    cf.compile()
    cframe = (
        cf.parts[0].part.move(
            Location(
                (
                    0,
                    0,
                    -_config.sidewall_straight_depth
                    - _config.frame_connector_depth,
                )
            )
        ),
    )

    bkt = (
        filamentbracket.bottom_bracket()
        .rotate(Axis.X, 90)
        .move(
            Location(
                (
                    _config.frame_hanger_offset,
                    _config.bracket_depth / 2,
                    _config.frame_base_depth,
                )
            )
        )
    )

    pin = lockpin.lock_pin(
        inset=_config.frame_lock_pin_tolerance / 2, tie_loop=True
    ).move(
        Location(
            (
                _config.lock_pin_point.x + _config.frame_hanger_offset,
                _config.frame_exterior_width / 2,
                _config.lock_pin_point.y
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
