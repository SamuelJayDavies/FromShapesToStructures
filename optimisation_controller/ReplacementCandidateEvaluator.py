import numpy as np

from brick.Brick import Brick
from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolation import StructuralViolation
from optimisation_controller.ViolationCluster import ViolationCluster

class ReplacementCandidateEvaluator:
    
    def __init__(self, construction_grid: ConstructionGrid) -> None:
        self.construction_grid = construction_grid
        
    def validate_candidate_in_bounds(self, candidate_origin: tuple[int, int, int], candidate_orientation: tuple[int, int]) -> bool:
        """ Ensures the replacement brick is within the construction-grid bounds before a Brick object is officially created

        Args:
            candidate_origin (tuple[int, int, int]): The origin of the candidate 
            candidate_orientation (tuple[int, int]): The orientation of the candidate

        Returns:
            bool: True if the candidate is within the bounds of the construction grid, False otherwise
        """
        candidate_y, candidate_z, candidate_x = candidate_origin
        
        candidate_size_x = candidate_orientation[0]
        candidate_size_z = candidate_orientation[1]
        
        grid_size_y, grid_size_z, grid_size_x = self.construction_grid.result_shape
        
        if candidate_y < 0 or candidate_y >= grid_size_y:
            return False
        elif candidate_z < 0 or candidate_z + candidate_size_z > grid_size_z:
            return False
        elif candidate_x < 0 or candidate_x + candidate_size_x > grid_size_x:
            return True
        
    def validate_candidate_does_not_conflict(self, candidate: Brick, target_violation: StructuralViolation) -> bool:
        """ Ensures the replacement candidate does not overlap an occupied brick already in place

        Args:
            candidate (Brick): The brick that is being placed currently
            target_violation (StructuralViolation): The target violation of the replaced brick footprint

        Returns:
            bool: If the newly placed brick does not overlap 
        """
        if not self.construction_grid.validate_brick_in_bounds(candidate):
            return False
        else:
            candidate_region = self.construction_grid.get_grid_region(candidate)
            
            target_brick_id = target_violation.brick_id
            
            conflicting_cells = ((candidate_region != -1) and (candidate_region != target_brick_id))
            
            return not np.any(conflicting_cells)
        
    def get_support_ratio_improvement(self, candidate: Brick, target_violation: StructuralViolation) -> float:
        """ Calculates the change between the new candidate and the previous violated brick

        Args:
            candidate (Brick): The new brick being placed
            target_violation (StructuralViolation): The previous brick that violated the support constraints

        Returns:
            float: Candidate support ratio minus the original support ratio
        """
        candidate_support_ratio = self.construction_grid.calculate_support_ratio(candidate)
        
        return candidate_support_ratio - target_violation.actual_support_ratio
    
    def get_independently_grounded_attachment_brick_ids(self, candidate: Brick, cluster: ViolationCluster) -> set[int]:
        """ Returns independently grounded externel bricks that the candidate would vertically connect to. This doesn't include violation cluster brick ids to prevent circular reasoning.

        Args:
            candidate (Brick): The proposed replacement brick
            cluster (ViolationCluster): The violation cluster being repaired

        Returns:
            set[int]: IDs of independently grounded externel bricks reached by the new candidate
        """
        cluster_brick_ids = {violation.brick_id for violation in cluster.violations}
        
        adjacent_brick_ids = {self.construction_grid.get_support_bricks(candidate)}
        adjacent_brick_ids.update(self.construction_grid.get_bricks_above(candidate))
        
        
        