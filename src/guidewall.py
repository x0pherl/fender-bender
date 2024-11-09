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
    export_stl,
    fillet,
    loft,
)
from build123d.build_common import PolarLocations
from build123d.objects_part import Cylinder
from ocp_vscode import Camera, show
from bender_config import BenderConfig
from hexwall import HexWall
from partomatic import Partomatic
from guidewall_config import GuidewallConfig
from tongue_groove import tongue


class Guidewall(Partomatic):
    """partomatic for the frand and back chamber walls of the filament bank"""

    wall: Part
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
                    self._config.core_length,
                    self._config.wall_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                Rectangle(
                    self._config.wall_thickness * 3,
                    self._config.core_length,
                )
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness * 3)):
                Rectangle(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    self._config.core_length,
                )
            loft()
            with BuildPart(
                Plane.XY.offset(self._config.wall_thickness),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    self._config.core_length,
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

    def _guide_side(self) -> Part:
        """
        defines the outer sides of the sidewall with appropriate structural
        reinforcements
        """
        with BuildPart() as side:
            Box(
                self._config.reinforcement_thickness - self._config.tolerance,
                self._config.core_length,
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
            if not self._config.solid_wall:
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
            add(self._guide_set())
            add(self._tongues())
        return wall.part

    def load_config(self, configuration: str, yaml_tree="guidewall"):
        """
        loads a sidewall configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the wheel configuration node,
            separated by slashes (example: "BenderConfig/Sidewall")
        """
        self._config.load_config(configuration, yaml_tree)

    def __init__(self, config: GuidewallConfig = None):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - config: a GuidewallConfig ojbect
        """
        super(Partomatic, self).__init__()

        if config:
            self.load_config({"guidewall": asdict(config)})
        else:
            self._config = GuidewallConfig()

    def compile(self):
        self.wall = self.build_guidewall()

    def export_stls(self):
        """
        Generates the wall STLs in the configured
        folder
        """
        if self._config.stl_folder.upper() == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.wall, str(output_directory / "wall-guide.stl"))

    def display(self):
        show(self.wall, reset_camera=Camera.KEEP)

    def render_2d(self):
        pass


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"

    gw = Guidewall(BenderConfig(config_path).guidewall_config)
    gw.compile()
    gw.display()
    gw.export_stls()
