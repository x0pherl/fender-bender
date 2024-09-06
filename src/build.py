""" Build and export all parts required for assebly for each configuration file in the build-configs directory """
from pathlib import Path
from time import time
from filament_wheel import FilamentWheel
from frames import FrameSet
from walls import Walls
from bank_config import BankConfig, LockStyle
from filament_bracket import FilamentBracket
from lock_pin import LockPin

start_time = time()
build_configs_dir = (Path(__file__).parent / '../build-configs').resolve()
##handle kwargs???
for conf_file in [conf_file.resolve() for conf_file in build_configs_dir.glob('*.conf')]:
    config = BankConfig(conf_file)
    if config.stl_folder == "NONE":
        continue
    print(f"Generating parts for {conf_file.name}")
    config = BankConfig(conf_file)
    iteration_start_time = time()
    wheel = FilamentWheel(conf_file)
    wheel.partomate()
    frameset = FrameSet(conf_file)
    frameset.partomate()
    walls = Walls(conf_file)
    walls.partomate()
    bracket = FilamentBracket(conf_file)
    bracket.partomate()
    if LockStyle.PIN in config.frame_lock_style:
        lockpin = LockPin(conf_file)
        lockpin.partomate()
    print(f"\t{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds")

print(f"Build Complete in {(time() - start_time):.2f} seconds")
