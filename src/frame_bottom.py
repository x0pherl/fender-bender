from fb_library import screw_cut
from frame_common import chamber_cuts, core_cut, wallslots
from tongue_groove import groove_pair
from frame_config import FrameConfig, FrameStyle
from partomatic import AutomatablePart, Partomatic
from bender_config import BenderConfig

from dataclasses import asdict
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    GridLocations,
    Location,
    Mode,
    Part,
    add,
    export_stl,
    fillet,
)
from ocp_vscode import Camera, show


class BottomFrame(Partomatic):
    """
    A Partomatic for the bottom frame
    """

    _config: FrameConfig = FrameConfig()

    def _bottom_base_block(
        self, offset: float = 0, extra_length: float = 0
    ) -> Part:
        """the basic top shape of the frame before any cuts are made out"""
        with BuildPart() as base:
            with BuildPart(Location((-offset, 0, 0))):
                Box(
                    self._config.exterior_length + extra_length,
                    self._config.exterior_width,
                    self._config.base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location(
                    (
                        0,
                        0,
                        self._config.base_depth,
                    )
                )
            ):
                Cylinder(
                    radius=self._config.exterior_radius,
                    height=self._config.exterior_width,
                    rotation=(90, 0, 0),
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                )
            edge_set = base.edges() - base.edges().filter_by_position(
                Axis.X,
                minimum=self._config.exterior_radius + offset - 1,
                maximum=self._config.exterior_radius + offset + 1,
            )
            fillet(edge_set, self._config.fillet_radius)
        return base.part

    def _hanging_screw_fitting(self, extra_length) -> Part:
        """
        a fitting for screwing the bracket to the wall
        """
        with BuildPart(
            Location(
                (
                    -self._config.exterior_length / 2 - extra_length,
                    self._config.screw_offset,
                    0,
                )
            )
        ) as fitting:
            Box(
                self._config.base_depth,
                self._config.bracket_spacing,
                self._config.exterior_radius / 2,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            fillet(
                fitting.faces().edges()
                - fitting.faces().sort_by(Axis.X)[0].edges()
                + fitting.faces().sort_by(Axis.Z)[0].edges(),
                self._config.fillet_radius,
            )
        screwfitting = fitting.part
        screwfitting.label = "Screw Fitting"
        return screwfitting

    def _standing_screw_fitting(self, offset) -> Part:
        """
        a fitting for screwing the bracket to the wall
        """
        base_width = (
            self._config.exterior_radius / 2 + self._config.fillet_radius
        )
        with BuildPart(
            Location(
                (
                    -self._config.exterior_length / 2 - offset,
                    self._config.screw_offset,
                    self._config.stand_depth,
                )
            )
        ) as fitting:
            Box(
                base_width,
                self._config.bracket_spacing - self._config.wall_thickness,
                base_width,
                align=(Align.MIN, Align.CENTER, Align.MAX),
            )
            fillet(
                fitting.faces()
                .sort_by(Axis.Z)[-1]
                .edges()
                .filter_by(Axis.Y)
                .sort_by(Axis.X)[0],
                self._config.fillet_radius,
            )
            with BuildPart(
                Location(
                    (
                        -self._config.exterior_length / 2
                        - offset
                        + base_width
                        - self._config.fillet_radius * 1.5,
                        self._config.screw_offset,
                        self._config.base_depth * 2
                        + self._config.exterior_radius,
                    ),
                    (0, 45, 0),
                ),
                mode=Mode.SUBTRACT,
            ) as cut:
                Box(
                    base_width * 2,
                    self._config.bracket_spacing - self._config.wall_thickness,
                    base_width * 5,
                    align=(Align.MIN, Align.CENTER, Align.CENTER),
                )
                fillet(cut.edges(), self._config.fillet_radius)
        screwfitting = fitting.part
        screwfitting.label = "Screw Fitting"
        return screwfitting

    def _bottom_frame_stand(self, extend=False) -> Part:
        """
        a stand for balancing the bottom bracket when sitting on a flat surface
        instead of hanging from a wall
        """
        offset = self._config.interior_offset if extend else 0
        extra_length = offset * 2

        with BuildPart(Location((-offset, 0, 0))) as stand:
            Box(
                self._config.exterior_length + extra_length,
                self._config.exterior_width,
                self._config.stand_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Box(
                self._config.exterior_length - self._config.base_depth * 2,
                self._config.exterior_width,
                self._config.base_depth
                + self._config.exterior_radius
                - self._config.fillet_radius / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
            fillet(stand.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((-offset, 0, self._config.base_depth)),
                mode=Mode.SUBTRACT,
            ) as longcuts:
                with GridLocations(
                    0,
                    self._config.bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    Box(
                        self._config.exterior_length + extra_length,
                        self._config.bracket_spacing
                        - self._config.wall_thickness,
                        self._config.exterior_radius,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                fillet(
                    longcuts.edges().filter_by(Axis.X),
                    self._config.fillet_radius,
                )
        return stand.part

    def _hanging_screw_cut(self):
        with BuildPart() as cut:
            add(
                screw_cut(
                    head_radius=self._config.screw_head_radius,
                    head_sink=self._config.screw_head_sink,
                    shaft_radius=self._config.screw_shaft_radius,
                    shaft_length=self._config.exterior_length,
                    bottom_clearance=self._config.exterior_length,
                )
                .rotate(Axis.Y, -135)
                .move(
                    Location(
                        (
                            -self._config.exterior_length / 2
                            + self._config.screw_shaft_radius,
                            self._config.screw_offset,
                            self._config.exterior_radius / 4,
                        )
                    )
                )
            )
        return cut.part

    def _standing_screw_cut(self):
        with BuildPart() as cut:
            add(
                screw_cut(
                    head_radius=self._config.screw_head_radius,
                    head_sink=self._config.screw_head_sink,
                    shaft_radius=self._config.screw_shaft_radius,
                    shaft_length=self._config.exterior_length,
                    bottom_clearance=self._config.exterior_length,
                )
                .rotate(Axis.Y, -135)
                .move(
                    Location(
                        (
                            -self._config.exterior_length / 2
                            - self._config.interior_offset * 2
                            + self._config.exterior_radius / 8,
                            self._config.screw_offset,
                            self._config.exterior_radius
                            + self._config.base_depth,
                        )
                    )
                )
            )
        return cut.part

    def _dry_box(self, extend=False) -> Part:
        offset = self._config.interior_offset if extend else 0
        extra_length = offset * 2
        with BuildPart(
            Location(
                (
                    -offset,
                    0,
                    self._config.base_depth,
                )
            )
        ) as dry:
            Box(
                self._config.exterior_length
                - self._config.base_depth * 2
                + self._config.minimum_thickness * 2,
                self._config.exterior_width - self._config.fillet_radius * 2,
                self._config.stand_depth - self._config.base_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Location(
                    (
                        0,
                        0,
                        self._config.base_depth,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.exterior_diameter,
                    self._config.exterior_width,
                    self._config.base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )
                Cylinder(
                    radius=self._config.exterior_radius,
                    height=self._config.exterior_width,
                    rotation=(90, 0, 0),
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )
            with BuildPart(mode=Mode.SUBTRACT):
                add(
                    chamber_cuts(
                        count=self._config.filament_count,
                        spacing=self._config.bracket_spacing,
                        length=self._config.interior_length,
                        width=self._config.bracket_spacing
                        - self._config.wall_thickness,
                        depth=self._config.stand_depth
                        - self._config.minimum_thickness,
                        fillet_radius=self._config.fillet_radius,
                    )
                )
        return dry.part

    def bottom_frame(self) -> Part:
        """
        creates the bottom frame
        -------
        arguments:
            - standing: whether the frame is standing or hanging
        """
        offset = (
            self._config.interior_offset
            if FrameStyle.HANGING in self._config.frame_style
            else 0
        )
        extra_length = offset * 2
        with BuildPart() as bframe:
            add(self._bottom_base_block(offset, extra_length))
            if FrameStyle.STANDING in self._config.frame_style:
                add(
                    self._bottom_frame_stand(
                        extend=FrameStyle.HANGING in self._config.frame_style
                    )
                )
            with BuildPart(Location((0, 0, 0)), mode=Mode.SUBTRACT):
                add(
                    core_cut(
                        self._config.interior_radius,
                        self._config.exterior_width,
                        self._config.base_depth,
                    )
                )
                add(
                    chamber_cuts(
                        count=self._config.filament_count,
                        spacing=self._config.bracket_spacing,
                        length=self._config.interior_length,
                        width=self._config.bracket_spacing
                        - self._config.wall_thickness,
                        depth=self._config.exterior_diameter,
                        fillet_radius=self._config.fillet_radius,
                    )
                )
                add(
                    wallslots(
                        wall_distance=self._config.bracket_spacing,
                        count=self._config.filament_count + 1,
                        wall_thickness=self._config.wall_thickness,
                        length=self._config.interior_length
                        + self._config.wall_thickness * 2,
                        interior_radius=self._config.interior_radius,
                        base_depth=self._config.base_depth,
                    )
                )
                add(
                    groove_pair(
                        self._config.groove_distance,
                        self._config.wall_thickness,
                        self._config.interior_width,
                        self._config.groove_depth,
                        self._config.tolerance,
                        self._config.click_fit_distance,
                        self._config.click_fit_radius,
                    ).mirror()
                )
            if self._config.drybox:
                add(
                    self._dry_box(
                        extend=FrameStyle.HANGING in self._config.frame_style
                    )
                )
            if (
                FrameStyle.STANDING in self._config.frame_style
                and FrameStyle.HANGING in self._config.frame_style
            ):
                add(self._standing_screw_fitting(extra_length), mode=Mode.ADD)
                add(self._standing_screw_cut(), mode=Mode.SUBTRACT)
            elif FrameStyle.HANGING in self._config.frame_style:
                add(self._hanging_screw_fitting(extra_length))
                add(self._hanging_screw_cut(), mode=Mode.SUBTRACT)
        return bframe.part

    def compile(self):
        bottom_frame_location = (
            Location((0, 0, 0), (0, 0, 0))
            if self._config.frame_style == FrameStyle.HANGING
            else Location((0, 0, self._config.stand_depth), (180, 0, 0))
        )
        self.parts.clear()
        self.parts.append(
            AutomatablePart(
                self.bottom_frame().move(bottom_frame_location),
                "frame-bottom",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/debug.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
    bender_config = BenderConfig(config_path)
    frame_config = bender_config.frame_config
    frame = BottomFrame(frame_config)
    frame.compile()
    frame.display()
    frame.export_stls()
