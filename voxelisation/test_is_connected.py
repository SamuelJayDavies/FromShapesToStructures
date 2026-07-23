from brick.Brick import Brick
from brick.BrickType import BrickType
from brick_placement.ConstructionGrid import ConstructionGrid
from .simplified_grids import SimpleShapeCreator

brick_type = BrickType(name="2x4", x_length=2, z_length=4)
lower_brick = Brick(brickType=brick_type, y=0, z=2, x=0, orientation=(4,2))
upper_brick = Brick(brickType=brick_type, y=1, z=2, x=0, orientation=(4,2))

result_grid = SimpleShapeCreator.create_cube(height=4, depth=4, width=6)
construction_grid = ConstructionGrid(result_grid)

print("Can the upper brick be placed before the lower brick: " + str(construction_grid.validate_brick_is_connected(upper_brick)))

construction_grid.place_brick(lower_brick)
print(construction_grid.current_grid)

print("Can the upper brick be placed after the lower brick: " + str(construction_grid.validate_brick_is_connected(upper_brick)))

construction_grid.place_brick(upper_brick)

print(construction_grid.current_grid)

print(construction_grid.calculate_support_ratio(upper_brick))

new_result_grid = SimpleShapeCreator.create_cube(height=10, depth=10, width=10)
construction_grid_2 = ConstructionGrid(new_result_grid)


# This test results in 50% look at the paint graph in Overleaf to help understand
#lower_brick_2 = Brick(brickType=brick_type, y=0, z=2, x=0, orientation=(4,2))
#test_support_brick = Brick(brickType=brick_type, y=1, z=3, x=0, orientation=(4,2))

# And as the orientation is (width=4, depth=2) a change in width by 1 will reduce support by 1/4 so 0.75
# and a change in depth will halve the support by a change of 1/2
lower_brick_2 = Brick(brickType=brick_type, y=0, z=2, x=0, orientation=(4,2))
test_support_brick = Brick(brickType=brick_type, y=1, z=2, x=1, orientation=(4,2))

construction_grid_2.place_brick(lower_brick_2)

print("Can you place upper_brick at its current position")
print(construction_grid_2.calculate_support_ratio(test_support_brick))
construction_grid_2.place_brick(test_support_brick)