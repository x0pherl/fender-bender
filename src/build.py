""" Build and export all parts required for assebly for each configuration file in the build-configs directory """

from argparse import ArgumentParser
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from time import time
from copy import deepcopy

from bender_config import BenderConfig, LockStyle
from frame_config import FrameConfig, FrameStyle
from hanging_bracket import HangingBracket
from filament_bracket import FilamentBracket
from filament_wheel import FilamentWheel
from frame_top import TopFrame
from frame_connector import ConnectorFrame
from frame_bottom import BottomFrame
from hanging_bracket_config import HangingBracketStyle
from lock_pin import LockPin
from sidewall import Sidewall
from guidewall import Guidewall
from filament_bracket_config import ChannelPairDirection
from hanging_bracket import HangingBracket

import socket
import re
from contextlib import closing

from sidewall_config import WallStyle
from os import chdir

chdir(Path(__file__).parent)

# from ocp_vscode.standalone import Viewer


def ocp_responding() -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        ocp_open = sock.connect_ex(("127.0.0.1", 3939)) == 0
    return ocp_open


def nice_direction_name(direction: ChannelPairDirection) -> str:
    if direction == ChannelPairDirection.LEAN_REVERSE:
        return "reverse-path-angle"
    elif direction == ChannelPairDirection.STRAIGHT:
        return "straight-path-angle"
    else:
        return "forward-path-angle"


def leading_tabs(input_string: str) -> str:
    # Use a regular expression to match leading tabs
    match = re.match(r"^\t*", input_string)
    if match:
        return match.group(0)
    return ""


def dash_prefix(input_string: str) -> str:
    if input_string[0] == "-":
        return input_string
    return f"-{input_string}"


def headline(text: str) -> str:
    tabs = leading_tabs(text)
    return f"{tabs}{'-'*len(text)}\n{text}\n{tabs}{'-'*len(text)}"


def partomate_alt_solid_sidewalls(bender_config: BenderConfig):
    sidewall = Sidewall(bender_config.sidewall_config)

    sidewall._config.wall_style = WallStyle.SOLID
    sidewall._config.stl_folder = str(
        (Path(sidewall._config.stl_folder) / "alt-wall-styles")
    )
    sidewall._config.file_prefix = "alt-"
    sidewall._config.file_suffix = f"{sidewall._config.file_suffix}-solid"
    sidewall.partomate()


def partomate_alt_hex_sidewalls(bender_config: BenderConfig):
    sidewall = Sidewall(bender_config.sidewall_config)

    sidewall._config.wall_style = WallStyle.SOLID
    sidewall._config.stl_folder = str(
        (Path(sidewall._config.stl_folder) / "alt-wall-styles")
    )
    sidewall._config.file_prefix = "alt-"
    sidewall._config.file_suffix = f"{sidewall._config.file_suffix}-open-hex"
    sidewall.partomate()


def partomate_alt_non_dry_sidewalls(bender_config: BenderConfig):
    sidewall = Sidewall(bender_config.sidewall_config)

    sidewall._config.wall_style = WallStyle.HEX
    sidewall._config.stl_folder = str(
        (Path(sidewall._config.stl_folder) / "alt-wall-styles")
    )
    sidewall._config.file_prefix = "alt-"
    sidewall._config.file_suffix = f"{sidewall._config.file_suffix}-open-hex"
    sidewall._config.block_inner_wall_generation = True
    sidewall.partomate()


def partomate_alt_dry_sidewalls(bender_config: BenderConfig):
    sidewall = Sidewall(bender_config.sidewall_config)

    sidewall._config.wall_style = WallStyle.DRYBOX
    sidewall._config.stl_folder = str(
        (Path(sidewall._config.stl_folder) / "alt-wall-styles")
    )
    sidewall._config.file_prefix = "alt-"
    sidewall._config.file_suffix = f"{sidewall._config.file_suffix}-drybox"
    sidewall._config.block_inner_wall_generation = True
    sidewall.partomate()


def partomate_alt_guidewall(
    bender_config: BenderConfig,
    wall_style: WallStyle,
    override_filament_count=None,
):
    guidewall = Guidewall(bender_config.guidewall_config)

    guidewall._config.wall_style = wall_style
    if override_filament_count is not None:
        guidewall._config.section_count = override_filament_count
        guidewall._config.stl_folder = str(
            (
                Path(guidewall._config.stl_folder)
                / f"alt-{override_filament_count}-filament-parts"
            )
        )
        guidewall._config.file_suffix = f"-{override_filament_count}-filament"
    guidewall._config.file_prefix = "alt-"
    guidewall._config.stl_folder = str(
        (Path(guidewall._config.stl_folder) / "alt-wall-styles")
    )
    guidewall._config.file_suffix = (
        f"{guidewall._config.file_suffix}-{wall_style.name.lower()}"
    )
    guidewall.partomate()


