import numpy as np

from brick import Brick
from brick import BrickType
from brick_placement import ConstructionGrid


target_grid = np.ones(
    shape=(1, 4, 6),
    dtype=bool,
)

construction_grid = ConstructionGrid(target_grid)

brick_type = BrickType("2x4", 2, 4)

brick = Brick(
    brickType=brick_type,
    y=0,
    z=1,
    x=2,
    orientation=(4, 2),
)

print("Footprint bounds:")
print(construction_grid.get_footprint_bounds(brick))

print()

print("Footprint region:")
print(construction_grid.get_footprint_region(brick))