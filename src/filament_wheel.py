"""
Generates the part for the filament wheel of our filament bank design
"""

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
from pathlib import Path
from partomatic import Partomatic
from bank_config import BankConfig

def diamond_torus(major_radius: float, minor_radius: float) -> Part:
    """
    sweeps a regular diamond along a circle defined by major_radius
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

    _config = BankConfig()
    wheel : Part

    def spoke(self) -> Sketch:
        """
        returns the spoke Sketch for the filament wheel
        """
        spoke_outer_radius = (
            self._config.wheel_radius + self._config.bearing_radius + self._config.rim_thickness
        ) / 2
        spoke_shift = (
            self._config.wheel_radius - self._config.bearing_radius - self._config.rim_thickness
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
                    radius=spoke_outer_radius - self._config.rim_thickness,
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
                Circle(radius=self._config.wheel_radius)
                Circle(
                    radius=self._config.wheel_radius - self._config.rim_thickness,
                    mode=Mode.SUBTRACT,
                )
            with BuildSketch():
                Circle(radius=self._config.bearing_radius + self._config.rim_thickness)
                Circle(radius=self._config.bearing_radius, mode=Mode.SUBTRACT)
            with PolarLocations(0, self._config.wheel_spoke_count):
                add(self.spoke())
            extrude(amount=self._config.bearing_depth)
            add(
                diamond_torus(self._config.wheel_radius, self._config.bearing_depth / 2).move(
                    Location((0, 0, self._config.bearing_depth / 2))
                ),
                mode=Mode.SUBTRACT,
            )
        return fwheel.part

    def load_config(self, configuration_path: str):
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file:str='../build-configs/default.conf'):
        super(Partomatic, self).__init__()
        self.load_config(configuration_file)

    def compile(self):
        self.wheel = self.filament_wheel()
        self.wheel.label = "filament wheel"

    def display(self):
        show(self.wheel, Camera.KEEP)

    def export_stls(self):
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.wheel, str(output_directory / "filament_wheel.stl"))

    def render_2d(self):
        pass

if __name__ == "__main__":
    wheel = FilamentWheel(Path(__file__).parent / "../build-configs/default.conf")
    wheel.compile()
    wheel.display()
    wheel.export_stls()
