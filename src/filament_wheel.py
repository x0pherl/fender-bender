"""
Generates the part for the filament wheel of our filament bank design
"""

from dataclasses import asdict
from pathlib import Path

from build123d import (
    Align,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    Cylinder,
    Line,
    Location,
    Mode,
    Part,
    PolarLocations,
    Sketch,
    add,
    export_stl,
    extrude,
    make_face,
)

from ocp_vscode import Camera, show

from bender_config import BenderConfig
from filament_wheel_config import WheelConfig
from partomatic import Partomatic, AutomatablePart
from basic_shapes import diamond_torus
from bearing import print_in_place_bearing


class FilamentWheel(Partomatic):
    """A partomatic for the filament wheel of the filament bank"""

    _config = WheelConfig()

    def _spoke(self) -> Sketch:
        """
        returns the spoke Sketch for the filament wheel
        """
        spoke_outer_radius = (
            self._config.radius
            + self._config.bearing.radius
            + self._config.bearing.depth
        ) / 2
        spoke_shift = (
            self._config.radius
            - self._config.bearing.radius
            - self._config.bearing.depth
        ) / 2
        with BuildSketch() as sketch:
            with BuildLine():
                l1 = CenterArc(
                    center=((spoke_shift, 0)),
                    radius=spoke_outer_radius,
                    start_angle=0,
                    arc_size=180,
                )
                l2 = CenterArc(
                    center=((spoke_shift, 0)),
                    radius=spoke_outer_radius - self._config.bearing.depth,
                    start_angle=0,
                    arc_size=180,
                )
                Line(l1 @ 0, l2 @ 0)
                Line(l1 @ 1, l2 @ 1)
            make_face()
        return sketch.sketch

    def filament_wheel(self) -> Part:
        """
        the wheel for passing the filament through the bracket
        """
        with BuildPart() as fwheel:
            with BuildSketch():
                Circle(radius=self._config.radius)
                Circle(
                    radius=self._config.radius - self._config.bearing.depth,
                    mode=Mode.SUBTRACT,
                )
            with BuildSketch():
                Circle(
                    radius=self._config.bearing.radius
                    + self._config.bearing.depth
                )
                Circle(
                    radius=self._config.bearing.radius,
                    mode=Mode.SUBTRACT,
                )
            with PolarLocations(0, self._config.spoke_count):
                add(self._spoke())
            extrude(amount=self._config.bearing.depth)
            add(
                diamond_torus(
                    self._config.radius,
                    self._config.bearing.depth / 2,
                ).move(Location((0, 0, self._config.bearing.depth / 2))),
                mode=Mode.SUBTRACT,
            )
            if self._config.bearing.print_in_place:
                Cylinder(
                    self._config.bearing.diameter,
                    self._config.depth,
                    mode=Mode.SUBTRACT,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                add(
                    print_in_place_bearing(
                        outer_radius=self._config.bearing.diameter,
                        inner_radius=self._config.bearing.inner_radius,
                        height=self._config.depth,
                    )
                )
        part = fwheel.part
        part.label = "filament wheel"
        return part

    def compile(self):
        """
        Builds the relevant parts for the filament wheel
        """
        self.parts.clear()
        self.parts.append(
            AutomatablePart(
                self.filament_wheel(),
                "filament-bracket-wheel",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/debug.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
    bender_config = BenderConfig(config_path)
    wheel_conf = bender_config.wheel
    wheel = FilamentWheel(wheel_conf, stl_folder=bender_config.stl_folder)
    wheel.compile()
    wheel.display()
    wheel.export_stls()
