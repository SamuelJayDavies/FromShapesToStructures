import numpy as np
import pandas as pd

from brick_placement import ConstructionGrid


result_shape = np.ones(
    shape=(2, 3, 4),
    dtype=bool,
)

construction_grid = ConstructionGrid(result_shape)

df = pd.DataFrame(construction_grid.current_grid[0])
print("Initial Construction Grid (Layer 0):")
print(df)

print("Result Shape:", construction_grid.result_shape)
print("Construction grid:")
print(construction_grid.current_grid)

print("Is empty:", construction_grid.is_empty())
print("Cell occupied:", construction_grid.is_occupied(0, 0, 0))
print("Cell brick ID:", construction_grid.get_brick_id(0, 0, 0))
print("Generated grid:")
print(construction_grid.convert_to_result_grid().astype(int))