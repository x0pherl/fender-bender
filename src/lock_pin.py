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
from lock_pin_config import LockPinConfig
from partomatic import AutomatablePart, Partomatic


class LockPin(Partomatic):
    """a partomatic of the lock pin"""

    _config = LockPinConfig()

    def lock_pin(self, inset: float = 0.3, tie_loop=False):
        """
        The pin shape for locking in the filament brackets if LockStyle.PIN is used
        -------
        arguments:
            - inset: an inset amount allowing tolerance in the printed parts
            - tie_loop: whether to include a handle/loop
                for tying the lock pin in place
        """
        rail_height = self._config.height - inset
        lateral_tolerance = inset
        if lateral_tolerance > 0:
            lateral_tolerance *= 2
        with BuildPart() as lpin:
            with BuildPart() as lower:
                Box(
                    self._config.height - lateral_tolerance,
                    self._config.pin_length,
                    rail_height / 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                chamfer(
                    lower.faces()
                    .sort_by(Axis.Z)[-1]
                    .edges()
                    .filter_by(Axis.Y),
                    length=rail_height / 2 - abs(inset / 2),
                    length2=self._config.height / 4,
                )
            with BuildPart(Plane.XY.offset(rail_height / 2)) as upper:
                Box(
                    self._config.height - lateral_tolerance,
                    self._config.pin_length,
                    rail_height / 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                chamfer(
                    upper.faces().sort_by(Axis.Z)[0].edges().filter_by(Axis.Y),
                    length=rail_height / 2 - abs(inset / 2),
                    length2=self._config.height / 4,
                )
            if tie_loop:
                with BuildPart(
                    Location((0, self._config.pin_length / 2, 0))
                ) as outer_loop:
                    Box(
                        self._config.height * 2,
                        self._config.height * 2,
                        rail_height,
                        align=(Align.CENTER, Align.MIN, Align.MIN),
                    )
                    fillet(
                        outer_loop.faces()
                        .sort_by(Axis.Y)[-1]
                        .edges()
                        .filter_by(Axis.Z),
                        self._config.height - (abs(inset)),
                    )
                with BuildPart(
                    Location(
                        (
                            0,
                            self._config.pin_length / 2 + self._config.height,
                            0,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    Cylinder(
                        radius=self._config.height - self._config.height / 4,
                        height=rail_height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
        part = lpin.part
        part.label = "lockpin"
        return part

    def compile(self):
        self.parts.clear()
        self.parts.append(
            AutomatablePart(
                self.lock_pin(
                    inset=self._config.tolerance / 2,
                    tie_loop=self._config.tie_loop,
                ),
                "lock-pin",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/debug.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
    bender_config = BenderConfig(str(config_path))

    pin = LockPin(bender_config.lock_pin_config)
    pin.compile()
    pin.display()
    pin.export_stls()
