"""a part for locking the filament brackets into the frame"""

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    Location,
    Mode,
    Part,
    Plane,
    chamfer,
    export_stl,
    fillet,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from partomatic import Partomatic


class LockPin(Partomatic):
    """a partomatic of the lock pin"""

    _config = BenderConfig()
    _lockpin: Part

    def lock_pin(
        self, inset=_config.frame_lock_pin_tolerance / 2, tie_loop=False
    ):
        """
        The pin shape for locking in the filament brackets if LockStyle.PIN is used
        -------
        arguments:
            - inset: an inset amount allowing tolerance in the printed parts
            - tie_loop: whether to include a handle/loop
                for tying the lock pin in place
        """
        rail_height = self._config.minimum_structural_thickness - inset
        lateral_tolerance = inset
        if lateral_tolerance > 0:
            lateral_tolerance *= 2
        with BuildPart() as lpin:
            with BuildPart() as lower:
                Box(
                    self._config.minimum_structural_thickness
                    - lateral_tolerance,
                    self._config.frame_exterior_width,
                    rail_height / 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                chamfer(
                    lower.faces()
                    .sort_by(Axis.Z)[-1]
                    .edges()
                    .filter_by(Axis.Y),
                    length=rail_height / 2 - abs(inset / 2),
                    length2=self._config.minimum_thickness,
                )
            with BuildPart(Plane.XY.offset(rail_height / 2)) as upper:
                Box(
                    self._config.minimum_structural_thickness
                    - lateral_tolerance,
                    self._config.frame_exterior_width,
                    rail_height / 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                chamfer(
                    upper.faces().sort_by(Axis.Z)[0].edges().filter_by(Axis.Y),
                    length=rail_height / 2 - abs(inset / 2),
                    length2=self._config.minimum_thickness,
                )
            if tie_loop:
                with BuildPart(
                    Location((0, self._config.frame_exterior_width / 2, 0))
                ) as outer_loop:
                    Box(
                        self._config.minimum_structural_thickness * 2,
                        self._config.minimum_structural_thickness * 2,
                        rail_height,
                        align=(Align.CENTER, Align.MIN, Align.MIN),
                    )
                    fillet(
                        outer_loop.faces()
                        .sort_by(Axis.Y)[-1]
                        .edges()
                        .filter_by(Axis.Z),
                        self._config.minimum_structural_thickness
                        - (abs(inset)),
                    )
                with BuildPart(
                    Location(
                        (
                            0,
                            self._config.frame_exterior_width / 2
                            + self._config.minimum_structural_thickness,
                            0,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    Cylinder(
                        radius=self._config.minimum_structural_thickness
                        - self._config.minimum_thickness,
                        height=rail_height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
        return lpin.part

    def load_config(self, configuration_path: str):
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file: str = None):
        super(Partomatic, self).__init__()
        if configuration_file is not None:
            self.load_config(configuration_file)

    def compile(self):
        self._lockpin = self.lock_pin(
            inset=self._config.frame_lock_pin_tolerance / 2, tie_loop=True
        )
        self._lockpin.label = "filament wheel"

    def display(self):
        show(self._lockpin, reset_camera=Camera.KEEP)

    def export_stls(self):
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self._lockpin, str(output_directory / "lock-pin.stl"))

    def render_2d(self):
        pass


if __name__ == "__main__":
    pin = LockPin(Path(__file__).parent / "../build-configs/debug.conf")
    pin.compile()
    pin.display()
    pin.export_stls()
