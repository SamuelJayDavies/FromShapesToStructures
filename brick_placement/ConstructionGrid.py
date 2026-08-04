from numbers import Real

import numpy as np

from brick import Brick

class ConstructionGrid:
    def __init__(self, result_grid: np.ndarray, minimum_support_ratio: float = 0.5, force_support: bool = True) -> None:

        # Validation Checks
        if result_grid.ndim != 3:
            raise ValueError("Result Grid must be 3-dimensions of shape (y,z,x).")
        if minimum_support_ratio < 0.0 or minimum_support_ratio > 1.0:
            raise ValueError("Minimum support ratio must be a float between 0.0 and 1.0")

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
        self.force_support = force_support

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
        
    # NEW METHod for OPTIMISATION 
    def validate_support(self, brick:Brick) -> bool:

        # Now under the relaxed constraints a brick can pass without having to be connected or supported until later
        if not self.force_support:
            return True
        # 5. The brick is connected to the ground or a block on a lower level of the y-axis 
        elif not self.validate_brick_is_connected(brick):
            return False
        elif not self.validate_minimum_support(brick):
            return False
        else:
            return True
        
    def get_support_bricks(self, brick: Brick) -> set[int]:
        """ Utility method to be used in-junction with connectivity score by identifying how many different bricks are being supported below a candidate brick placement """
        if brick.y == 0:
            return set()
        else:
            support_region = self.get_supported_region(brick)

            support_brick_ids = support_region[support_region != -1]

            num_of_support_bricks = set()
            for brick_id in np.unique(support_brick_ids):
                num_of_support_bricks.add(int(brick_id))

            return num_of_support_bricks
        
    def get_uncovered_layer(self, y: int) -> np.ndarray:
        """ Compares against the result layer and the current occupied current grid to return what positions need to be covered and which are currently uncovered
        
        Args:
            y: the y-coordinate of the layer that is being returned
            
        Returns;
            An array with the same shape as the current_grid with True positions needing to be filled, and the False positions not needing to be filled or already occupied"""
        if y < 0 or y >= self.result_shape[0]:
            raise TypeError("Layer coordinate y is outside of the construction grid")
        
        result_layer = self.result_grid[y]
        # Will make empty positions be False and occupied positions True
        current_layer = self.current_grid[y] != -1

        # A bit of fancy code that reverses the Boolean current-layer mask, so occupied becomes False and Empty becomes True
        # This is needed because current_layer has empty positions currently as False
        return result_layer & ~current_layer
    
    def get_uncovered_layer_after_candidate(self, candidate: Brick) -> np.ndarray:
        """ Returns a particular z and x layer showing which coordinates are still empty after a candidate placement"""
        if not self.validate_brick_in_bounds(candidate):
            raise ValueError("Candidate cannot be placed outside of the result grid")
        else:
            uncovered_layer = self.get_uncovered_layer(candidate.y).copy()

            _, z_start, z_end, x_start, x_end = self.get_brick_bounds(candidate)

            # This array is a 2D array because the result of .get_uncovered_layer already had the y-axis
            # This will replace the bricks bounds with False in the uncovered_layer as they no longer need to be filled
            # This is the only conclusion because the method beforehand would've eliminated positions that were not part of the original result layer (explemplar model)
            uncovered_layer[z_start:z_end, x_start:x_end] = False

            return uncovered_layer

    def get_alone_coordinates(self, uncovered_layer: np.ndarray) -> set[tuple[int, int]]:
        """ Identifies coordinates within an uncovered_layer that are isolated and don't have any empty neighbours or partners, a crucial aspect in scoring awkward placements
        
        Args:
            uncovered_layer: a 2-dimension layer from a singular y-plane that has True values as unoccupied positions needing a brick and False as already occupied or outside of the exemplar model
            
        Returns:
            A set of z,x coordinates that point to singular gaps within an uncovered_layer"""
        if uncovered_layer.ndim != 2:
            raise ValueError("Uncovered layer needs to come from an individual y-layer and should be 2-dimensional")
        else:
            # An array of coordinates that point to akwkward gaps in the structure
            gap_coordinates: set[tuple[int, int]] = set()

            neighbour_shifts = (-1, 0), (1,0), (0,-1), (0,1)

            layer_size_z, layer_size_x = uncovered_layer.shape

            # Only check coordinates where the cell may be alone (empty and alone)
            for z, x in np.argwhere(uncovered_layer):
                has_empty_neighbour = False

                for z_shift, x_shift in neighbour_shifts:
                    neighbour_z = z + z_shift
                    neighbour_x = x + x_shift

                    if (0 <= neighbour_z < layer_size_z) and (0 <= neighbour_x < layer_size_x) and uncovered_layer[neighbour_z, neighbour_x]: # If the position needs to be filled
                        has_empty_neighbour = True
                        break
                # We have already checked cooridnates that are empty, so if we don't find a neighbour that is also empty, this is a singular alone coordinate
                # If they have a neighbour they aren't a problem
                if not has_empty_neighbour:
                    gap_coordinates.add((z,x))
            
            return gap_coordinates
                    


        
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
        # 5, 6. The brick has the minimum required level of support to remain stable
        elif not self.validate_support(brick):
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