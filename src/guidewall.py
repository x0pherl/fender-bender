"""
Generates the part for the front & back chamber walls of the filament bank
"""

from dataclasses import asdict
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    Sphere,
    add,
    chamfer,
    export_stl,
    fillet,
    loft,
)
from build123d.build_common import PolarLocations
from build123d.objects_part import Cylinder
from ocp_vscode import Camera, show
from bender_config import BenderConfig
from hexwall import HexWall
from partomatic import Partomatic, BuildablePart
from guidewall_config import GuidewallConfig
from tongue_groove import tongue
from sidewall_config import WallStyle


class Guidewall(Partomatic):
    """partomatic for the frand and back chamber walls of the filament bank"""

    _config: GuidewallConfig = GuidewallConfig()

    def _wall_channel(self) -> Part:
        """
        creates a channel with tapered sides and
        snap-click points for locking in side walls
        """
        with BuildPart() as channel:
            with BuildPart():
                Box(
                    self._config.wall_thickness * 3,
                    self._config.rail_length,
                    self._config.wall_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                Rectangle(
                    self._config.wall_thickness * 3,
                    self._config.rail_length,
                )
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness * 3)):
                Rectangle(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    self._config.rail_length,
                )
            loft()
            with BuildPart(
                Plane.XY.offset(self._config.wall_thickness),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    self._config.rail_length,
                    self._config.wall_thickness * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(Plane.XY.offset(self._config.wall_thickness * 2)):
                with GridLocations(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    (
                        self._config.core_length
                        + self._config.wall_thickness / 2
                    )
                    / 2,
                    2,
                    2,
                ):
                    Sphere(self._config.click_fit_radius * 0.675)
        part = channel.part
        part.label = "wall channel guide"
        return part

    def _hex_outline_cut(self) -> Part:
        with BuildPart() as cutline:
            outline = HexWall(
                width=self._config.core_length
                - self._config.reinforcement_inset * 2,
                length=self._config.width
                - self._config.reinforcement_inset * 2,
                height=0.20,
                apothem=self._config.wall_window_apothem,
                wall_thickness=self._config.wall_window_bar_thickness,
                inverse=False,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            add(outline)
            with BuildPart(mode=Mode.SUBTRACT):
                cut = HexWall(
                    width=self._config.core_length
                    - self._config.reinforcement_inset * 2,
                    length=self._config.width
                    - self._config.reinforcement_inset * 2,
                    height=0.20,
                    apothem=self._config.wall_window_apothem,
                    wall_thickness=self._config.wall_window_bar_thickness
                    - 0.4,
                    inverse=False,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                add(cut)
        return cutline.part

    def _guide_side(self) -> Part:
        """
        defines the outer sides of the sidewall with appropriate structural
        reinforcements
        """
        with BuildPart() as side:
            Box(
                self._config.reinforcement_thickness - self._config.tolerance,
                self._config.rail_length,
                self._config.wall_thickness * 3,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            fillet(
                (side.faces().sort_by(Axis.X)[-1]).edges().filter_by(Axis.Y),
                self._config.wall_thickness / self._config.fillet_ratio,
            )

        return side.part

    def _guide_set(self) -> Part:
        """
        createst the complete set of guides for the guidewall
        """
        with BuildPart() as guides:
            with GridLocations(
                self._config.section_width,
                0,
                self._config.section_count + 1,
                1,
            ):
                add(self._wall_channel())
            with PolarLocations(
                self._config.width / 2 - self._config.tolerance * 2,
                2,
            ):
                add(self._guide_side())
        return guides.part

    def _tongues(self) -> Part:
        """
        creates the tongues for the front and back walls
        """
        with BuildPart() as tongues:
            with PolarLocations(
                self._config.core_length / 2,
                2,
                start_angle=90,
            ):
                add(
                    tongue(
                        self._config.wall_thickness,
                        self._config.tongue_width,
                        self._config.tongue_depth,
                        0,
                        (self._config.section_count - 1)
                        * self._config.section_width
                        + self._config.tolerance * 2,
                        self._config.click_fit_radius,
                    )
                    .rotate(Axis.Y, 90)
                    .rotate(Axis.X, 180)
                    .move(Location((0, 0, self._config.wall_thickness / 2)))
                )
        return tongues.part

    def build_guidewall(self) -> Part:
        """
        builds the guidewall part
        """
        with BuildPart() as wall:
            Box(
                self._config.width,
                self._config.core_length,
                self._config.wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            if not self._config.wall_style == WallStyle.SOLID:
                with BuildPart(mode=Mode.SUBTRACT):
                    hw = HexWall(
                        width=self._config.core_length
                        - self._config.reinforcement_inset * 2,
                        length=self._config.width
                        - self._config.reinforcement_inset * 2,
                        height=self._config.wall_thickness,
                        apothem=self._config.wall_window_apothem,
                        wall_thickness=self._config.wall_window_bar_thickness,
                        inverse=True,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    add(hw)
            if self._config.wall_style == WallStyle.DRYBOX:
                Box(
                    self._config.width - self._config.reinforcement_inset * 2,
                    self._config.core_length
                    - self._config.reinforcement_inset * 2,
                    self._config.minimum_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            add(self._guide_set())
            if not not self._config.wall_style == WallStyle.SOLID:
                add(self._hex_outline_cut(), mode=Mode.SUBTRACT)
            add(self._tongues())
        return wall.part

    def compile(self):
        self.parts.clear()
        self.parts.append(
            BuildablePart(
                self.build_guidewall(),
                "wall-guide",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"

    gw = Guidewall(BenderConfig(config_path).guidewall_config)
    gw.compile()
    gw.display()
    gw.export_stls()
