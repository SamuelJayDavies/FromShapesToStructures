import math
from numbers import Integral, Real

from brick.Brick import Brick

class StructuralViolation:
    
    MATHS_ROUNDING = 1e-10
    
    def __init__(self, brick_id: int, brick: Brick, footprint_coordinates: list[tuple[int, int, int]], unsupported_footprint_coordinates: list[tuple[int, int, int]], actual_support_ratio: float, minimum_support_ratio: float) -> None:
        if brick_id < 0:
            raise ValueError("brick_id needs to be a non-negative integer")
        elif not 0.0 <= float(actual_support_ratio) <= 1.0:
            raise ValueError("actual_support_ratio needs to be a float between 0.0 and 1.0")
        else:
            self.validate_coordinates(footprint_coordinates, brick)
            # This might fail here if there is no unsupported footprint coordinate
            self.validate_coordinates(unsupported_footprint_coordinates, brick)

            footprint_coordinates_set = set(footprint_coordinates)
            unsupported_footprint_coordinates_set = set(unsupported_footprint_coordinates)
            
            if not unsupported_footprint_coordinates_set.issubset(footprint_coordinates_set):
                raise ValueError("unsupported_footprint_coordinates must be from the footprint_coordinate set")
            
            if actual_support_ratio >= minimum_support_ratio:
                raise ValueError("brick cannot be violating support if it has an adequate support ratio")
            
            total_footprint_coordinates_count = len(footprint_coordinates)
            unsupported_footprint_coordinates_count = len(unsupported_footprint_coordinates)
            
            supported_footprint_coordinates_count = total_footprint_coordinates_count - unsupported_footprint_coordinates_count
            
            cooridinates_support_ratio = supported_footprint_coordinates_count / total_footprint_coordinates_count  
            
            if not math.isclose(cooridinates_support_ratio, actual_support_ratio, rel_tol=0.0, abs_tol=self.MATHS_ROUNDING):
                raise ValueError("actual_support_ratio does not match footprint of the brick")
            
            self.brick_id = brick_id
            self.brick = brick
            self.layer = brick.y
            self.footprint_coordinates = tuple(footprint_coordinates)
            self.unsupported_footprint_coordinates = tuple(unsupported_footprint_coordinates)
            self.total_footprint_coordinates_count = total_footprint_coordinates_count
            self.supported_footprint_coordinates_count = supported_footprint_coordinates_count
            self.unsupported_footprint_coordinates_count = unsupported_footprint_coordinates_count
            self.actual_support_ratio = actual_support_ratio
            self.minimum_support_ratio = minimum_support_ratio
            
            self.support_diff = self.minimum_support_ratio - self.actual_support_ratio
            
    def validate_coordinates(self, coordinates: list[tuple[int, int, int]], brick: Brick) -> None:
        for coordinate in coordinates:
            if len(coordinate) != 3:
                raise ValueError("coordinates needs to be a list of tuples of length 3")
            elif coordinate[0] != brick.y:
                raise ValueError("coordinates must be on the same y-plane as the brick")
            else:
                for value in coordinate:
                    if value < 0:
                        raise ValueError("coordinates needs to be a list of tuples of non-negative integers")
                    
    
    def __repr__(self) -> str:
        return ("StructuralViolation(brick_id " + str(self.brick_id) + ", brick " + str(self.brick) + ", layer " + str(self.layer) + ", footprint_coordinates " + str(self.footprint_coordinates) + ", unsupported_footprint_coordinates " + str(self.unsupported_footprint_coordinates) + ", total_footprint_coordinates " + str(self.total_footprint_coordinates) + ", supported_footprint_coordinates " + str(self.supported_footprint_coordinates) + ", actual_support_ratio " + str(self.actual_support_ratio) + ", minimum_support_ratio " + str(self.minimum_support_ratio) + ")")
    