from .simplified_grids import SimpleShapeCreator
from brick_placement import ConstructionGrid

result_grid = SimpleShapeCreator.create_cube(1, 4, 6)

construction_grid = ConstructionGrid(result_grid)

print("Shape of result grid [y, z, x]: \n")
print(construction_grid.result_grid.shape)
print("Result Grid\n")
print(construction_grid.result_grid)
print("Current Grid\n")
print(construction_grid.current_grid)