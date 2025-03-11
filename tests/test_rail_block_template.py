from rail_block import rail_block_template
from build123d import Part
import pytest


class TestRailBlockTemplate:
    def test_rail_block_template(self):
        rail_block = rail_block_template(
            width=10, length=20, depth=10, radius=1, inset=0.2, rail_width=1
        )
        assert rail_block.is_valid()
        assert isinstance(rail_block, Part)
        assert rail_block.bounding_box().size.X == pytest.approx(24.8)
        assert rail_block.bounding_box().size.Y == pytest.approx(9.8)
        assert rail_block.bounding_box().size.Z == pytest.approx(10.8)
