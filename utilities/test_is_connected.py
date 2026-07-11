from brick.Brick import Brick
from brick.BrickType import BrickType
from brick_placement.ConstructionGrid import ConstructionGrid
from .simplified_grids import SimpleShapeCreator

brick_type = BrickType(name="2x4", x_length=2, z_length=4)
lower_brick = Brick(brickType=brick_type, y=0, z=2, x=0, orientation=(4,2))
upper_brick = Brick(brickType=brick_type, y=1, z=2, x=0, orientation=(4,2))

result_grid = SimpleShapeCreator.create_cube(height=3, depth=4, width=6)
construction_grid = ConstructionGrid(result_grid)

print("Can the upper brick be placed before the lower brick: " + str(construction_grid.validate_brick_is_connected(upper_brick)))

construction_grid.place_brick(lower_brick)
print(construction_grid.current_grid)

print("Can the upper brick be placed after the lower brick: " + str(construction_grid.validate_brick_is_connected(upper_brick)))

construction_grid.place_brick(upper_brick)

print(construction_grid.current_grid)