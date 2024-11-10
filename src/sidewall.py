"""
Generates the part for the side chamber walls of the filament bank
"""

from dataclasses import asdict
from pathlib import Path

from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    Sketch,
    Sphere,
    add,
    export_stl,
    extrude,
    loft,
)
from ocp_vscode import Camera, show, save_screenshot

from bender_config import BenderConfig
from hexwall import HexWall
from partomatic import Partomatic
from sidewall_config import SidewallConfig


class Sidewall(Partomatic):
    """partomatic for the chamber walls of the filament bank"""

    _config = SidewallConfig()

    sidewall: Part
    solidsidewall: Part
    solidreinforcedsidewall: Part
    reinforcedsidewall: Part
    dryreinforcedsidewall: Part

    def _base_sidewall_shape(
        self,
        top_radius: float = 70,
        extension_length: float = 20,
        width: float = 170,
        straight_length: float = 170,
        end_count=1,
    ) -> Sketch:
        with BuildSketch(mode=Mode.PRIVATE) as top:
            Circle(top_radius)
            Rectangle(
                top_radius * 2,
                top_radius,
                align=(Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )
            Rectangle(
                top_radius * 2,
                extension_length,
                align=(Align.CENTER, Align.MAX),
            )
        with BuildSketch(Location((0, 0))) as sw:
            Rectangle(
                width,
                straight_length,
                align=(Align.CENTER, Align.MAX),
            )
            if end_count > 0:
                add(top.sketch.move(Location((0, extension_length, 0))))
            if end_count > 1:
                add(
                    top.sketch.rotate(axis=Axis.Z, angle=180).move(
                        Location((0, -extension_length - straight_length, 0))
                    )
                )
        return sw.sketch

    def _outer_sidewall_shape(self) -> Sketch:
        return self._base_sidewall_shape(
            top_radius=self._config.top_radius
            - self._config.wall_thickness * 0.75,
            extension_length=self._config.top_extension
            + self._config.wall_thickness * 0.75,
            width=self._config.sidewall_width - self._config.wall_thickness,
            straight_length=self._config.straight_length
            - self._config.wall_thickness,
            end_count=self._config.end_count,
        )

    def _center_sidewall_shape(self) -> Sketch:
        return self._base_sidewall_shape(
            top_radius=self._config.top_radius,
            extension_length=self._config.top_extension,
            width=self._config.sidewall_width,
            straight_length=self._config.straight_length
            + self._config.wall_thickness
            / 4,  # note this last bit feels wrong but is v1.0 exact --
            # start here when troubleshooting
            end_count=self._config.end_count,
        ).move(Location((0, self._config.wall_thickness * 0.75)))

    def _central_core_sidewall_shape(self) -> Sketch:
        return self._base_sidewall_shape(
            top_radius=self._config.top_radius
            - self._config.reinforcement_inset
            - self._config.wall_thickness / 2,
            extension_length=self._config.top_extension
            + self._config.reinforcement_inset
            + self._config.wall_thickness / 2,
            width=self._config.sidewall_width
            - self._config.reinforcement_inset * 2
            - self._config.wall_thickness,
            straight_length=self._config.straight_length
            - self._config.reinforcement_inset * 2
            - self._config.wall_thickness,
            end_count=self._config.end_count,
        ).move(
            Location(
                (
                    0,
                    -self._config.reinforcement_inset / 2
                    - self._config.wall_thickness * 0.75,
                )
            )
        )

    def _reinforcer(self) -> Part:
        with BuildPart() as reinforce:
            with BuildSketch():
                add(
                    self._base_sidewall_shape(
                        top_radius=self._config.top_radius
                        - self._config.wall_thickness * 0.75,
                        extension_length=self._config.top_extension
                        + self._config.wall_thickness * 0.75,
                        width=self._config.sidewall_width
                        + self._config.wall_thickness
                        - self._config.reinforcement_thickness * 2,
                        straight_length=self._config.straight_length
                        - self._config.wall_thickness,
                        end_count=self._config.end_count,
                    )
                )
                add(
                    self._base_sidewall_shape(
                        top_radius=self._config.top_radius
                        - self._config.wall_thickness * 0.75
                        - self._config.reinforcement_inset,
                        extension_length=self._config.top_extension
                        + self._config.wall_thickness * 0.75
                        + self._config.reinforcement_inset,
                        width=self._config.sidewall_width
                        + self._config.wall_thickness
                        - self._config.reinforcement_thickness * 2
                        - self._config.reinforcement_inset * 2,
                        straight_length=self._config.straight_length
                        - self._config.wall_thickness
                        - self._config.reinforcement_inset * 2,
                        end_count=self._config.end_count,
                    ).move(Location((0, -self._config.reinforcement_inset))),
                    mode=Mode.SUBTRACT,
                )
            extrude(amount=self._config.reinforcement_thickness)
        return reinforce.part

    def _core_hexwall_cut(self, depth=_config.wall_thickness) -> Part:
        with BuildPart() as hexwall:
            with BuildSketch() as coreshape:
                add(self._central_core_sidewall_shape())
            extrude(coreshape.sketch, amount=self._config.wall_thickness)
            with BuildPart(mode=Mode.INTERSECT):
                hw = HexWall(
                    width=self._config.straight_length * 2,
                    length=self._config.sidewall_width,
                    height=depth,
                    apothem=self._config.wall_window_apothem,
                    wall_thickness=self._config.wall_window_bar_thickness,
                    inverse=True,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                add(hw)
        return hexwall.part

    def _side_wall_divots(self) -> Part:
        """
        positions the holes that get punched along a sidewall to connect to
        the front and back walls
        """
        with BuildPart(
            Location(
                (
                    0,
                    -self._config.straight_length / 2
                    + self._config.wall_thickness
                    * 0.5,  # should go away in v2
                    0,
                )
            )
        ) as divots:
            with BuildPart(
                Location(
                    (
                        0,
                        -self._config.straight_length / 2
                        + self._config.wall_thickness
                        * 0.5,  # should go away in v2
                        self._config.wall_thickness,
                    )
                )
            ):
                with GridLocations(
                    self._config.sidewall_width
                    - self._config.wall_thickness * 2,
                    self._config.straight_length / 2,
                    2,
                    2,
                ):
                    Sphere(radius=self._config.click_fit_radius)
            with GridLocations(
                self._config.sidewall_width - self._config.wall_thickness * 2,
                self._config.straight_length / 2,
                2,
                2,
            ):
                Sphere(radius=self._config.click_fit_radius)
        return divots.part

    def _sidewall(self, reinforced=False, solid=False, dry=False) -> Part:
        """
        creates a sidewall part, optionally reinforced
        -------
        arguments:
            - reinforced: whether to add a thicker structural outline to the wall
            to result in a stiffer part
        """
        with BuildPart() as sw:
            with BuildSketch():
                add(self._outer_sidewall_shape())
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness / 2)):
                add(self._center_sidewall_shape())
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                add(self._outer_sidewall_shape())
            loft(ruled=True)
            with BuildPart(mode=Mode.SUBTRACT):
                add(self._side_wall_divots())
                if not solid:
                    add(self._core_hexwall_cut())
            if dry and not solid:
                with BuildSketch():
                    add(self._central_core_sidewall_shape())
                extrude(amount=self._config.minimum_thickness)
            if reinforced:
                add(self._reinforcer())
        return sw.part

    def load_config(self, configuration: str, yaml_tree="sidewall"):
        """
        loads a sidewall configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the sidewall configuration node,
            separated by slashes (example: "BenderConfig/Sidewall")
        """
        self._config.load_config(configuration, yaml_tree)

    def __init__(self, config: SidewallConfig = None):
        """
        initializes the Partomatic sidewall
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - kwargs: specific configuration values to override as key value pairs
        """
        super(Partomatic, self).__init__()
        if config:
            self.load_config({"sidewall": asdict(config)})
        else:
            self._config = SidewallConfig()

    def compile(self):
        """
        Builds the internal sidewall parts
        """
        self.sidewall = self._sidewall()
        self.reinforcedsidewall = self._sidewall(reinforced=True)
        self.solidsidewall = self._sidewall(solid=True)
        self.solidreinforcedsidewall = self._sidewall(
            reinforced=True, solid=True
        )
        self.dryreinforcedsidewall = self._sidewall(reinforced=True, dry=True)

    def export_stls(self):
        """
        Generates the wall STLs in the configured
        folder
        """
        if self._config.stl_folder.upper() == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.sidewall, str(output_directory / "wall-side.stl"))
        export_stl(
            self.reinforcedsidewall,
            str(output_directory / "wall-side-reinforced.stl"),
        )
        export_stl(
            self.solidsidewall,
            str(output_directory / "alt/wall-side-solid.stl"),
        )
        export_stl(
            self.solidreinforcedsidewall,
            str(output_directory / "wall-side-reinforced-solid.stl"),
        )
        export_stl(
            self.dryreinforcedsidewall,
            str(output_directory / "alt/wall-side-reinforced-dry.stl"),
        )

    def display(self):
        """
        Shows the walls in OCP CAD Viewer
        """
        show(
            self.dryreinforcedsidewall,
            reset_camera=Camera.KEEP,
        )

    def render_2d(self):
        pass


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"

    sw = Sidewall(BenderConfig(config_path).sidewall_config)
    sw.compile()
    sw.display()
    sw.export_stls()
