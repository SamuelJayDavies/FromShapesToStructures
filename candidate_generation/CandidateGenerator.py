import numpy as np

from brick.Brick import Brick
from brick.BrickType import BrickType
from brick.Brick_vocabulary import Brick_vocabulary

from brick_placement.ConstructionGrid import ConstructionGrid

class CandidateGenerator:

    # we will deem an available grid as the result_grid - occupied_grid (construction_grid)

    def __init__(self, brick_vocabulary: Brick_vocabulary) -> None:

        if not isinstance(brick_vocabulary, Brick_vocabulary):
            raise TypeError("Brick vocabulary must be of type Brick_vocabulary")
        
        self.brick_vocabulary = brick_vocabulary

    def _validate_free_grid(self, free_grid: np.ndarray) -> bool:
        
        if not isinstance(free_grid, np.ndarray):
            print("Available grid is of the wrong type and should be a NumPy Array")
            return False
        elif free_grid.ndim != 3:
            print("Available grid should be three-dimensional in the form (y, z, x)")
            return False
        elif free_grid.dtype != np.bool:
            print("Avaiable grid should be strictly boolean values (likely the result grid or construction grid was incorrectly passed)")
            return False
        elif any(size == 0 for size in free_grid.shape):
            print("One of the dimensions is empty")
            return False
        else:
            return True
        
    # Note for later that will help reunderstand this method
    # We are looking for which positions are True, because our result_grid had True positions as needing to be filled and part of the target shape
    # Whereas False meant the voxel was empty or outside the target shape
    # This same rule is applied here, as either, False means it has already been covered by a birck, or is outside the target position, while True means it is ready for placement
    def find_next_crucial_point(self, free_grid: np.ndarray) -> tuple[int, int, int] | None:
        if(not self._validate_free_grid):
            raise ValueError("Free grid failed validation, look above for debugging reason")
        else:
            size_y, size_z, size_x = free_grid.shape

            # This ordering ensures the model is created from the ground-layer upwards
            for y in range(size_y):

                for z in range(size_z):

                    for x in range(size_x):

                        if free_grid[y, z, x]:
                            return y, z, x
            
            return None

    def _validate_crucial_point(self, crucial_point: tuple[int, int, int], free_grid: np.ndarray) -> bool:

        if len(crucial_point) != 3:
            print("Crucial point must contain exactly three coordinates: (y, z, x)")
            return False
        elif not all(isinstance(coordinate, int) for coordinate in crucial_point):
            print("One of the dimensions within the crucial point is not an integer value")
            return False
        else:
            
            crucial_y, crucial_z, crucial_x = crucial_point

            size_y, size_z, size_x = free_grid.shape

            if not(0 <= crucial_y < size_y and 0 <= crucial_z < size_z and 0 <= crucial_x < size_x):
                print("Crucial point is outside of the free grids shape")
                return False
            elif not free_grid[crucial_y, crucial_z, crucial_x]:
                print("Voxel targetted by the crucial point is currently occupied or outside of the target shape")
                return False
            else:
                return True

    def _validate_orientation(self, orientation: tuple[int, int]) -> bool:

        if not all(isinstance(dimension, int) for dimension in orientation):
            print("Dimension of the orientation is not an integer value")
            return False
        elif any(dimension < 1 for dimension in orientation):
            print("For a valid brick value orientation, it has to be at least 1")
        else:
            return True

    def _validate_area_is_free(self, free_grid: np.ndarray, candidate_origin: tuple[int, int, int], orientation: tuple[int, int]) -> bool:
        """ Method that validates that the area being taken up by a placed brick over its crucial point is available and not currently occupied by a brick or outside the target shape 
        
        Args:
            free_grid: an array that has the same shape as the result grid with every True position a target voxel available to fill and False position a space outside the target or already occupied
            candidate_origin: the coordinates where the candidate will be placed
            orientation: the width and depth of the brick being placed

        Returns:
            True if the area is free for the brick to be placed on
        """
        candidate_y, candidate_z, candidate_x = candidate_origin
        size_x, size_z = orientation

        candidate_end_z = candidate_z + size_z
        candidate_end_x = candidate_x + size_x

        candidate_area = free_grid[candidate_y, candidate_z:candidate_end_z, candidate_x:candidate_end_x]

        # if any position is false, the area is not safe to place a brick on
        return bool(np.all(candidate_area))
        
    def generate_candidate_origins(self, free_grid: np.ndarray, crucial_point: tuple[int, int, int], orientation: tuple[int, int]) -> list[tuple[int, int, int]]:

        if not self._validate_free_grid(free_grid):
            raise ValueError("Free grid failed to validate for the above stated reason")
        elif not self._validate_crucial_point(crucial_point, free_grid):
            raise ValueError("Crucial point failed to validate for the above stated reason")
        elif not self._validate_orientation(orientation):
            raise ValueError("Orienation failed due to incorrect integer value or due to an integer value lower than 1")
        else:
            crucial_y, crucial_z, crucial_x = crucial_point
            size_x, size_z = orientation

            # We work on layer at a time so the y vertical layer is ignored
            _, grid_size_z, grid_size_x = free_grid.shape

            candidate_origins: list[tuple[int, int, int]] = []

            # Now by looping through every combination of origin placement, we can understand where the brick could be placed and still cover that crucial point
            for z_offset in range(size_z):
                for x_offset in range(size_x):

                    candidate_z = (crucial_z - z_offset)
                    candidate_x = (crucial_x - x_offset)

                    # In the case where the crucial point is at a position that is less than a poitential offset value
                    if  candidate_z < 0 or candidate_x < 0:
                        # coordinate is negative so just restart the loop
                        continue
                    else:
                        candidate_end_z = candidate_z + size_z
                        candidate_end_x = candidate_x + size_x
                        
                        
                        if  candidate_end_z > grid_size_z or candidate_end_x > grid_size_x:
                            # coordinate goes outside the free grid so just restart the loop
                            continue
                        else:
                            candidate_origins.append((crucial_y, candidate_z, candidate_x))
            return candidate_origins
        
    def generate_candidates_for_singular_brick_type(self, free_grid: np.ndarray, crucial_point: tuple[int, int, int], brick_type: BrickType) -> list[Brick]:

        candidates: list[Brick] = []

        for orientation in brick_type.orientations():
            candidate_origins = self.generate_candidate_origins(free_grid, crucial_point, orientation)

            for candidate_origin in candidate_origins:

                if not self._validate_area_is_free(free_grid, candidate_origin, orientation):
                    continue

                candidate = Brick(brick_type, candidate_origin[0], candidate_origin[1], candidate_origin[2], orientation)

                candidates.append(candidate)
            
        return candidates

    def genereate_all_candidates(self, free_grid: np.ndarray, crucial_point: tuple[int, int, int]) -> list[Brick]:

        candidates: list[Brick] = []

        for brick_type in self.brick_vocabulary:
            brick_type_candidates = self.generate_candidates_for_singular_brick_type(free_grid, crucial_point, brick_type)

            candidates.append(brick_type_candidates)

        return candidates





