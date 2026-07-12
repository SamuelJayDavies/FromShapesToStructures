import numpy as np

from brick import Brick

class ConstructionGrid:
    def __init__(self, result_grid: np.ndarray, minimum_support_ratio: float = 0.5) -> None:

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

        # Currently at least half of the bricks below a newly placed brick need to be occupied for a ratio of 0.5
        # This works as a baseline configuration and no assumed universal physical law so it won't be mentioned like that in the diss
        self.minimum_support_ratio = minimum_support_ratio

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
    
    # Different to is a valid coordinate, as you can have a brick placed via coordinates within the bounds of
    # the construction grid, while its length can make it extend outside of the grid, this is what this method checks
    def validate_brick_in_bounds(self, brick:Brick) -> bool:
        
        size_y, size_z, size_x = self.result_shape
        y, z_start, z_end, x_start, x_end = self.get_brick_bounds(brick)
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
        
        if not self.validate_brick_in_bounds(brick):
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

        if not self.validate_brick_in_bounds(brick):
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

    def get_supported_region(self, brick:Brick) -> np.ndarray:

        y, z_start, z_end, x_start, x_end = self.get_brick_bounds(brick)

        if not self.validate_brick_in_bounds(brick):
            print("Brick: " + brick.brickType.name + " cannot be placed outside of the bounds of the result grid")
            raise ValueError("No support can be provided outside the grid")
        elif y==0:
            print("Brick: " + brick.brickType.name + " cannot have support below the bottom of the y-axis or below the ground")
            raise ValueError("No support can be provided below the ground")
        else:
            support_region = self.current_grid[y-1, z_start:z_end, x_start:x_end]
            return support_region


            
    def validate_brick_is_connected(self, brick: Brick) -> bool:
        # No need to check if in bounds, already checked

        if brick.y==0:
            return True
        
        support_region = self.get_supported_region(brick)

        if not np.any(support_region != -1):
            print("Brick has no lower-level connection and hence is floating")
            return False
        else:
            return True
    
    def calculate_support_ratio(self, brick:Brick) -> float:
        if brick.y == 0:
            return 1.0
        else:
            # This can throw an error here if incorrect could check if more thoroughly later but kinda unnecessary
            support_region = self.get_supported_region(brick)

            supported_studs = np.count_nonzero(support_region != -1)
            total_occupied_area = support_region.size

            support_ratio = supported_studs / total_occupied_area
            return support_ratio

    def validate_minimum_support(self, brick:Brick) -> bool:

        support_ratio = self.calculate_support_ratio(brick)

        if support_ratio < self.minimum_support_ratio:
            print("Support of brick: " + brick.brickType.name + " is below the threshold of " + str(self.minimum_support_ratio) + " supported studs")
            return False
        else:
            return True
        
    def can_place_brick(self, brick: Brick) -> bool:
        # Obviously this method can be done shorter, but i prefer to see each condition that is being checked explicity
        grid_bounds = self.get_grid_region(brick)

        # 1. Has the brick already been placed 
        if brick.is_placed():
            print("The brick has already been placed")
            return False
        # 2. Is the brick in the bounds of the construction grid
        elif not self.validate_brick_in_bounds(brick):
            return False
        # 3. The brick is being placed within an occupied voxel of the result grid (it is matching the model visually)
        elif not self.validate_is_within_model(brick):
            return False
        # 4. The brick doesn't occupy the same area as an existing brick
        elif not self.validate_brick_does_not_conflict(grid_bounds):
            return False
        # 5. The brick is connected to the ground or a block on a lower level of the y-axis 
        elif not self.validate_brick_is_connected(brick):
            return False
        # 6. The brick has the minimum required level of support to remain stable
        elif not self.validate_minimum_support(brick):
            return False
        
        else:
            return True

    def place_brick(self, brick:Brick) -> None:
        if not self.can_place_brick(brick):
            raise ValueError("Brick placement failed a placement constraint, refer to the above diagnostic information")
        else:
            grid_bounds = self.get_grid_region(brick)

            brick_id = len(self.placed_bricks)

            # Place the brick in the brick class
            brick.place_brick(brick_id)

            # Place the brick in the brick array
            self.placed_bricks.append(brick)

            # Place the brick inside the grid_bounds
            grid_bounds[:, :] = brick_id
        
        


    """  
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
            elif not self.validate_minimum_support(brick):
                raise ValueError("Brick does not meet the required threshold of " + str(self.minimum_support_ratio) + " ratio of support studs")
            else:
                brick_id = len(self.placed_bricks)

                # Place the brick in the brick class
                brick.place_brick(brick_id)

                # Place the brick in the brick array
                self.placed_bricks.append(brick)

                # Place the brick inside the grid_bounds
                grid_bounds[:, :] = brick_id
    """