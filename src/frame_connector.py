from dataclasses import asdict, dataclass
from pathlib import Path
from build123d import (
    BuildPart,
    Align,
    Axis,
    add,
    extrude,
    Location,
    Locations,
    Mode,
    GridLocations,
    fillet,
    export_stl,
    Box,
    scale,
    BuildSketch,
    RegularPolygon,
    Part,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from frame_common import chamber_cuts
from partomatic import AutomatablePart, Partomatic
from tongue_groove import groove_pair
from frame_config import FrameConfig, FrameStyle


class ConnectorFrame(Partomatic):
    _config: FrameConfig = FrameConfig()

    def _frame_flat_sidewall_cut(self) -> Part:
        """
        a flat cut for the sidewall
        """
        length = self._config.interior_length + self._config.wall_thickness * 2
        with BuildPart() as cut:
            with BuildSketch():
                RegularPolygon(self._config.wall_thickness / 4, 4)
            extrude(amount=length)
            scale(by=(2, 1, 1))
        return cut.part.move(Location((0, 0, -length / 2))).rotate(Axis.Y, 90)

    def connector_frame(self) -> Part:
        """
        the connecting frame for supporting the walls of the top and extension
        sections
        """
        standing = FrameStyle.STANDING in self._config.frame_style
        extra_length = 0 if standing else self._config.interior_offset
        with BuildPart() as cframe:
            with BuildPart():
                Box(
                    self._config.exterior_length + extra_length * 2,
                    self._config.exterior_width,
                    self._config.depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            fillet(cframe.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((extra_length, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                with Locations(
                    cframe.faces().sort_by(Axis.Z)[-1],
                    cframe.faces().sort_by(Axis.Z)[0],
                ):
                    add(
                        groove_pair(
                            self._config.groove_distance,
                            self._config.wall_thickness,
                            self._config.interior_width,
                            self._config.groove_depth,
                            self._config.tolerance,
                            self._config.click_fit_distance,
                            self._config.click_fit_radius,
                        )
                    )
                    with GridLocations(
                        0,
                        self._config.bracket_spacing,
                        1,
                        self._config.filament_count + 1,
                    ):
                        add(self._frame_flat_sidewall_cut())
                add(
                    chamber_cuts(
                        count=self._config.filament_count,
                        spacing=self._config.bracket_spacing,
                        length=self._config.interior_length,
                        width=self._config.bracket_spacing
                        - self._config.wall_thickness,
                        depth=self._config.depth,
                        fillet_radius=self._config.fillet_radius,
                    )
                )
        return cframe.part

    def compile(self):
        self.parts.clear()
        self.parts.append(
            AutomatablePart(
                self.connector_frame(),
                "frame-connector",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/debug.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
    bender_config = BenderConfig(config_path)
    frame = ConnectorFrame(bender_config.frame_config)
    frame.compile()
    frame.display()
    frame.export_stls()
