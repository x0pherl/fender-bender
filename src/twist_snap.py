"""

Twist & Snap Connector

name: twist_snap.py
by:   x0pherl
date: May 19 2024

desc: A parameterized twist and snap fitting.

license:

license:

    Copyright 2024 x0pherl

    Use of this source code is governed by an MIT-style
    license that can be found in the LICENSE file or at
    https://opensource.org/licenses/MIT.

"""

from dataclasses import dataclass
from enum import Enum, Flag, auto
from math import radians, cos, sin

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    GeomType,
    Location,
    Locations,
    Mode,
    PolarLocations,
    Polygon,
    SortBy,
    add,
    fillet,
    sweep,
)

from ocp_vscode import Camera, show

from partomatic import AutomatablePart, Partomatic, PartomaticConfig


class TwistSnapSection(Flag):
    SOCKET = auto()
    CONNECTOR = auto()
    COMPLETE = SOCKET | CONNECTOR


class TwistSnapEndFinish(Enum):
    RAW = auto()
    SQUARE = auto()
    FADE = auto()
    CHAMFER = auto()


@dataclass
class TwistSnapConfig(PartomaticConfig):
    connector_diameter: float = 4.5
    wall_size: float = 2
    tolerance: float = 0.12
    end_finish: TwistSnapEndFinish = TwistSnapEndFinish.RAW
    section: TwistSnapSection = TwistSnapSection.CONNECTOR
    arc_percentage: float = 10
    snapfit_count: int = 4
    snapfit_radius_extension: float = wall_size * 2 / 3
    wall_width: float = wall_size
    wall_depth: float = wall_size
    grip_diameter: float = connector_diameter + wall_size * 2
    snapfit_height: float = wall_size

    def __init__(self, configuration: any = None, **kwargs):
        super().__init__(configuration, **kwargs)


class TwistSnapConnector(Partomatic):
    """TwistSnap Connector

    Partomatic TwistSnap connectors and sockets that twist together and lock
    """

    _config: TwistSnapConfig = TwistSnapConfig()

    def twist_snap_connector(self) -> Compound:
        """
        Builds a Part for the defined twist snap connector
        """
        with BuildPart() as twistbase:
            Cylinder(
                radius=self._config.connector_diameter,
                height=self._config.wall_depth * 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            path = (
                twistbase.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS)[-1]
            )  # top edge of cylinder
            path = path.trim(
                self._config.arc_percentage / -200,
                self._config.arc_percentage / 200,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (self._config.snapfit_radius_extension, 0),
                            (
                                self._config.snapfit_radius_extension,
                                self._config.snapfit_height,
                            ),
                            (0, self._config.snapfit_height / 2),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                with Locations(
                    snapfit.part.center()
                    + (0, self._config.snapfit_radius_extension / 2, 0)
                ):
                    Cylinder(
                        radius=self._config.snapfit_radius_extension / 2,
                        height=self._config.snapfit_height * 3,
                        mode=Mode.SUBTRACT,
                    )
                fillet(
                    snapfit.faces()
                    .sort_by(Axis.Y)[-2:]
                    .edges()
                    .filter_by(Axis.Z),
                    min(
                        self._config.snapfit_radius_extension / 8,
                        snapfit.part.max_fillet(
                            snapfit.faces()
                            .sort_by(Axis.Y)[-2:]
                            .edges()
                            .filter_by(Axis.Z),
                            max_iterations=40,
                        ),
                    ),
                )

            with PolarLocations(0, self._config.snapfit_count):
                add(snapfit.part)
        return twistbase.part.rotate(Axis.X, 180).move(Location((0, 0, 4)))

    def twist_snap_socket(self) -> Compound:
        """
        Returns a Part for the defined twist snap socket
        """
        with BuildPart() as socket_fitting:
            Cylinder(
                radius=self._config.connector_diameter
                + self._config.wall_width * 4 / 3,
                height=self._config.wall_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                socket_fitting.faces().sort_by(Axis.Z)[-1]
            ) as snap_socket:
                Cylinder(
                    radius=self._config.connector_diameter
                    + self._config.wall_width * 4 / 3,
                    height=self._config.wall_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Cylinder(
                    radius=self._config.connector_diameter
                    + self._config.tolerance,
                    height=self._config.wall_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
            trace_path = (
                snap_socket.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS, reverse=True)[-1]
            )  # top edge of cylinder
            path = trace_path.trim(
                (self._config.arc_percentage / -200) * 1.1,
                (self._config.arc_percentage / 200) * 1.1,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (self._config.snapfit_radius_extension, 0),
                            (
                                self._config.snapfit_radius_extension,
                                self._config.snapfit_height * 2,
                            ),
                            (0, self._config.snapfit_height * 2),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces()
                    .sort_by(Axis.Y)[-1]
                    .edges()
                    .filter_by(Axis.Z),
                    self._config.snapfit_radius_extension / 8,
                )
            with PolarLocations(0, self._config.snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)

            path = trace_path.trim(
                (self._config.arc_percentage / -200) * 3.3,
                (self._config.arc_percentage / 200) * 1.1,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (
                                self._config.snapfit_radius_extension
                                + self._config.tolerance,
                                0,
                            ),
                            (
                                self._config.snapfit_radius_extension
                                + self._config.tolerance,
                                self._config.snapfit_height
                                + self._config.tolerance,
                            ),
                            (
                                0,
                                self._config.snapfit_height / 2
                                + self._config.tolerance,
                            ),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces()
                    .sort_by(Axis.Y)[-1]
                    .edges()
                    .filter_by(Axis.Z),
                    self._config.snapfit_radius_extension / 8,
                )
            with PolarLocations(0, self._config.snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)
            with PolarLocations(
                self._config.connector_diameter
                + self._config.snapfit_radius_extension
                + self._config.tolerance * 2,
                self._config.snapfit_count,
                start_angle=self._config.arc_percentage * -4,
            ):
                Cylinder(
                    radius=self._config.snapfit_radius_extension / 2
                    - self._config.tolerance,
                    height=self._config.snapfit_height * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        return socket_fitting.part

    def compile(self):
        self.parts.clear()
        if TwistSnapSection.SOCKET in self._config.section:
            self.parts.append(
                AutomatablePart(
                    self.twist_snap_socket(),
                    "socket",
                    stl_folder=self._config.stl_folder,
                )
            )
        if TwistSnapSection.CONNECTOR in self._config.section:
            self.parts.append(
                AutomatablePart(
                    self.twist_snap_connector(),
                    "connector",
                    stl_folder=self._config.stl_folder,
                )
            )


if __name__ == "__main__":
    connector = TwistSnapConnector(
        TwistSnapConfig(
            connector_diameter=4.5,
            wall_size=2,
            tolerance=0.12,
            section=TwistSnapSection.CONNECTOR,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
    )

    connector.compile()
    connector.display()
    # from build123d import export_stl

    # export_stl(connector.parts[0].part, "test.stl")
