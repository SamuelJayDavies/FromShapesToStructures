import numpy as np

class SimpleShapeCreator:
    # Making this static because an instance isn't needed
    @staticmethod
    def create_cube(height: int, depth: int, width: int) -> np.ndarray:

        if height <= 0 or depth <= 0 or width <= 0:
            raise ValueError("Shape of the cube cannot be negative or zero")
        
        return np.ones(shape=(height, depth, width), dtype=bool)
    
    @staticmethod
    def break_cube(result_grid: np.ndarray) -> np.ndarray:
        """ Method that creates holes in a cube to test for placement outside of model structure. At the moment it is not dynamic and makes the same fixed change
        
        Args:
            result_grid: the array shape of the model that is being broken
        
        Returns:
            a result grid that will have broken spots"""
        result_grid[0, 0:2, 4:6] = False
        return result_grid