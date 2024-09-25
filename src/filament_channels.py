"""
Generates filament ingress and egress shapes
"""

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
from partomatic import Partomatic


class FilamentChannels(Partomatic):
    """a partomatic for the filament ingress and egress channels"""

    _config = BenderConfig()
    _curvedfilamentpath: Part
    _straightfilamentpath: Part

    def _connector_threads(self, connector_index=0) -> Part:
        """
        returns the threads for the connector
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        with BuildPart() as threads:
            TrapezoidalThread(
                diameter=self._config.connectors[connector_index].diameter,
                pitch=self._config.connectors[connector_index].thread_pitch,
                length=self._config.connectors[connector_index].length
                - self._config.minimum_thickness / 2,
                thread_angle=self._config.connectors[
                    connector_index
                ].thread_angle,
                external=False,
                interference=self._config.connectors[
                    connector_index
                ].thread_interference,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=self._config.connectors[connector_index].radius,
                height=self._config.connectors[connector_index].length
                - self._config.minimum_thickness / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.INTERSECT,
            )
        part = threads.part
        part.label = "connector threads"
        return part

    def straight_filament_connector_threads(self, connector_index=0) -> Part:
        """
        the threads for the ingress connector
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        with BuildPart(
            Location(
                (
                    0,
                    self._config.bracket_height
                    - self._config.minimum_thickness / 2,
                    self._config.bracket_depth / 2,
                ),
                (90, 0, 0),
            )
        ) as threads:
            add(self._connector_threads(connector_index=connector_index))
        part = threads.part
        part.label = "connector threads"
        return part

    def curved_filament_connector_threads(self, connector_index=0) -> Part:
        """
        places the threads for the curved filament connector
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        with BuildLine() as path:
            add(self._curved_filament_line())
        offset = (self._config.minimum_thickness / 2) / sqrt(2)
        with BuildPart(
            Location(
                (
                    (path.line @ 1).X - offset,
                    (path.line @ 1).Y - offset,
                    self._config.bracket_depth / 2,
                ),
                (90, -45, 0),
            )
        ) as threads:
            add(self._connector_threads(connector_index=connector_index))
        part = threads.part
        part.label = "connector threads"
        return part

    def straight_filament_path_cut(self, connector_index=0) -> Part:
        """
        creates a cutout for a filament tube allowing for the connector, and
        a tube stop with a funnel entry
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        with BuildPart(mode=Mode.PRIVATE) as tube:
            with BuildPart():
                with BuildSketch(Plane.XY.offset(0)):
                    Circle(
                        radius=self._config.connectors[
                            connector_index
                        ].tube.outer_diameter
                        * 0.75
                    )
                    Rectangle(
                        width=self._config.connectors[
                            connector_index
                        ].tube.outer_diameter
                        * 2,
                        height=self._config.wheel.bearing.depth
                        + self._config.wheel.lateral_tolerance,
                        mode=Mode.INTERSECT,
                    )
                with BuildSketch(
                    Plane.XY.offset(self._config.filament_funnel_height)
                ):
                    Circle(
                        radius=self._config.connectors[
                            connector_index
                        ].tube.inner_radius
                    )
                loft()
            with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
                Cylinder(
                    radius=self._config.connectors[
                        connector_index
                    ].tube.outer_radius,
                    height=self._config.bracket_height
                    - self._config.filament_funnel_height
                    - self._config.connectors[connector_index].length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
                Cylinder(
                    radius=self._config.connectors[connector_index].radius,
                    height=self._config.connectors[connector_index].length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildSketch(
                Plane.XY.offset(
                    self._config.bracket_height
                    - self._config.minimum_thickness / 2
                )
            ):
                Circle(radius=self._config.connectors[connector_index].radius)
            with BuildSketch(Plane.XY.offset(self._config.bracket_height)):
                Circle(
                    radius=self._config.connectors[connector_index].radius
                    + self._config.minimum_thickness / 2
                )
            loft()

        with BuildPart(
            Location((0, 0, self._config.bracket_depth / 2), (-90, 0, 0))
        ) as cut:
            add(tube)
        part = cut.part
        part.label = "tube cut"
        return part

    def straight_filament_path_solid(self) -> Part:
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

    def straight_filament_path(self, draft=True, connector_index=0) -> Part:
        """
        builds a straight filaement channel with the cut in place
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        with BuildPart() as path:
            add(self.straight_filament_path_solid())
            with BuildPart(mode=Mode.SUBTRACT):
                add(
                    self.straight_filament_path_cut(
                        connector_index=connector_index
                    )
                )
            if not draft and self._config.connectors[connector_index].threaded:
                add(
                    self.straight_filament_connector_threads(
                        connector_index=connector_index
                    )
                )
        part = path.part
        part.label = "filament path"
        return part

    def _curved_filament_line(self, connector_index=0) -> Compound:
        """
        returns a compund with three line segments representing the
        channel for the ingress funnel, the PTFE tube,
        and the connector
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        straight_distance = (
            self._config.connectors[connector_index].length / 2
            + self._config.minimum_structural_thickness
        ) / sqrt(2)

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
            output = Line(
                curve @ 1,
                (
                    (curve @ 1).X + straight_distance,
                    (curve @ 1).Y + straight_distance,
                ),
            )
            bridge.label = "input"
            bridge.color = "RED"
            curve.label = "curve"
            curve.color = "BLUE"
            output.label = "output"
            output.color = "GREEN"
        lines = Compound(children=(funnel, bridge, curve, output))
        return lines

    def curved_filament_path_cut(self, connector_index=0) -> Compound:
        """
        returns the shape to be cut out of a curved filament path
        allowing for the PTFE tube and the connector
        arguments:
            - connector_index: the index of the connector in the configuration
        """
        path = self._curved_filament_line()
        with BuildPart() as inlet:
            with BuildLine() as intake:
                add(path.children[0])
            with BuildSketch(
                Plane(origin=intake.line @ 0, z_dir=intake.line % 0)
            ):
                Circle(
                    radius=self._config.connectors[
                        connector_index
                    ].tube.outer_diameter
                    * 0.75
                )
                Rectangle(
                    height=self._config.connectors[
                        connector_index
                    ].tube.outer_diameter
                    * 2,
                    width=self._config.wheel.bearing.depth
                    + self._config.wheel.lateral_tolerance,
                    mode=Mode.INTERSECT,
                )
            with BuildSketch(
                Plane(origin=intake.line @ 1, z_dir=intake.line % 1)
            ):
                Circle(
                    self._config.connectors[connector_index].tube.inner_radius
                )
            loft()
            extrude(
                inlet.faces().sort_by(Axis.Y)[0], self._config.bracket_depth
            )
        with BuildPart() as tube:
            with BuildLine() as tube_path:
                add(path.children[1])
            with BuildSketch(
                Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
            ):
                Circle(
                    self._config.connectors[connector_index].tube.outer_radius
                )
            sweep()
        with BuildPart() as tube_curve:
            with BuildLine() as tube_path:
                add(path.children[2])
            with BuildSketch(
                Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
            ):
                Circle(
                    self._config.connectors[connector_index].tube.outer_radius
                )
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
                Circle(self._config.connectors[connector_index].radius)
            sweep()
        with BuildPart() as connector_chamfer:
            with BuildSketch(
                Plane(
                    origin=connector_path.line @ 1,
                    z_dir=connector_path.line % 1,
                )
            ):
                Circle(
                    self._config.connectors[connector_index].radius
                    + self._config.minimum_thickness / 2
                )
            with BuildSketch(
                Plane(
                    origin=connector_path.line @ 1,
                    z_dir=connector_path.line % 1,
                ).offset(-self._config.minimum_thickness / 2)
            ):
                Circle(self._config.connectors[connector_index].radius)
            loft()
            extrude(
                connector_chamfer.faces().sort_by(Axis.X)[-1],
                self._config.bracket_depth,
            )
        complete = Compound(
            label="curved filament path cut",
            children=(
                inlet.part,
                tube.part,
                tube_curve.part,
                connector.part,
                connector_chamfer.part,
            ),
        ).move(Location((0, 0, self._config.bracket_depth / 2)))
        return complete

    def curved_filament_path_solid(self, top_exit_fillet=True) -> Part:
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

    def curved_filament_path(
        self, top_exit_fillet=False, draft=True, connector_index=0
    ) -> Part:
        """
        builds a straight filaement channel with the cut in place
        -------
        arguments:
            - top_exit_fillet: set to false to render a clean intersection with
                box immediately to the left of the exit
            - connector_index: the index of the connector in the configuration
        """
        with BuildPart() as path:
            add(self.curved_filament_path_solid(top_exit_fillet))
            with BuildPart(mode=Mode.SUBTRACT):
                add(self.curved_filament_path_cut())
            if not draft and self._config.connectors[connector_index].threaded:
                add(
                    self.curved_filament_connector_threads(
                        connector_index=connector_index
                    )
                )
        part = path.part
        part.label = "filament path"
        return part

    def load_config(self, configuration_path: str):
        """
        loads the configuration file
        -------
        arguments:
            - configuration_path: the path to the configuration file
        """
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file: str = None):
        """
        initializes the Partomatic filament channels
        -------
        arguments:
            - configuration_file: the path to the configuration file,
                    set to None to use the default configuration
        """
        super(Partomatic, self).__init__()
        if configuration_file is not None:
            self.load_config(configuration_file)

    def compile(self):
        """
        Builds the relevant parts for the filament channels
        """
        self._straightfilamentpath = self.straight_filament_path(
            draft=False
        ).move(Location((-self._config.wheel.radius, 0, 0)))
        self._curvedfilamentpath = self.curved_filament_path(
            top_exit_fillet=True, draft=False
        ).move(Location((self._config.wheel.radius, 0, 0)))

    def display(self):
        """
        Shows the filament channels in OCP CAD Viewer
        """
        show(
            self._curvedfilamentpath,
            self._straightfilamentpath,
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        """
        Required for partomatic, although there are no
        STLs to export for the filament channels
        """
        pass

    def render_2d(self):
        """
        not yet implemented
        """
        pass


if __name__ == "__main__":
    channels = FilamentChannels(
        Path(__file__).parent / "../build-configs/debug.conf"
    )
    channels.compile()
    channels.display()
