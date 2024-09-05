from pathlib import Path
from filament_wheel import FilamentWheel
from frames import FrameSet
from walls import Walls
from filament_bracket import FilamentBracket
from time import time

start_time = time()
build_configs_dir = (Path(__file__).parent / '../build-configs').resolve()
##handle kwargs???
for conf_file in [conf_file.resolve() for conf_file in build_configs_dir.glob('*.conf')]:
    if conf_file.name == "debug.conf":
        continue
    print(f"Generating parts for {conf_file.name}")
    iteration_start_time = time()
    wheel = FilamentWheel(conf_file)
    wheel.partomate()
    frameset = FrameSet(conf_file)
    frameset.partomate()
    walls = Walls(conf_file)
    walls.partomate()
    bracket = FilamentBracket(conf_file)
    bracket.partomate()
    print(f"\t{conf_file.stem} configuration built in {(time() - iteration_start_time):.2f} seconds")

print(f"Build Complete in {(time() - start_time):.2f} seconds")
