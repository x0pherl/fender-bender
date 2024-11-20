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
    GridLocations,
    Line,
    Location,
    Mode,
    Part,
    Sketch,
    CenterArc,
    CenterArc,
    Cylinder,
    add,
    fillet,
    export_stl,
    extrude,
    make_face,
)

from ocp_vscode import Camera, show

from bender_config import BenderConfig
from partomatic import BuildablePart, Partomatic
from basic_shapes import screw_cut, heatsink_cut, nut_cut
from frame_config import FrameConfig

from hanging_bracket_config import (
    HangingBracketConfig,
    HangingBracketStyle,
)
from wall_hanger_cut_template import wall_hanger_cut_template


class HangingBracket(Partomatic):
    """
    A Partomatic for the top frame
    """

    _config: HangingBracketConfig = HangingBracketConfig()

    def _desk_bracket_profile(self) -> Sketch:
        curve_unit = (self._config.height - self._config.arm_thickness) / 2
        with BuildSketch() as profile:
            with BuildLine() as ln:
                l1 = Line(
                    (
                        -self._config.height - self._config.arm_thickness,
                        0,
                    ),
                    (0, 0),
                )
                l2 = Line(l1 @ 1, (0, self._config.height))
                curve1 = CenterArc(
                    (0, curve_unit + self._config.arm_thickness),
                    curve_unit,
                    90,
                    90,
                )
                curve2 = CenterArc(
                    (-curve_unit * 2, self._config.arm_thickness + curve_unit),
                    curve_unit,
                    0,
                    -90,
                )
                l3 = Line(
                    curve2 @ 1,
                    (-self._config.height, self._config.arm_thickness),
                )
                CenterArc(
                    (-self._config.height, 0),
                    self._config.arm_thickness,
                    90,
                    90,
                )
            make_face()
        return profile.sketch

    def _desk_bracket_base(self) -> Part:
        with BuildPart() as base:
            extrude(
                self._desk_bracket_profile(),
                self._config.width / 2,
                both=True,
            )
            fillet(
                base.part.edges()
                - base.faces().sort_by(Axis.X)[-1].edges()
                - base.faces().sort_by(Axis.Y)[0].edges(),
                self._config.fillet_radius,
            )
        return base.part.rotate(Axis.X, 90)

    def _desk_aligner(self) -> Part:
        with BuildPart() as tool:
            Box(
                self._config.height,
                self._config.width,
                self._config.bracket_inset / 4,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
            Box(
                self._config.bracket_inset,
                self._config.width,
                self._config.arm_thickness * 2,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Location(
                    (
                        -self._config.height + self._config.screw_head_radius,
                        0,
                        0,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.width - self._config.arm_thickness * 3,
                    1,
                    2,
                ):
                    Cylinder(
                        self._config.m4_shaft_radius,
                        self._config.bracket_inset / 4,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
        return tool.part

    def _desk_bracket(self, heatsink_nut=False) -> Part:
        with BuildPart() as bracket:
            add(self._desk_bracket_base())
            add(
                wall_hanger_cut_template(
                    self._config.bracket_inset * 1.5,
                    self._config.width - self._config.bracket_inset * 2,
                    self._config.height,
                    bottom=False,
                    post_count=self._config.post_count,
                    tolerance=-self._config.tolerance,
                )
            )
            with BuildPart(
                Location(
                    (
                        -self._config.height + self._config.screw_head_radius,
                        0,
                        self._config.arm_thickness,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.width - self._config.arm_thickness * 3,
                    1,
                    2,
                ):
                    if heatsink_nut:
                        add(
                            heatsink_cut(
                                self._config.m4_heatsink_radius,
                                self._config.m4_heatsink_depth,
                                self._config.m4_shaft_radius,
                                self._config.height,
                            ).rotate(Axis.X, 180)
                        )
                    else:
                        add(
                            nut_cut(
                                self._config.m4_nut_radius,
                                self._config.m4_nut_depth,
                                self._config.screw_shaft_radius,
                                self._config.height,
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
                    self._config.bracket_inset * 1.5,
                    self._config.width - self._config.bracket_inset * 2,
                    self._config.height,
                    bottom=False,
                    post_count=self._config.post_count,
                    tolerance=-self._config.tolerance,
                )
            )
            with BuildPart(
                Location(
                    (
                        self._config.bracket_inset,
                        0,
                        self._config.height / 2,
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
                        self._config.height,
                    )
                )
        return hanger.part

    def compile(self):
        self.parts.clear()
        if self._config.bracket_style == HangingBracketStyle.SURFACE_TOOL:
            self.parts.append(
                BuildablePart(
                    self._desk_aligner(),
                    "surface-mount--alignment-tool",
                    stl_folder=self._config.stl_folder,
                )
            )
        elif self._config.bracket_style == HangingBracketStyle.SURFACE_MOUNT:
            self.parts.append(
                BuildablePart(
                    self._desk_bracket(self._config.heatsink_desk_nut),
                    "frame-surface-mount-bracket",
                    stl_folder=self._config.stl_folder,
                )
            )
        else:
            self.parts.append(
                BuildablePart(
                    self._wall_bracket(),
                    "frame-wall-bracket",
                    stl_folder=self._config.stl_folder,
                )
            )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)

    print(bender_config.hanging_bracket_config)
    brackets = HangingBracket(bender_config.hanging_bracket_config)
    brackets._config.bracket_style = HangingBracketStyle.SURFACE_TOOL
    brackets.compile()
    brackets.display()
    brackets.export_stls()
