from typing import Optional
from build123d import *
from ocp_vscode import show, Camera
from partomatic import Partomatic, PartomaticConfig, BuildablePart
from twist_snap import TwistSnapConnector, TwistSnapConfig, TwistSnapSection


class BackConfig(PartomaticConfig):
    name: str = "connector"
    file_prefix: Optional[str] = None
    file_suffix: Optional[str] = None


class MMUAlternate(Partomatic):
    _config: BackConfig = BackConfig()

    def compile(self):
        connector = TwistSnapConnector(
            TwistSnapConfig(
                connector_diameter=4.5,
                wall_size=2,
                tolerance=0.12,
                section=TwistSnapSection.CONNECTOR,
                snapfit_height=2,
                snapfit_radius_extension=2 * (2 / 3) - 0.06,
                wall_width=2,
                wall_depth=2,
            )
        )
        with BuildPart() as mmu:
            Box(65.2, 10, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildPart(Plane.XY.offset(16)):
                with GridLocations(14, 0, 5, 1):
                    add(connector.twist_snap_connector())

            with GridLocations(14, 0, 5, 1):
                add(
                    Cylinder(
                        radius=2.3,
                        height=20,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    ),
                    mode=Mode.SUBTRACT,
                )

        show(mmu)


if __name__ == "__main__":
    mmu = MMUAlternate()
    mmu.compile()
