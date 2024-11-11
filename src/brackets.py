"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""

from dataclasses import asdict
from enum import Enum, auto
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    FilletPolyline,
    GridLocations,
    Line,
    Location,
    Mode,
    Part,
    PolarLocations,
    Polyline,
    Rectangle,
    Sketch,
    CenterArc,
    Circle,
    CenterArc,
    Cylinder,
    add,
    chamfer,
    export_stl,
    extrude,
    make_face,
)

from ocp_vscode import Camera, show

from bender_config import BenderConfig
from partomatic import Partomatic
from basic_shapes import screw_cut, heatsink_cut, nut_cut
from frame_config import FrameConfig
from wall_hanger_cut_template import wall_hanger_cut_template


class NutStyle(Enum):
    """What sort of frame to have"""

    HEATSINK = auto()
    NUT = auto()


class Brackets(Partomatic):
    """
    A Partomatic for the top frame
    """

    _config: FrameConfig = FrameConfig()

    _wall_hanger: Part
    _desk_hanger_heatsink: Part
    _desk_hanger_nut: Part
    _desk_alignment_tool: Part

    def _desk_bracket_profile(self) -> Sketch:
        curve_unit = (
            self._config.bracket_height - self._config.base_depth
        ) / 2
        with BuildSketch() as profile:
            with BuildLine() as ln:
                l1 = Line(
                    (
                        -self._config.bracket_height - self._config.base_depth,
                        0,
                    ),
                    (0, 0),
                )
                l2 = Line(l1 @ 1, (0, self._config.bracket_height))
                curve1 = CenterArc(
                    (0, curve_unit + self._config.base_depth),
                    curve_unit,
                    90,
                    90,
                )
                curve2 = CenterArc(
                    (-curve_unit * 2, self._config.base_depth + curve_unit),
                    curve_unit,
                    0,
                    -90,
                )
                l3 = Line(
                    curve2 @ 1,
                    (-self._config.bracket_height, self._config.base_depth),
                )
                CenterArc(
                    (-self._config.bracket_height, 0),
                    self._config.base_depth,
                    90,
                    90,
                )
            make_face()
        return profile.sketch

    def _desk_bracket_base(self) -> Part:
        with BuildPart() as base:
            extrude(
                self._desk_bracket_profile(),
                self._config.exterior_width / 2,
                both=True,
            )
            chamfer(
                base.part.edges()
                - base.faces().sort_by(Axis.X)[-1].edges()
                - base.faces().sort_by(Axis.Y)[0].edges(),
                2,
            )
        return base.part.rotate(Axis.X, 90)

    def _desk_aligner(self) -> Part:
        with BuildPart() as tool:
            Box(
                self._config.bracket_height,
                self._config.exterior_width,
                self._config.minimum_thickness,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
            Box(
                self._config.minimum_structural_thickness,
                self._config.exterior_width,
                self._config.bracket_depth,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Location(
                    (
                        -self._config.bracket_height
                        + self._config.screw_head_radius,
                        0,
                        0,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.exterior_width
                    - self._config.bracket_depth * 2,
                    1,
                    2,
                ):
                    Cylinder(
                        self._config.m4_shaft_radius,
                        self._config.minimum_thickness,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
        return tool.part

    def _desk_bracket(self, nut_style: NutStyle = NutStyle.NUT) -> Part:
        with BuildPart() as bracket:
            add(self._desk_bracket_base())
            add(
                wall_hanger_cut_template(
                    self._config.minimum_structural_thickness * 1.5,
                    self._config.exterior_width
                    - self._config.minimum_structural_thickness * 2,
                    self._config.bracket_height,
                    bottom=False,
                    post_count=self._config.wall_bracket_post_count,
                    tolerance=-self._config.tolerance,
                )
            )
            with BuildPart(
                Location(
                    (
                        -self._config.bracket_height
                        + self._config.screw_head_radius,
                        0,
                        self._config.base_depth,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.exterior_width
                    - self._config.bracket_depth * 2,
                    1,
                    2,
                ):
                    if nut_style == NutStyle.NUT:
                        add(
                            nut_cut(
                                self._config.m4_nut_radius,
                                self._config.m4_nut_depth,
                                self._config.screw_shaft_radius,
                                self._config.exterior_length,
                            ).rotate(Axis.X, 180)
                        )
                    else:
                        add(
                            heatsink_cut(
                                self._config.m4_heatsink_radius,
                                self._config.m4_heatsink_depth,
                                self._config.m4_shaft_radius,
                                self._config.exterior_length,
                            ).rotate(Axis.X, 180)
                        )

        part = bracket.part
        part.label = "Desk Hanger Bracket"
        return part

    def _wall_bracket(self) -> Part:
        """
        generates the wall hanger for the top frame
        """
        with BuildPart() as hanger:
            add(
                wall_hanger_cut_template(
                    self._config.minimum_structural_thickness * 1.5,
                    self._config.exterior_width
                    - self._config.minimum_structural_thickness * 2,
                    self._config.bracket_height,
                    bottom=False,
                    post_count=self._config.wall_bracket_post_count,
                    tolerance=-self._config.tolerance,
                )
            )
            with BuildPart(
                Location(
                    (
                        self._config.minimum_structural_thickness,
                        0,
                        self._config.bracket_height / 2,
                    ),
                    (0, -90, 0),
                ),
                mode=Mode.SUBTRACT,
            ):
                add(
                    screw_cut(
                        self._config.screw_head_radius,
                        self._config.screw_head_sink,
                        self._config.screw_shaft_radius,
                        self._config.exterior_length,
                    )
                )
        return hanger.part

    def compile(self):
        self._wall_hanger = self._wall_bracket()
        self._desk_hanger_heatsink = self._desk_bracket(NutStyle.HEATSINK)
        self._desk_hanger_nut = self._desk_bracket(NutStyle.NUT)
        self._desk_alignment_tool = self._desk_aligner()

    def display(self):
        show(
            self._wall_hanger.move(
                Location((0, self._config.exterior_width, 0))
            ),
            self._desk_hanger_heatsink,
            self._desk_alignment_tool.mirror().move(
                Location((0, 0, -self._config.bracket_depth))
            ),
            self._desk_hanger_nut.move(
                Location((0, -self._config.exterior_width, 0))
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        Path(output_directory / "alt").mkdir(parents=True, exist_ok=True)
        Path(output_directory / "tools").mkdir(parents=True, exist_ok=True)

        export_stl(
            self._wall_hanger,
            str(Path(output_directory / "frame-wall-bracket.stl")),
        )
        export_stl(
            self._desk_hanger_heatsink,
            str(
                Path(
                    output_directory / "alt/frame-desktop-bracket-heatsink.stl"
                )
            ),
        )
        export_stl(
            self._desk_hanger_nut,
            str(Path(output_directory / "alt/frame-desktop-bracket-nut.stl")),
        )
        export_stl(
            self._desk_alignment_tool,
            str(Path(output_directory / "tools/desk-alignment-tool.stl")),
        )

    def render_2d(self):
        pass

    def load_config(self, configuration: str, yaml_tree="frame"):
        """
        loads a sidewall configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the wheel configuration node,
            separated by slashes (example: "BenderConfig/ConnectorFrame")
        """
        self._config.load_config(configuration, yaml_tree)

    def __init__(self, config: FrameConfig = None):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - config: a GuidewallConfig ojbect
        """
        super(Partomatic, self).__init__()

        if config:
            self.load_config({"frame": asdict(config)})
        else:
            self._config = FrameConfig()


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    brackets = Brackets(bender_config.frame_config)
    brackets.compile()
    brackets.display()
    brackets.export_stls()
