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
    Cylinder,
    BuildSketch,
    RegularPolygon,
    Part,
    Sphere,
    PolarLocations,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from frame_common import chamber_cuts
from partomatic import Partomatic
from tongue_groove import groove_pair
from frame_config import ConnectorFrameConfig


class ConnectorFrame(Partomatic):
    _config: ConnectorFrameConfig = ConnectorFrameConfig()
    _standing_frame: Part
    _hanging_frame: Part

    # def _chamber_cut(self) -> Part:
    #     """
    #     a filleted box for each chamber in the lower connectors
    #     -------
    #     arguments:
    #         - height: the height of the chamber cut
    #     """
    #     with BuildPart() as cut:
    #         Box(
    #             self._config.interior_length,
    #             self._config.bracket_spacing - self._config.wall_thickness,
    #             self._config.depth,
    #             align=(Align.CENTER, Align.CENTER, Align.MIN),
    #         )
    #         fillet(
    #             cut.edges().filter_by(Axis.Z),
    #             radius=self._config.fillet_radius,
    #         )
    #     return cut.part

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

    def connector_frame(self, standing=True) -> Part:
        """
        the connecting frame for supporting the walls of the top and extension
        sections
        """
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
                            self._config.interior_width
                            - self._config.bracket_spacing,
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
        self._standing_frame = self.connector_frame()
        self._hanging_frame = self.connector_frame(standing=False)

    def display(self):
        show(
            self._hanging_frame,
            self._standing_frame.move(
                Location(
                    (
                        self._config.interior_offset,
                        self._config.exterior_width,
                        0,
                    )
                )
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        Path(output_directory / "alt").mkdir(parents=True, exist_ok=True)

        export_stl(
            self._hanging_frame,
            str(Path(output_directory / "frame-connector.stl")),
        )

        export_stl(
            self._standing_frame,
            str(Path(output_directory / "alt/frame-connector-standing.stl")),
        )

    def render_2d(self):
        pass

    def load_config(self, configuration: str, yaml_tree="connector-frame"):
        """
        loads a sidewall configuration from a file or valid yaml
        -------
        arguments:
            - configuration: the path to the configuration file
                OR
              a valid yaml configuration string
            - yaml_tree: the yaml tree to the wheel configuration node,
            separated by slashes (example: "BenderConfig/ConnectorFrame")
        """
        self._config.load_config(configuration, yaml_tree)

    def __init__(self, config: ConnectorFrameConfig = None):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - config: a GuidewallConfig ojbect
        """
        super(Partomatic, self).__init__()

        if config:
            self.load_config({"connector-frame": asdict(config)})
        else:
            self._config = ConnectorFrameConfig()


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    frame = ConnectorFrame(bender_config.connector_frame_config)
    frame.compile()
    frame.display()
    frame.export_stls()
