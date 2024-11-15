""" Build and export all parts required for assebly for each configuration file in the build-configs directory """

from argparse import ArgumentParser
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from time import time

from bender_config import BenderConfig, LockStyle
from hanging_brackets import HangingBrackets
from filament_bracket import FilamentBracket
from filament_wheel import FilamentWheel
from frame_top import TopFrame
from frame_connector import ConnectorFrame
from frame_bottom import BottomFrame
from lock_pin import LockPin
from sidewall import Sidewall
from guidewall import Guidewall

import socket
from contextlib import closing

# from ocp_vscode.standalone import Viewer

alternate_filament_counts = {
    "single filament": 1,
    "8-filament": 8,
    "12-filament": 12,
}


def ocp_responding() -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        ocp_open = sock.connect_ex(("127.0.0.1", 3939)) == 0
    return ocp_open


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
    "--config", type=str, help="The configuration file to run."
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

if not conf_files:
    print("No matching configuration file found")
    exit()

# Run the script for the matching configuration file(s)
for conf_file in conf_files:
    config = BenderConfig(conf_file)
    if config.stl_folder == "NONE":
        continue
    print(f"Generating parts for {conf_file.name}")
    print(f"\t connector diam is {config.default_connector.diameter}")
    iteration_start_time = time()
    HangingBrackets(config.frame_config).partomate()
    FilamentWheel(config.wheel, config.stl_folder).partomate()
    FilamentBracket(conf_file).partomate()
    TopFrame(config.frame_config).partomate()
    BottomFrame(config.frame_config).partomate()
    ConnectorFrame(config.frame_config).partomate()
    Sidewall(config.sidewall_config).partomate()
    Guidewall(config.guidewall_config).partomate()
    if LockStyle.PIN in config.frame_lock_style:
        lockpin = LockPin(config.lock_pin_config)
        lockpin.partomate()
    print("Generating alternate frame parts")
    original_stl_folder = config.stl_folder
    for name, count in alternate_filament_counts.items():
        print(f"{name} has {count} filaments")
        config.stl_folder = str(
            Path(original_stl_folder) / "alt" / f"frame-parts-{name}"
        )
        config.filament_count = count
        Guidewall(config.guidewall_config).partomate()
        TopFrame(config.frame_config).partomate()
        BottomFrame(config.frame_config).partomate()
        ConnectorFrame(config.frame_config).partomate()
    print(
        f"\t{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds"
    )

    # TODO -- this is an awful hack for now, but build is not the most important bit of software
    loader = SourceFileLoader("__main__", "assembly_documentation.py")
    loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

print(f"Build Complete in {(time() - start_time):.2f} seconds")
