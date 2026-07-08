import numpy as np

from brick import Brick
from brick import BrickType
from brick_placement import ConstructionGrid


result_grid = np.ones(
    shape=(1, 4, 6),
    dtype=bool,
)

construction_grid = ConstructionGrid(result_grid)

brick_type = BrickType("2x4", 2, 4)

brick = Brick(
    brickType=brick_type,
    y=0,
    z=1,
    x=2,
    orientation=(4, 2),
)

print("Brick bounds:")
print(construction_grid.get_brick_bounds(brick))

print()

print("Grid region:")
print(construction_grid.get_grid_bounds(brick))