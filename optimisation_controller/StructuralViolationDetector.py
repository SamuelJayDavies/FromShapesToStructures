from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolation import StructuralViolation
from brick.Brick import Brick

class StructuralViolationDetector:
    """_summary_ Checks a completed structure for any bricks that violate the minimum support ratio. 
    
    The detector does not change the structure in any way, but simply detects inadequatly supported bricks and returns said list
    
    """
    
    def __init__(self, minimum_support_ratio: float) -> None:
        if not 0.0 <= float(minimum_support_ratio) <= 1.0:
            raise ValueError("minimum_support_ratio needs to be a float between 0.0 and 1.0")
        else:
            self.minimum_support_ratio = minimum_support_ratio
            
    def _get_ordered_placed_bricks(self, construction_grid: ConstructionGrid) -> list[tuple[int, Brick]]:
        
        ordered_bricks = list(enumerate(construction_grid.placed_bricks))
        # Need brick id as the last tie-breaker 
        ordered_bricks.sort(key=lambda ordered_brick: (ordered_brick[1].y, ordered_brick[1].z, ordered_brick[1].x, ordered_brick[0]))
        
        return ordered_bricks
    
    def _create_violation(self, construction_grid: ConstructionGrid, brick_id: int, brick: Brick, actual_support_ratio: float) -> StructuralViolation:
        
        footprint_coordinates = construction_grid.get_brick_footprint_coordinates(brick)
        unsupported_footprint_coordinates = construction_grid.get_unsupported_footprint_coordinates(brick)
        
        violation = StructuralViolation(brick_id, brick, footprint_coordinates, unsupported_footprint_coordinates, actual_support_ratio, self.minimum_support_ratio)
        
        return violation
    
    def detect_violations(self, construction_grid: ConstructionGrid) -> list[StructuralViolation]:
        
        violations = []
        
        ordered_bricks = self._get_ordered_placed_bricks(construction_grid)
        
        for brick_id, brick in ordered_bricks:
            if brick.y != 0:
            # else brick is on the ground layer and cannot be violating support

                actual_support_ratio = construction_grid.calculate_support_ratio(brick)
                
                if actual_support_ratio < self.minimum_support_ratio:
                    violation = self._create_violation(construction_grid, brick_id, brick, actual_support_ratio)
                    violations.append(violation)
                # else: no violation, brick is adequately supported
        return violations
            