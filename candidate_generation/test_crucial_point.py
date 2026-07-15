import numpy as np

from brick.Brick_vocabulary import BASIC_BRICK_VOCABULARY
from candidate_generation.CandidateGenerator import CandidateGenerator

# Ensuring that it does through all lower level until the y-axis

# this just sets all available positions in this free_grid as False
free_grid = np.zeros(
    shape=(2, 3, 4),
    dtype=bool,
)

free_grid[0, 1, 2] = True
free_grid[0, 2, 0] = True
free_grid[1, 0, 0] = True

generator = CandidateGenerator(
    brick_vocabulary=BASIC_BRICK_VOCABULARY,
)

crucial_point = generator.find_next_crucial_point(
    free_grid=free_grid,
)

print("Available grid:")
print(free_grid)

print("\nSelected crucial pt:")
print(crucial_point)

free_grid[0, 1, 2] = False

crucial_point = generator.find_next_crucial_point(
    free_grid=free_grid,
)

print("Available grid:")
print(free_grid)

print("\nSelected crucial pt:")
print(crucial_point)

free_grid[0, 2, 0] = False

crucial_point = generator.find_next_crucial_point(
    free_grid=free_grid,
)

print("Available grid:")
print(free_grid)

print("\nSelected crucial pt:")
print(crucial_point)