def build_wheel(bender_config: BenderConfig):
    wheel = FilamentWheel(
        bender_config.wheel, stl_folder=bender_config.stl_folder
    )
    wheel.partomate()
    wheel._config.bearing.print_in_place = (
        not wheel._config.bearing.print_in_place
    )
    description = (
        "print-in-place-bearing"
        if wheel._config.bearing.print_in_place
        else "empty-bearing"
    )
    wheel._config.stl_folder = str(
        (Path(wheel._config.stl_folder) / f"alt-wheel-{description}")
    )
    wheel._config.file_prefix = "alt-"
    wheel._config.file_suffix = f"-{description}"
    wheel.partomate()


start_time = time()

if not ocp_responding():
    print("OCP_VSCODE port not open, exiting")
    exit()
    # need to work out how to get ocp_vscode standalone running on the gitlab runner
    # cfg = {}
    # cfg["host"] = '127.0.0.1'
    # cfg["port"] = 3939
    # Viewer(cfg).start()


parser = ArgumentParser(description="Build part stls")
parser.add_argument(
    "--config",
    type=str,
    help="The configuration file to run.",
    default="release",
)
args = parser.parse_args()

build_configs_dir = (Path(__file__).parent / "../build-configs").resolve()
# Get the list of configuration files
conf_files = [
    conf_file.resolve() for conf_file in build_configs_dir.glob("*.conf")
]

# Filter the configuration files based on the provided stem
if args.config:
    conf_files = [
        conf_file
        for conf_file in conf_files
        if (
            (conf_file.name.lower() == args.config.lower())
            | (conf_file.name.lower() == f"{args.config.lower()}.conf")
        )
    ]


def build_hanger_set(
    bender_config: BenderConfig, override_filament_count=None
):
    hanger_bender_config = deepcopy(bender_config)
    if override_filament_count is not None:
        hanger_bender_config.filament_count = override_filament_count
    hanging_bracket_config = hanger_bender_config.hanging_bracket_config

    if override_filament_count is not None:
        hanging_bracket_config.stl_folder = str(
            Path(bender_config.stl_folder)
            / f"alt-{override_filament_count}-filament-parts"
        )
        hanging_bracket_config.file_prefix = "alt-"
        hanging_bracket_config.file_suffix = (
            f"-{override_filament_count}-filament"
        )

    HangingBracket(hanging_bracket_config).partomate()

    if bender_config.skip_alt_file_generation:
        return

    tool_config = deepcopy(hanging_bracket_config)
    tool_config.bracket_style = HangingBracketStyle.SURFACE_TOOL
    tool_config.stl_folder = str((Path(tool_config.stl_folder) / "tools"))
    HangingBracket(tool_config).partomate()

    if hanging_bracket_config.bracket_style == HangingBracketStyle.WALL_MOUNT:
        surface_config = deepcopy(hanging_bracket_config)
        surface_config.bracket_style = HangingBracketStyle.SURFACE_MOUNT
        surface_config.stl_folder = str(
            (Path(hanging_bracket_config.stl_folder) / "alt-frame-hangers")
        )
        surface_config.file_prefix = "alt-"
        surface_config.heatsink_desk_nut = False
        surface_config.file_suffix = (
            f"{hanging_bracket_config.file_suffix}-surface-mount-m4-nut"
        )
        HangingBracket(surface_config).partomate()
        surface_config.heatsink_desk_nut = True
        surface_config.file_suffix = (
            f"{hanging_bracket_config.file_suffix}-surface-mount-m4-heatsink"
        )
        HangingBracket(surface_config).partomate()
    else:
        wall_config = deepcopy(hanging_bracket_config)
        wall_config.bracket_style = HangingBracketStyle.WALL_MOUNT
        wall_config.stl_folder = str(
            (Path(hanging_bracket_config.stl_folder) / "alt-frame-hangers")
        )
        wall_config.file_prefix = "alt-"
        wall_config.file_suffix = (
            f"{hanging_bracket_config.file_suffix}-wall-mount"
        )
        HangingBracket(wall_config).partomate()

        surface_config = deepcopy(hanging_bracket_config)
        surface_config.heatsink_desk_nut = not surface_config.heatsink_desk_nut
        surface_config.stl_folder = str(
            (Path(hanging_bracket_config.stl_folder) / "alt-frame-hangers")
        )
        surface_config.file_prefix = "alt-"
        surface_config.file_suffix = f"{hanging_bracket_config.file_suffix}-surface-mount-{"-m4-nut"
            if surface_config.heatsink_desk_nut
            else "-m4-heatsink"}"

        HangingBracket(surface_config).partomate()


