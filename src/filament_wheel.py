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
from partomatic import Partomatic
from basic_shapes import diamond_torus
from bearing import print_in_place_bearing


class FilamentWheel(Partomatic):
    """A partomatic for the filament wheel of the filament bank"""

    _config = WheelConfig()
    stl_folder: str = "../stl/default"
    wheel: Part
    print_in_place_wheel: Part

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

    def filament_wheel(self, print_in_place=False) -> Part:
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
            if print_in_place:
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
        return fwheel.part

    def load_config(self, configuration: str, yaml_tree="wheel"):
        """
        loads a wheel configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the wheel configuration node,
            separated by slashes (example: "BenderConfig/wheel")
        """
        self._config.load_config(configuration, yaml_tree)

    def __init__(
        self, config: WheelConfig = None, stl_folder: str = "../stl/default"
    ):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - kwargs: specific configuration values to override as key value pairs
        """
        super(Partomatic, self).__init__()
        self.stl_folder = stl_folder
        if config:
            self.load_config({"wheel": asdict(config)})
        else:
            self._config = WheelConfig()

    def compile(self):
        """
        Builds the relevant parts for the filament wheel
        """
        self.wheel = self.filament_wheel()
        self.print_in_place_wheel = self.filament_wheel(print_in_place=True)
        self.wheel.label = "filament wheel"
        self.print_in_place_wheel.label = "print-in-place filament wheel"

    def display(self):
        """
        Shows the filament wheel in OCP CAD Viewer
        """
        show(
            self.wheel,
            self.print_in_place_wheel.move(
                Location(
                    (self._config.diameter + self._config.depth / 2, 0, 0)
                )
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        """
        Generates the filament wheel STLs in the configured
        folder
        """
        if self.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(
            self.wheel, str(output_directory / "filament-bracket-wheel.stl")
        )
        export_stl(
            self.print_in_place_wheel,
            str(
                output_directory
                / "alt/filament-bracket-wheel-print-in-place.stl"
            ),
        )

    def render_2d(self):
        """
        not yet implemented
        """
        pass


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    wheel_conf = bender_config.wheel
    wheel = FilamentWheel(wheel_conf, bender_config.stl_folder)
    wheel.compile()
    wheel.display()
    wheel.export_stls()
