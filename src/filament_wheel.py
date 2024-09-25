"""
Generates the part for the filament wheel of our filament bank design
"""

from pathlib import Path

from build123d import (
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    JernArc,
    Line,
    Location,
    Mode,
    Part,
    PolarLocations,
    RegularPolygon,
    Sketch,
    add,
    export_stl,
    extrude,
    make_face,
    sweep,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from partomatic import Partomatic


def diamond_torus(major_radius: float, minor_radius: float) -> Part:
    """
    sweeps a regular diamond along a circle defined by major_radius
    -------
    arguments:
        - major_radius: the radius of the circle to sweep the diamond along
        - minor_radius: the radius of the diamond
    """
    with BuildPart() as torus:
        with BuildLine():
            l1 = JernArc(
                start=(major_radius, 0),
                tangent=(0, 1),
                radius=major_radius,
                arc_size=360,
            )
        with BuildSketch(l1 ^ 0):
            RegularPolygon(radius=minor_radius, side_count=4)
        sweep()
    return torus.part


class FilamentWheel(Partomatic):
    """A partomatic for the filament wheel of the filament bank"""

    _config = BenderConfig()
    wheel: Part

    def _spoke(self) -> Sketch:
        """
        returns the spoke Sketch for the filament wheel
        """
        spoke_outer_radius = (
            self._config.wheel.radius
            + self._config.wheel.bearing.radius
            + self._config.wheel.bearing.depth
        ) / 2
        spoke_shift = (
            self._config.wheel.radius
            - self._config.wheel.bearing.radius
            - self._config.wheel.bearing.depth
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
                    radius=spoke_outer_radius
                    - self._config.wheel.bearing.depth,
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
                Circle(radius=self._config.wheel.radius)
                Circle(
                    radius=self._config.wheel.radius
                    - self._config.wheel.bearing.depth,
                    mode=Mode.SUBTRACT,
                )
            with BuildSketch():
                Circle(
                    radius=self._config.wheel.bearing.radius
                    + self._config.wheel.bearing.depth
                )
                Circle(
                    radius=self._config.wheel.bearing.radius,
                    mode=Mode.SUBTRACT,
                )
            with PolarLocations(0, self._config.wheel.spoke_count):
                add(self._spoke())
            extrude(amount=self._config.wheel.bearing.depth)
            add(
                diamond_torus(
                    self._config.wheel.radius,
                    self._config.wheel.bearing.depth / 2,
                ).move(Location((0, 0, self._config.wheel.bearing.depth / 2))),
                mode=Mode.SUBTRACT,
            )
        return fwheel.part

    def load_config(self, configuration_path: str):
        """
        loads the configuration file
         -------
        arguments:
            - configuration_path: the path to the configuration file
        """
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file: str):
        """
        initializes the Partomatic filament wheel
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
        Builds the relevant parts for the filament wheel
        """
        self.wheel = self.filament_wheel()
        self.wheel.label = "filament wheel"

    def display(self):
        """
        Shows the filament wheel in OCP CAD Viewer
        """
        show(self.wheel, reset_camera=Camera.KEEP)

    def export_stls(self):
        """
        Generates the filament wheel STLs in the configured
        folder
        """
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(
            self.wheel, str(output_directory / "filament-bracket-wheel.stl")
        )

    def render_2d(self):
        """
        not yet implemented
        """
        pass


if __name__ == "__main__":
    wheel = FilamentWheel(
        Path(__file__).parent / "../build-configs/debug.conf"
    )
    wheel.compile()
    wheel.display()
    wheel.export_stls()
