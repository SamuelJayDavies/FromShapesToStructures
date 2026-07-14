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

print("Before committing:")
print(construction_grid.current_grid)
print("Brick placed?", brick.is_placed())

construction_grid.place_brick(brick)

print()
print("Assigned ID:", brick.brick_id)

print()
print("After committing:")
print(construction_grid.current_grid)
print("Brick placed?", brick.is_placed())
print("Brick ID:", brick.brick_id)
print("Placed bricks:", construction_grid.placed_bricks)