def build_hangers(bender_config):
    print(headline(f"\t generating hangers"))
    print(f"\t\t generating default hanger")
    build_hanger_set(bender_config)

    if bender_config.skip_alt_file_generation:
        return

    for count in bender_config.alternate_filament_counts:
        print(
            f"\t\t generating hanger for {count} filament{"s" if count > 1 else ""}"
        )

        build_hanger_set(bender_config, override_filament_count=count)


def build_alt_style_frame_set(
    frame_config: FrameConfig, frame_style=FrameStyle
):
    alt_frame_config = deepcopy(frame_config)
    alt_frame_config.frame_style = frame_style
    alt_frame_config.stl_folder = str(
        (Path(alt_frame_config.stl_folder) / "alt-frame-styles")
    )
    alt_frame_config.file_prefix = "alt-"
    alt_frame_config.file_suffix = (
        f"{alt_frame_config.file_suffix}-{frame_style.name.lower()}"
    )
    if (FrameStyle.HANGING in frame_style) != (
        FrameStyle.HANGING in frame_config.frame_style
    ):
        TopFrame(alt_frame_config).partomate()
        ConnectorFrame(alt_frame_config).partomate()
    BottomFrame(alt_frame_config).partomate()

    if frame_style != FrameStyle.HANGING:
        dryflip_frame_config = deepcopy(alt_frame_config)
        dryflip_frame_config.drybox = not dryflip_frame_config.drybox
        dryflip_frame_config.file_suffix = f"{dryflip_frame_config.file_suffix}-{"not-" if not dryflip_frame_config.drybox else ""}drybox"
        BottomFrame(dryflip_frame_config).partomate()


def build_frame_set(bender_config: BenderConfig, override_filament_count=None):
    original_filament_count = bender_config.filament_count

    if override_filament_count is not None:
        bender_config.filament_count = override_filament_count
    frame_config = bender_config.frame_config

    lockpin_config = bender_config.lock_pin_config
    count_name_str = ""
    if override_filament_count is not None:
        count_name_str = f"{override_filament_count}-filament"

        frame_config.stl_folder = str(
            (Path(frame_config.stl_folder) / f"alt-{count_name_str}-parts")
        )
        frame_config.file_prefix = "alt-"
        frame_config.file_suffix = f"-{count_name_str}"
        lockpin_config.stl_folder = str(
            (Path(lockpin_config.stl_folder) / f"alt-{count_name_str}-parts")
        )
        lockpin_config.file_prefix = "alt-"
        lockpin_config.file_suffix = f"-{count_name_str}"

    TopFrame(frame_config).partomate()
    ConnectorFrame(frame_config).partomate()
    BottomFrame(frame_config).partomate()
    LockPin(lockpin_config).partomate()

    if not bender_config.skip_alt_file_generation:
        if FrameStyle.HANGING in frame_config.frame_style:
            build_alt_style_frame_set(frame_config, FrameStyle.STANDING)
        if frame_config.frame_style == FrameStyle.STANDING:
            build_alt_style_frame_set(frame_config, FrameStyle.HANGING)
        if frame_config.frame_style != FrameStyle.HYBRID:
            build_alt_style_frame_set(frame_config, FrameStyle.HYBRID)
    bender_config.filament_count = original_filament_count
    return


def build_frames(bender_config: BenderConfig):
    print(headline(f"\t generating frames"))
    print(f"\t\t generating default frame")
    build_frame_set(bender_config)
    for count in bender_config.alternate_filament_counts:
        print(
            f"\t\t generating frame for {count} filament{"s" if count > 1 else ""}"
        )
        build_frame_set(bender_config, override_filament_count=count)


