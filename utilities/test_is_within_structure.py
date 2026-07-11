from brick.Brick import Brick
from brick.BrickType import BrickType
from brick_placement.ConstructionGrid import ConstructionGrid
from .simplified_grids import SimpleShapeCreator

brick_type = BrickType(name="2x4", x_length=2, z_length=4)
placed_brick = Brick(brickType=brick_type, y=0, z=2, x=0, orientation=(4,2))

result_grid = SimpleShapeCreator.break_cube(SimpleShapeCreator.create_cube(height=1, depth=4, width=6))
construction_grid = ConstructionGrid(result_grid)

# Valid Placement

print("Current Grid Region")
print(construction_grid.get_brick_bounds(placed_brick))
print("Is the brick within the target region")
print(construction_grid.validate_is_within_model(placed_brick))

# Invalid Placement
invalid_brick = Brick(brickType=brick_type, y=0, z=0, x=2, orientation=(4,2))

print("Current Grid Region")
print(construction_grid.get_brick_bounds(invalid_brick))
print("Is the brick within the target region")
print(construction_grid.validate_is_within_model(invalid_brick))

# This fails because the broken brick has a gap from z=0 tp z=2 which this brick now occupies, and so it is occupying an invalid space within the voxel grid