"""
Generates filament ingress and egress shapes
"""

from enum import Enum, auto
from math import sqrt
from pathlib import Path

from bd_warehouse.thread import TrapezoidalThread
from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    Compound,
    Cylinder,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    add,
    extrude,
    fillet,
    loft,
    sweep,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from filament_bracket_config import FilamentBracketConfig, ChannelPairDirection
from partomatic import BuildablePart, Partomatic


class ChannelMode(Enum):
    """
    the type of channel
    -------
    options:
        - SOLID: a solid block with no filament path
        - CUT_PATH: a curved channel
    """

    SOLID = auto()
    CUT_PATH = auto()
    COMPLETE = auto()


class FilamentChannels(Partomatic):
    """a partomatic for the filament ingress and egress channels"""

    _config = FilamentBracketConfig()

    channel_mode: ChannelMode = ChannelMode.COMPLETE
    render_threads: bool = True

    def _connector_threads(self) -> Part:
        """
        returns the threads for the connector
        """
        with BuildPart() as threads:
            TrapezoidalThread(
                diameter=self._config.connector.diameter,
                pitch=self._config.connector.thread_pitch,
                length=self._config.connector.length,
                thread_angle=self._config.connector.thread_angle,
                external=False,
                interference=self._config.connector.thread_interference,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=self._config.connector.radius,
                height=self._config.connector.length
                - self._config.minimum_thickness / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.INTERSECT,
            )
        part = threads.part
        part.label = "connector threads"
        return part

    def straight_filament_path_cut(self) -> Part:
        """
        creates a cutout for a filament tube allowing for the connector, and
        a tube stop with a funnel entry
        """
        with BuildPart(mode=Mode.PRIVATE) as tube:
            with BuildPart():
                with BuildSketch(Plane.XY):
                    Circle(
                        radius=self._config.connector.tube.outer_diameter
                        * 0.75
                    )
                    Rectangle(
                        width=self._config.connector.tube.outer_diameter * 2,
                        height=self._config.wheel.bearing.depth
                        + self._config.wheel.lateral_tolerance,
                        mode=Mode.INTERSECT,
                    )
                with BuildSketch(
                    Plane.XY.offset(self._config.filament_funnel_height)
                ):
                    Circle(radius=self._config.connector.tube.inner_radius)
                loft()
            with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
                Cylinder(
                    radius=self._config.connector.tube.outer_radius,
                    height=self._config.bracket_height
                    - self._config.filament_funnel_height
                    - self._config.connector.length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
                Cylinder(
                    radius=self._config.connector.radius,
                    height=self._config.connector.length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildSketch(
                Plane.XY.offset(
                    self._config.bracket_height
                    - self._config.minimum_thickness / 2
                )
            ):
                Circle(radius=self._config.connector.radius)
            with BuildSketch(Plane.XY.offset(self._config.bracket_height)):
                Circle(
                    radius=self._config.connector.radius
                    + self._config.minimum_thickness / 2
                )
            loft()
            if self.render_threads and self._config.connector.threaded:
                with BuildPart(
                    Location(
                        (
                            0,
                            0,
                            self._config.bracket_height
                            - self._config.minimum_thickness / 2,
                        ),
                        (180, 0, 0),
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(self._connector_threads())

        with BuildPart(
            Location((0, 0, self._config.bracket_depth / 2), (-90, 0, 0))
        ) as cut:
            add(tube)
        part = cut.part
        part.label = "straight tube cut"
        return part

    def straight_filament_block_solid(self) -> Part:
        """
        builds the solid reinforcement for the filaement ingress channel
        """
        with BuildPart(Location((0, 0, 0), (-90, 0, 0))) as ingress:
            Box(
                self._config.bracket_depth,
                self._config.bracket_depth,
                self._config.bracket_height,
                align=(Align.CENTER, Align.MAX, Align.MIN),
            )
            fillet(
                ingress.edges().filter_by(Axis.Y)
                + ingress.faces().sort_by(Axis.Y)[0].edges().filter_by(Axis.X),
                self._config.fillet_radius,
            )
        return ingress.part

    def straight_filament_block(self) -> Part:
        """
        builds a straight filaement channel with the cut in place
        """
        with BuildPart() as path:
            add(self.straight_filament_block_solid())
            if self.channel_mode == ChannelMode.COMPLETE:
                with BuildPart(mode=Mode.SUBTRACT):
                    add(self.straight_filament_path_cut())
        part = path.part
        part.label = "filament path"
        return part

    def _curved_filament_line(self) -> Compound:
        """
        returns a compund with three line segments representing the
        channel for the ingress funnel, the PTFE tube,
        and the connector
        """
        with BuildLine(mode=Mode.PRIVATE):
            funnel = Line((0, 0), (0, self._config.filament_funnel_height))
            bridge = Line(
                funnel @ 1,
                (
                    0,
                    self._config.filament_funnel_height
                    + self._config.minimum_structural_thickness,
                ),
            )
            curve = CenterArc(
                center=(self._config.wheel.radius, (bridge @ 1).Y),
                radius=self._config.wheel.radius,
                start_angle=180,
                arc_size=-45,
            )
            with BuildLine(
                Plane(
                    origin=curve @ 1,
                    z_dir=curve % 1,
                )
            ):
                output = Line(
                    (0, 0),
                    (0, 0, self._config.connector.length),
                )
            bridge.label = "input"
            bridge.color = "RED"
            curve.label = "curve"
            curve.color = "BLUE"
            output.label = "output"
            output.color = "GREEN"
        lines = Compound(children=(funnel, bridge, curve, output))
        return lines

    def curved_filament_path_cut(self) -> Compound:
        """
        returns the shape to be cut out of a curved filament path
        allowing for the PTFE tube and the connector
        """
        path = self._curved_filament_line()
        with BuildPart() as complete:
            with BuildPart() as inlet:
                with BuildLine() as intake:
                    add(path.children[0])
                with BuildSketch(
                    Plane(origin=intake.line @ 0, z_dir=intake.line % 0)
                ):
                    Circle(
                        radius=self._config.connector.tube.outer_diameter
                        * 0.75
                    )
                    Rectangle(
                        height=self._config.connector.tube.outer_diameter * 2,
                        width=self._config.wheel.bearing.depth
                        + self._config.wheel.lateral_tolerance,
                        mode=Mode.INTERSECT,
                    )
                with BuildSketch(
                    Plane(origin=intake.line @ 1, z_dir=intake.line % 1)
                ):
                    Circle(self._config.connector.tube.inner_radius)
                loft()
                extrude(
                    inlet.faces().sort_by(Axis.Y)[0],
                    self._config.bracket_depth,
                )
            with BuildPart() as tube:
                with BuildLine() as tube_path:
                    add(path.children[1])
                with BuildSketch(
                    Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
                ):
                    Circle(self._config.connector.tube.outer_radius)
                sweep()
            with BuildPart() as tube_curve:
                with BuildLine() as tube_path:
                    add(path.children[2])
                with BuildSketch(
                    Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
                ):
                    Circle(self._config.connector.tube.outer_radius)
                sweep()
            with BuildPart() as connector:
                with BuildLine() as connector_path:
                    add(path.children[3])
                with BuildSketch(
                    Plane(
                        origin=connector_path.line @ 0,
                        z_dir=connector_path.line % 0,
                    )
                ):
                    Circle(self._config.connector.radius)
                sweep()
            with BuildPart() as connector_chamfer:
                with BuildSketch(
                    Plane(
                        origin=connector_path.line @ 1,
                        z_dir=connector_path.line % 1,
                    )
                ):
                    Circle(
                        self._config.connector.radius
                        + self._config.minimum_thickness / 2
                    )
                with BuildSketch(
                    Plane(
                        origin=connector_path.line @ 1,
                        z_dir=connector_path.line % 1,
                    ).offset(-self._config.minimum_thickness / 2)
                ):
                    Circle(self._config.connector.radius)
                loft()
                extrude(
                    connector_chamfer.faces().sort_by(Axis.X)[-1],
                    self._config.bracket_depth,
                )
            if self.render_threads and self._config.connector.threaded:
                with BuildPart(
                    Plane(
                        origin=connector_path.line @ 1,
                        z_dir=(connector_path.line % 1).reverse(),
                    ).offset(self._config.minimum_thickness / 2),
                    mode=Mode.SUBTRACT,
                ):
                    add(self._connector_threads())

        return complete.part.move(
            Location((0, 0, self._config.bracket_depth / 2))
        )

    def curved_filament_block_solid(self, top_exit_fillet=True) -> Part:
        """
        The solid shape for the channel around a curved filament path
        optionally
        -------
        arguments:
            - top_exit_fillet: set to false to render a clean intersection with
                box immediately to the left of the exit
        """
        with BuildPart() as solid_path:
            with BuildLine() as curve:
                add(self._curved_filament_line())
            with BuildSketch(
                Plane(origin=curve.line @ 0, z_dir=curve.line % 0)
            ) as path_face:
                Rectangle(
                    self._config.bracket_depth, self._config.bracket_depth
                )
                fillet(path_face.vertices(), self._config.fillet_radius)
            sweep()
            if not top_exit_fillet:
                with BuildLine() as curve2:
                    add(self._curved_filament_line().children[1])
                    add(self._curved_filament_line().children[2])
                with BuildSketch(
                    Plane(origin=curve2.line @ 0, z_dir=curve2.line % 0)
                ) as path_face:
                    Rectangle(
                        self._config.bracket_depth,
                        self._config.bracket_depth / 2,
                        align=(Align.CENTER, Align.MAX),
                    )
                sweep()
            fillet(
                solid_path.faces()
                .sort_by(Axis.Y)[0]
                .edges()
                .filter_by(Axis.X),
                self._config.fillet_radius,
            )
        part = solid_path.part.move(
            Location((0, 0, self._config.bracket_depth / 2))
        )
        part.label = "curved filament path"
        return part

    def curved_filament_block(self, top_exit_fillet=False) -> Part:
        """
        builds a straight filaement channel with the cut in place
        -------
        arguments:
            - top_exit_fillet: set to false to render a clean intersection with
                box immediately to the left of the exit
        """
        with BuildPart() as path:
            add(self.curved_filament_block_solid(top_exit_fillet))
            if self.channel_mode == ChannelMode.COMPLETE:
                with BuildPart(mode=Mode.SUBTRACT):
                    add(self.curved_filament_path_cut())
        part = path.part
        part.label = "filament path"
        return part

    def compile(self):
        """
        Builds the relevant parts for the filament channels
        """
        left: Part
        right: Part

        self.parts.clear()
        if (
            self._config.channel_pair_direction
            == ChannelPairDirection.LEAN_REVERSE
        ):
            if self.channel_mode == ChannelMode.CUT_PATH:
                left = self.curved_filament_path_cut().mirror(Plane.YZ)
            else:
                left = self.curved_filament_block(top_exit_fillet=True).mirror(
                    Plane.YZ
                )
        else:
            if self.channel_mode == ChannelMode.CUT_PATH:
                left = self.straight_filament_path_cut()
            else:
                left = self.straight_filament_block()
        left = left.move(Location((-self._config.wheel.radius, 0, 0)))
        if (
            self._config.channel_pair_direction
            == ChannelPairDirection.LEAN_FORWARD
        ):
            if self.channel_mode == ChannelMode.CUT_PATH:
                right = self.curved_filament_path_cut()
            else:
                right = self.curved_filament_block(top_exit_fillet=True)
        else:
            if self.channel_mode == ChannelMode.CUT_PATH:
                right = self.straight_filament_path_cut()
            else:
                right = self.straight_filament_block()

        right = right.move(Location((self._config.wheel.radius, 0, 0)))
        with BuildPart() as channels:
            add(left)
            add(right)
        channels.part.label = "filament channels"
        self.parts.append(
            BuildablePart(
                channels.part,
                "filament-bracket-channels",
                stl_folder="NONE",
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/reference.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    bracket_config = bender_config.filament_bracket_config
    channels = FilamentChannels(bracket_config)
    channels.channel_mode = ChannelMode.COMPLETE
    channels.compile()
    channels.display()
