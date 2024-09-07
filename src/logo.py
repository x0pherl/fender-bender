from build123d import (
    Align,
    Box,
    BuildLine,
    BuildSketch,
    CenterArc,
    Circle,
    ExportSVG,
    FontStyle,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    Sketch,
    Text,
    add,
    export_stl,
    extrude,
    fillet,
)
from ocp_vscode import Camera, show

from bank_config import BankConfig

##Note: Flamente Round Bold must be installed with the context menu: "Install For all Users" to show up!!!

_config = BankConfig()


def logo() -> Sketch:
    """generate the fenderbender logo!"""
    with BuildSketch() as sketch:
        with Locations(
            Location(
                (
                    -_config.frame_hanger_offset,
                    _config.minimum_structural_thickness / 2,
                )
            ),
            Location(
                (
                    -_config.frame_hanger_offset,
                    -_config.minimum_structural_thickness * 2.5,
                )
            ),
        ) as hangers:
            Rectangle(
                _config.frame_exterior_length,
                _config.frame_base_depth,
                align=(Align.CENTER, Align.MIN),
            )
        with Locations(
            Location(
                (
                    -_config.frame_hanger_offset,
                    _config.minimum_structural_thickness / 2,
                )
            )
        ) as frame:
            Rectangle(
                _config.frame_exterior_length / 2,
                _config.bracket_height,
                align=(Align.MAX, Align.MIN),
            )
        fillet(sketch.vertices(), _config.fillet_radius)
        Circle(_config.frame_bracket_exterior_radius)
        Circle(_config.wheel_radius, mode=Mode.SUBTRACT)
        Rectangle(
            _config.frame_bracket_exterior_diameter,
            _config.minimum_structural_thickness,
            align=(Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT,
        )
        with BuildLine() as toparc:
            CenterArc(
                (0, 0),
                _config.frame_bracket_exterior_radius
                - (
                    _config.frame_bracket_exterior_radius
                    - _config.wheel_radius
                )
                / 2,
                180,
                -180,
            )
        Text(
            "FENDER BENDER",
            12,
            font="Flamante Round Bold",
            font_style=FontStyle.BOLD,
            path=toparc.wire(),
            position_on_path=0.5,
            mode=Mode.SUBTRACT,
        )
        with BuildLine() as bottomarc:
            CenterArc(
                (0, 0),
                _config.frame_bracket_exterior_radius
                - (
                    _config.frame_bracket_exterior_radius
                    - _config.wheel_radius
                )
                / 2,
                360,
                -180,
            )
        Text(
            "FILAMENT BUFFER",
            12,
            font="Flamante Round Bold",
            font_style=FontStyle.BOLD,
            path=bottomarc.wire(),
            position_on_path=0.5,
            mode=Mode.SUBTRACT,
        )
        add(text())
        show(sketch, reset_camera=Camera.KEEP)
    return sketch


def text() -> Sketch:
    with BuildSketch() as fb2:
        with Locations(Location((14, 0))) as fb:
            Text(
                "FB",
                36,
                font="Flamante Round Bold",
                font_style=FontStyle.BOLD,
                align=(Align.MAX, Align.CENTER),
            ).move(Location((0, 10)))
        with Locations(Location((16, 10))) as two:
            Text(
                "²",
                36,
                font="Flamante Round Bold",
                font_style=FontStyle.BOLD,
                align=(Align.MIN, Align.CENTER),
            )
    return fb2.sketch


fb2_logo = logo().sketch
fb2_logo.color = (23, 63, 112)
show(fb2_logo, reset_camera=Camera.KEEP)

exporter = ExportSVG(scale=1.0)
exporter.add_layer(
    "Layer 1", fill_color=(23, 63, 112), line_color=(255, 255, 255)
)
exporter.add_shape(fb2_logo, "Layer 1")
exporter.write("../logo.svg")

with BuildPart() as logo_blue:
    extrude(fb2_logo.mirror(Plane.YZ),2)

with BuildPart() as logo_white:
    Box(_config.frame_exterior_length+20,_config.wheel_diameter+_config.frame_base_depth*2+40,3,
    align=(Align.CENTER,Align.CENTER,Align.MIN))
    add(logo_blue, mode=Mode.SUBTRACT)
blue = logo_blue.part
blue.color = (0,0,255)
white=logo_white.part
white.color = (255,255,255)
show(white, blue, reset_camera=Camera.KEEP)
export_stl(logo_blue.part, "../logo-blue.stl")
export_stl(logo_white.part, "../logo-white.stl")
