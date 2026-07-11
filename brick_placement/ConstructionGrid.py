import numpy as np

from brick import Brick

class ConstructionGrid:
    def __init__(self, result_grid: np.ndarray) -> None:

        # Validation Checks
        if result_grid.ndim != 3:
            raise ValueError("Result Grid must be 3-dimensions of shape (y,z,x).")

        self.result_grid = result_grid.astype(bool).copy()
        self.result_shape = result_grid.shape

        # Currently populate with -1 for empty and eventually populate with ID's of placed bricks
        self.current_grid = np.full(
            shape=self.result_shape,
            fill_value=-1,
            dtype=np.int32
        )

        self.placed_bricks = []

    def is_valid_coordinate(self, y: int, z: int, x: int) -> bool:
        if y < 0 or y >= self.result_shape[0]:
            print("Y coordinate is out of bounds of the result grid.")
            return False
        if z < 0 or z >= self.result_shape[1]:
            print("Z coordinate is out of bounds of the result grid.")
            return False
        if x < 0 or x >= self.result_shape[2]:
            print("X coordinate is out of bounds of the result grid.")
            return False
        return True

    def is_occupied(self, y: int, z: int, x: int) -> bool:
        if(not self.is_valid_coordinate(y, z, x)):
            raise ValueError("Invalid coordinate provided.")
        else:
            return self.current_grid[y, z, x] != -1
        
    def get_brick_id(self, y: int, z: int, x: int) -> int:
        if(not self.is_valid_coordinate(y, z, x)):
            raise ValueError("Invalid coordinate provided.")
        else:
            return int(self.current_grid[y, z, x])
        
    def convert_to_result_grid(self) -> np.ndarray:
        return self.current_grid != -1
    
    def is_empty(self) -> bool:
        return not np.any(self.convert_to_result_grid())
    
    def get_brick_bounds(self, brick: Brick) -> tuple[int, int, int, int, int]:
        # This is done in this format to work well with numpy slicing 
        y = brick.y
        z_start = brick.z
        z_end = brick.z + brick.size_z()
        x_start = brick.x
        x_end = brick.x + brick.size_x()

        return (y, z_start, z_end, x_start, x_end)
    
    def validate_brick_in_bounds(self, y: int, z_start: int, z_end: int, x_start: int, x_end: int) -> bool:
        
        size_y, size_z, size_x = self.result_shape
        if y < 0 or y >= size_y:
            print("Y coordinate is not within the bounds of the result grid.")
            return False
        if z_start < 0 or z_end > size_z:
            print("Z coordinates are not within the bounds of the result grid.")
            return False
        if x_start < 0 or x_end > size_x:
            print("X coordinates are not within the bounds of the result grid.")
            return False
        return True

    def get_grid_region(self, brick: Brick) -> np.ndarray:
        y, z_start, z_end, x_start, x_end = self.get_brick_bounds(brick)
        
        if not self.validate_brick_in_bounds(y, z_start, z_end, x_start, x_end):
            raise ValueError("Brick is being placed outside of the bounds of the result grid.")
        
        else:
            return self.current_grid[y, z_start:z_end, x_start:x_end]
        
    def validate_brick_does_not_conflict(self, grid_bounds: np.ndarray) -> bool:
        # If any of these grid bounds are occupied, the brick cannot be placed
        if np.any(grid_bounds != -1):
            print("Existing brick(s) already occupy this current space.")
            return False
        else:
            return True

    def validate_is_within_model(self, brick: Brick) -> bool:
        """ Ensures that every voxel occupied by the brick, is a valid voxel from the original model 
        (essentially, only place bricks in voxels that need to be occupied)
        
        Args:
            brick: the brick that is being placed
            
        Returns:
            true: if the brick occupies voxels from the original model, otherwise false
        """
        y, z_start, z_end, x_start, x_end = self.get_brick_bounds(brick)

        if not self.validate_brick_in_bounds(y, z_start, z_end, x_start, z_end):
            print("Brick: " + brick.brickType.name + " cannot be placed outside of the bounds of the result grid")
            return False
        
        brick_occupied_result_region = self.result_grid[y, z_start:z_end, x_start:x_end]

        # Get the area that is being currently occupied by the brick and ensure every voxel position is true
        # essentially ensure the brick is only occupying regions of the model that it needs to
        # we don't want any part of the brick extending beyond the target region of the model
        if not np.all(brick_occupied_result_region):
            print("Brick " + brick.brickType.name + " is occupying a space outside of the models result/target region")
            return False
        else:
            return True
    
    def validate_brick_is_connected(self, brick: Brick) -> bool:

        y, z_start, z_end, x_start, x_end = self.get_brick_bounds(brick)

        # No need to check if in bounds, already checked

        if y==0:
            return True
        
        support_region = self.current_grid[y-1, z_start:z_end, x_start:x_end]

        if not np.any(support_region != -1):
            print("Brick has no lower-level connection and hence is floating")
            return False
        else:
            return True

        
    def place_brick(self, brick: Brick) -> None:

        if brick.is_placed():
            raise ValueError("Brick has already been placed.")
        elif not self.validate_is_within_model(brick):
            raise ValueError("Brick cannot extend outside of the model's structure")
        else:
            grid_bounds = self.get_grid_region(brick)

            if not self.validate_brick_does_not_conflict(grid_bounds):
                raise ValueError("Brick cannot be placed as it conflicts with existing bricks.")
            elif not self.validate_brick_is_connected(brick):
                raise ValueError("Brick cannot be placed because it is not connected to a brick on a lower-level")
            else:
                brick_id = len(self.placed_bricks)

                # Place the brick in the brick class
                brick.place_brick(brick_id)

                # Place the brick in the brick array
                self.placed_bricks.append(brick)

                # Place the brick inside the grid_bounds
                grid_bounds[:, :] = brick_id