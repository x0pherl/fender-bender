from basic_shapes import screw_cut
from frame_common import chamber_cuts, core_cut, wallslots
from tongue_groove import groove_pair
from frame_config import TopFrameConfig
from partomatic import Partomatic
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

    _config: TopFrameConfig = TopFrameConfig()

    _standingframe: Part
    _hangingframe: Part
    _hybridframe: Part

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
            Location((-self._config.exterior_length / 2 - extra_length, 0, 0))
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
                    0,
                    self._config.base_depth * 2 + self._config.exterior_radius,
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
                        0,
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
                self._config.base_depth * 2 + self._config.exterior_radius,
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
                            0,
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
                            0,
                            self._config.exterior_radius
                            + self._config.base_depth,
                        )
                    )
                )
            )
        return cut.part

    def bottom_frame(self, standing: bool = True, hanging=False) -> Part:
        """
        creates the bottom frame
        -------
        arguments:
            - standing: whether the frame is standing or hanging
        """
        offset = self._config.interior_offset if hanging else 0
        extra_length = offset * 2
        with BuildPart() as bframe:
            add(self._bottom_base_block(offset, extra_length))
            if standing:
                add(self._bottom_frame_stand(extend=hanging))
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
                        self._config.interior_width
                        - self._config.bracket_spacing,
                        self._config.click_fit_radius,
                    ).mirror()
                )
            if standing and hanging:
                add(self._standing_screw_fitting(extra_length), mode=Mode.ADD)
                add(self._standing_screw_cut(), mode=Mode.SUBTRACT)
            elif hanging:
                add(self._hanging_screw_fitting(extra_length))
                add(self._hanging_screw_cut(), mode=Mode.SUBTRACT)

        return bframe.part

    def compile(self):
        self._standingframe = self.bottom_frame(standing=True, hanging=False)
        self._hangingframe = self.bottom_frame(standing=False, hanging=True)
        self._hybridframe = self.bottom_frame(standing=True, hanging=True)

    def display(self):
        show(
            self._hangingframe,
            self._hybridframe.move(
                Location(
                    (
                        0,
                        -self._config.exterior_width,
                        0,
                    )
                )
            ),
            self._standingframe.move(
                Location(
                    (
                        0,
                        self._config.exterior_width,
                        0,
                    )
                )
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        Path(output_directory / "alt").mkdir(parents=True, exist_ok=True)

        export_stl(
            self._hangingframe,
            str(Path(output_directory / "frame-bottom.stl")),
        )

        export_stl(
            self._hybridframe.rotate(Axis.X, 180).move(
                Location(
                    (
                        0,
                        0,
                        self._config.base_depth * 2
                        + self._config.exterior_radius,
                    )
                )
            ),
            str(Path(output_directory / "alt/frame-bottom-standing.stl")),
        )
        export_stl(
            self._standingframe.rotate(Axis.X, 180).move(
                Location(
                    (
                        0,
                        0,
                        self._config.base_depth * 2
                        + self._config.exterior_radius,
                    )
                )
            ),
            str(
                Path(
                    output_directory
                    / "alt/frame-bottom-standing-without-hanger.stl"
                )
            ),
        )

    def render_2d(self):
        pass

    def load_config(self, configuration: str, yaml_tree="bottom-frame"):
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

    def __init__(self, config: TopFrameConfig = None):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - config: a GuidewallConfig ojbect
        """
        super(Partomatic, self).__init__()

        if config:
            self.load_config({"bottom-frame": asdict(config)})
        else:
            self._config = TopFrameConfig()


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    frame = BottomFrame(bender_config.top_frame_config)
    frame.compile()
    frame.display()
    frame.export_stls()
