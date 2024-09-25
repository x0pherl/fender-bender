""" Build and export all parts required for assebly for each configuration file in the build-configs directory """

from argparse import ArgumentParser
from pathlib import Path
from time import time

from bank_config import BankConfig, LockStyle
from filament_bracket import FilamentBracket
from filament_wheel import FilamentWheel
from frames import FrameSet
from lock_pin import LockPin
from walls import Walls

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
    config = BankConfig(conf_file)
    if config.stl_folder == "NONE":
        continue
    print(f"Generating parts for {conf_file.name}")
    print(f"\t connector diam is {config.default_connector.diameter}")
    iteration_start_time = time()
    wheel = FilamentWheel(conf_file)
    wheel.partomate()
    bracket = FilamentBracket(conf_file)
    bracket.partomate()
    frameset = FrameSet(conf_file)
    frameset.partomate()
    walls = Walls(conf_file)
    walls.partomate()
    if LockStyle.PIN in config.frame_lock_style:
        lockpin = LockPin(conf_file)
        lockpin.partomate()
    print(
        f"\t{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds"
    )

print(f"Build Complete in {(time() - start_time):.2f} seconds")
