""" Build and export all parts required for assebly for each configuration file in the build-configs directory """

from argparse import ArgumentParser
from pathlib import Path
from time import time

from bender_config import BenderConfig, LockStyle
from filament_bracket import FilamentBracket
from filament_wheel import FilamentWheel
from frame_top import TopFrame
from frame_connector import ConnectorFrame
from frame_bottom import BottomFrame
from lock_pin import LockPin
from sidewall import Sidewall
from guidewall import Guidewall

start_time = time()
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
    wheel = FilamentWheel(config.wheel)
    wheel.partomate()
    bracket = FilamentBracket(conf_file)
    bracket.partomate()
    topframe = TopFrame(config.top_frame_config)
    topframe.partomate()
    BottomFrame(config.top_frame_config).partomate()
    connectorframe = ConnectorFrame(config.connector_frame_config).partomate()
    Sidewall(config.sidewall_config).partomate()
    Guidewall(config.guidewall_config).partomate()
    if LockStyle.PIN in config.frame_lock_style:
        lockpin = LockPin(config.lock_pin_config)
        lockpin.partomate()
    print(
        f"\t{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds"
    )

print(f"Build Complete in {(time() - start_time):.2f} seconds")