def build_brackets(bender_config: BenderConfig):
    print(f"\t generating filament brackets")
    for direction_index, direction in enumerate(ChannelPairDirection):
        if (
            direction != bender_config.bracket_direction
            and bender_config.skip_alt_file_generation
        ):
            continue
        print(f"\t generating brackets for {direction.name}")
        for connector_index, connector in enumerate(bender_config.connectors):
            print(f"\t\t generating bracket with {connector.name}")
            bracket = FilamentBracket(
                bender_config.filament_bracket_config(connector_index)
            )
            bracket._config.channel_pair_direction = direction
            if direction != bender_config.bracket_direction:
                bracket._config.stl_folder = str(
                    Path(bracket._config.stl_folder)
                    / f"alt-brackets-{nice_direction_name(direction)}"
                )
                bracket._config.file_prefix = "alt-"
                bracket._config.file_suffix = f"{bracket._config.file_suffix}-{nice_direction_name(direction)}"
                bracket._config.block_pin_generation = True
            if connector_index > 0:
                bracket._config.block_pin_generation = True
                bracket._config.stl_folder = str(
                    Path(bracket._config.stl_folder)
                    / f"alt-brackets-{nice_direction_name(direction)}-alternate-connectors"
                )
                bracket._config.file_prefix = "alt-"
                bracket._config.file_suffix = f"{bracket._config.file_suffix}{dash_prefix(connector.file_suffix)}"
            bracket.partomate()


def build_guidewall_set(
    bender_config: BenderConfig, override_filament_count=None
):
    guidewall_config = bender_config.guidewall_config
    if override_filament_count is not None:
        guidewall_config.section_count = override_filament_count

    if override_filament_count is not None:
        guidewall_config.stl_folder = str(
            (
                Path(guidewall_config.stl_folder)
                / f"alt-{override_filament_count}-filament-parts"
            )
        )
        guidewall_config.file_prefix = "alt-"
        guidewall_config.file_suffix = f"-{override_filament_count}-filament"
    guidewall = Guidewall(guidewall_config)
    guidewall.partomate()

    if bender_config.skip_alt_file_generation:
        return

    if bender_config.wall_style != WallStyle.DRYBOX:
        partomate_alt_guidewall(
            bender_config, WallStyle.DRYBOX, override_filament_count
        )
    if bender_config.wall_style != WallStyle.SOLID:
        partomate_alt_guidewall(
            bender_config, WallStyle.SOLID, override_filament_count
        )
    if bender_config.wall_style != WallStyle.HEX:
        partomate_alt_guidewall(
            bender_config, WallStyle.HEX, override_filament_count
        )


def build_walls(bender_config: BenderConfig):
    print(f"\t generating walls")
    sidewall = Sidewall(bender_config.sidewall_config)
    sidewall.partomate()
    build_guidewall_set(bender_config)

    if bender_config.skip_alt_file_generation:
        return

    if sidewall._config.wall_style == WallStyle.SOLID:
        sidewall._config.wall_style = WallStyle.HEX
        sidewall._config.stl_folder = str(
            (Path(sidewall._config.stl_folder) / "alt-wall-styles")
        )
        sidewall._config.file_suffix = f"{sidewall._config.file_suffix}-hex"
        sidewall.partomate()
    elif sidewall._config.wall_style == WallStyle.HEX:
        print(f"\t\t generating alternate solid sidewalls")
        partomate_alt_solid_sidewalls(bender_config)
    elif (
        sidewall._config.wall_style == WallStyle.DRYBOX
        and sidewall._config.wall_style != WallStyle.SOLID
    ):
        print(f"\t\t generating alternate hex sidewalls")
        partomate_alt_non_dry_sidewalls(bender_config)
    if sidewall._config.wall_style != WallStyle.HEX:
        print(f"\t\t generating alternate drybox sidewalls")
        partomate_alt_dry_sidewalls(bender_config)

    for count in bender_config.alternate_filament_counts:
        print(
            f"\t\t generating guidewalls for {count} filament{"s" if count > 1 else ""}"
        )

        build_guidewall_set(bender_config, override_filament_count=count)


if not conf_files:
    print("No matching configuration file found")
    exit()

# Run the script for the matching configuration file(s)
for conf_file in conf_files:
    bender_config = BenderConfig(conf_file)
    if bender_config.stl_folder == "NONE":
        continue
    print(headline(f"Generating parts for {conf_file.name}"))

    iteration_start_time = time()
    build_brackets(bender_config)
    build_wheel(bender_config)
    build_walls(bender_config)
    build_frames(bender_config)
    build_hangers(bender_config)

    print(
        headline(
            f"{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds"
        )
    )

    # TODO --need to get documentation generation sorted
    # loader = SourceFileLoader("__main__", "assembly_documentation.py")
    # loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
print()
print(headline(f"Build Complete in {(time() - start_time):.2f} seconds"))
