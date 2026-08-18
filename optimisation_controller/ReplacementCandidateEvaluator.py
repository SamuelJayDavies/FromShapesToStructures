import numpy as np

from brick.Brick import Brick
from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolation import StructuralViolation
from optimisation_controller.ViolationCluster import ViolationCluster

import numpy as np

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
            return False
        else:
            return True
        
    def validate_candidate_does_not_conflict_with_ignored_bricks(self, candidate: Brick, ignored_brick_ids: set[int]) -> bool:
        
        if not self.construction_grid.validate_brick_in_bounds(candidate):
            return False
        else:
            candidate_region = self.construction_grid.get_grid_region(candidate)
            
            occupied_brick_ids = {int(brick_id) for brick_id in np.unique(candidate_region) if brick_id != -1}
            
            conflicting_brick_ids = occupied_brick_ids - ignored_brick_ids
            
            return len(conflicting_brick_ids) == 0
                
    def validate_candidate_does_not_conflict(self, candidate: Brick, target_violation: StructuralViolation) -> bool:
        """ Ensures the replacement candidate does not overlap an occupied brick already in place

        Args:
            candidate (Brick): The brick that is being placed currently
            target_violation (StructuralViolation): The target violation of the replaced brick footprint

        Returns:
            bool: If the newly placed brick does not overlap 
        """
        return self.validate_candidate_does_not_conflict_with_ignored_bricks(candidate, {target_violation.brick_id})
    
    def validate_merge_candidate_does_not_conflict(self, candidate: Brick, target_brick_id: int, neighbour_brick_id: int) -> bool:
        
        if target_brick_id == neighbour_brick_id:
            raise ValueError("A merge needs two differnet brick ids")
        else:
            return self.validate_candidate_does_not_conflict_with_ignored_bricks(candidate, ignored_brick_ids={target_brick_id, neighbour_brick_id})
        
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
        
        adjacent_brick_ids = (self.construction_grid.get_support_bricks(candidate))
        adjacent_brick_ids.update(self.construction_grid.get_bricks_above(candidate))
        
        external_adjacent_brick_ids = (adjacent_brick_ids - cluster_brick_ids)
        
        independently_grounded_brick_ids = set(self.construction_grid.get_grounded_brick_ids(cluster_brick_ids))
        
        return (external_adjacent_brick_ids & independently_grounded_brick_ids)
    
    def get_independent_grounded_attachment_count(self, candidate: Brick, cluster: ViolationCluster) -> int:
        return len(self.get_independently_grounded_attachment_brick_ids(candidate, cluster))
    
    def get_outside_target_coordinates(self, candidate: Brick) -> list[tuple[int, int, int]]:
        """ Return candidate footprint coordinates that are outside the target model

        Args:
            candidate (Brick): The proposed new placement brick

        Returns:
            list[tuple[int, int, int]]: Candidate coordinates whose corresponding result_grid value is False
        """
        if not self.construction_grid.validate_brick_in_bounds(candidate):
            raise ValueError("Brick is not in-bounds")
        
        footprint_coordinates = self.construction_grid.get_brick_footprint_coordinates(candidate)
        
        outside_target_coordinates: list[tuple[int, int, int]] = []
        
        for coordinate in footprint_coordinates:
            
            current_y, current_z, current_x = coordinate
            
            if not self.construction_grid.result_grid[current_y, current_z, current_x]:
                outside_target_coordinates.append(coordinate)
        
        return outside_target_coordinates
    
    def get_outside_target_coordinate_count(self, candidate: Brick) -> int:
        """ Return the number of candidate footprint cells outside the target model

        Args:
            candidate (Brick): The proposed replacement brick

        Returns:
            int: Number of outside-target cells made by the new candidate
        """
        return len(self.get_outside_target_coordinates(candidate))
    
    def has_structural_improvement(self, support_ratio_improvement: float, independent_attachment_count: int) -> bool:
        """ Returns True if the support ratio is greater than zero or the attachment count is

        Args:
            support_ratio_improvement (float): The new support ratio improvement 
            independent_attachment_count (int): The amount of independent attachments

        Returns:
            bool: True if support ratio is greater than zero or attachment count is greater than zero
        """
        return support_ratio_improvement > 0.0 or independent_attachment_count > 0
    
    # SORT THESE METHODS BELOW, THEY ARE PRETTY POORLY WRITTEN
    
    def is_candidate_better(self, candidate: Brick, candidate_support_improvement: float, candidate_attachment_count: int, candidate_outside_target_count: int, current_best: Brick, current_best_support_improvement: float, current_best_attachment_count: int, current_best_outside_target_area: int) -> bool:
        
        candidate_has_grounded_attachment = candidate_attachment_count > 0
        current_best_has_grounded_attachment = current_best_attachment_count > 0
        
        # Criteria 1: Better grounding
        if candidate_has_grounded_attachment != current_best_has_grounded_attachment:
            return candidate_has_grounded_attachment
        elif candidate_support_improvement != current_best_support_improvement:
            return candidate_support_improvement > current_best_support_improvement
        elif candidate_attachment_count != current_best_attachment_count:
            return candidate_attachment_count > current_best_attachment_count
        elif candidate_outside_target_count != current_best_outside_target_area:
            return candidate_outside_target_count < current_best_outside_target_area
        elif candidate.area() != current_best.area():
            return candidate.area() < current_best.area()
        elif candidate.brickType.name != current_best.brickType.name:
            return candidate.brickType.name < current_best.brickType.name
        elif candidate.orientation != current_best.orientation:
            return candidate.orientation < current_best.orientation
        else:
            candidate_position = (candidate.y, candidate.z, candidate.x)
            current_best_position = (current_best.y, current_best.z, current_best.x)
            
            return candidate_position < current_best_position
        
    def select_best_candidate(self, candidate_evaluations: list[tuple[Brick, float, int, int]]) -> Brick | None:
        """ Selects the best structural beneficial replacement candidate

        Args:
            candidate_evaluation (list[tuple[Brick, float, int, int]]): Each evaluation contains the candidate: Brick, the support ratio improvement: float, the grounded attachment count: int and the outside target coordinate count: int

        Returns:
            Brick | None: The structural beneficial 
        """
        
        best_candidate: Brick | None = None
        best_support_improvement = 0
        best_attachment_count = 0
        best_outside_target_count = 0
        
        for evaluation in candidate_evaluations:
            candidate_has_potential = self.has_structural_improvement(support_ratio_improvement=evaluation[1], independent_attachment_count=evaluation[2])
            
            if candidate_has_potential:
                if best_candidate is None:
                    best_candidate = evaluation[0]
                    best_support_improvement = evaluation[1]
                    best_attachment_count = evaluation[2]
                    best_outside_target_count = evaluation[3]
                else:
                    candidate_is_better = self.is_candidate_better(candidate=evaluation[0], candidate_support_improvement=evaluation[1], candidate_attachment_count=evaluation[2], candidate_outside_target_count=evaluation[3], 
                                                                   current_best=best_candidate, current_best_support_improvement=best_support_improvement, current_best_attachment_count=best_attachment_count, current_best_outside_target_area=best_outside_target_count)
                    
                    if candidate_is_better:
                        best_candidate = evaluation[0]
                        best_support_improvement = evaluation[1]
                        best_attachment_count = evaluation[2]
                        best_outside_target_count = evaluation[3]
                        
        return best_candidate
    
    def evaluate_candidate(self, candidate: Brick, target_violation: StructuralViolation, cluster: ViolationCluster) -> tuple[Brick, float, int, int] | None:
        """ Validates and evaluates a replacement candidate

        Args:
            candidate (Brick): The new brick being placed
            target_violation (StructuralViolation): The violation the brick is replacing
            cluster (ViolationCluster): The cluster the target violation is from

        Returns:
            tuple[Brick, float, int, int] | None: Returns the candidate brick: Brick, the support ratio improvement: float, the independent attachment count: int, and the outside target coordinate count: int. 
            Alternatively, will return None if hte candidate is not valid
        """
        candidate_is_valid = self.validate_candidate_does_not_conflict(candidate, target_violation)
        
        if not candidate_is_valid:
            return None
        else:
            support_ratio_improvement = self.get_support_ratio_improvement(candidate, target_violation)
            independent_attachment_count = self.get_independent_grounded_attachment_count(candidate, cluster)
            outside_target_coordinate_count = self.get_outside_target_coordinate_count(candidate)
            
            return candidate, support_ratio_improvement, independent_attachment_count, outside_target_coordinate_count
        
    def evaluate_all_candidates(self, candidates: list[Brick], target_violation: StructuralViolation, cluster: ViolationCluster) -> Brick | None:
        
        candidate_evaluations: list[tuple[Brick, float, int, int]] = []
        
        for candidate in candidates:
            evaluation = self.evaluate_candidate(candidate, target_violation, cluster)
            
            if evaluation is not None:
                candidate_evaluations.append(evaluation)
        
        return self.select_best_candidate(candidate_evaluations)
    
    
    # Merge Stuff
    def get_merge_support_ratio(self, candidate: Brick) -> float:
        return self.construction_grid.calculate_support_ratio(candidate)
    
    def get_target_gained_merge_support(self, candidate: Brick, target_violation: StructuralViolation) -> float:
        """ Returns the support gained by the weak target brick when it becomes part of a larger merged structural brick

        Args:
            candidate (Brick): The new brick it has merged into 
            target_violation (StructuralViolation): The original target violation the brick was a part of

        Returns:
            float: The new support ratio
        """
        merged_support_ratio = self.get_merge_support_ratio(candidate)
        
        return (merged_support_ratio - target_violation.actual_support_ratio)
    
    def evaluate_merge_candidate(self, candidate: Brick, target_brick_id: int, neighbour_brick_id: int, target_violation: StructuralViolation, cluster: ViolationCluster) -> tuple[Brick, int, int, float, float, int] | None:
        candidate_is_valid = self.validate_merge_candidate_does_not_conflict(candidate, target_brick_id, neighbour_brick_id)
        
        if not candidate_is_valid:
            return None
        
        merged_support_ratio = self.get_merge_support_ratio(candidate)
        
        target_support_gain = self.get_target_gained_merge_support(candidate, target_violation)
        
        independent_attachment_count = self.get_independent_grounded_attachment_count(candidate, cluster)
        
        return (candidate, target_brick_id, neighbour_brick_id, merged_support_ratio, target_support_gain, independent_attachment_count)
    
    def evaluate_all_merge_candidates(self, merge_candidates: list[tuple[Brick, int, int]], target_violation: StructuralViolation, cluster: ViolationCluster) -> list[tuple[Brick, int, int, float, float, int]]:
        
        candidate_evaluations: list[tuple[Brick, int, int, float, float, int]] = []
        
        for candidate, target_brick_id, neighbour_brick_id in merge_candidates:
            
            evaluation = self.evaluate_merge_candidate(candidate, target_brick_id, neighbour_brick_id, target_violation, cluster)
            
            if evaluation is not None:
                candidate_evaluations.append(evaluation)
        
        return candidate_evaluations
    
    def is_merge_candidate_better(self, candidate_evaluation: tuple[Brick, int, int, float, float, int], current_best_evaluation: tuple[Brick, int, int, float, float, int]) -> bool:
        
        candidate, _, candidate_neighbour_id, candidate_support_ratio, _, candidate_attachment_count = candidate_evaluation
        
        current_best, _, current_best_neighbour_id, current_best_support_ratio, _, current_best_attachment_count = current_best_evaluation
        
        candidate_has_grounded_attachment = candidate_attachment_count > 0
        
        current_best_has_grounded_attachment = current_best_attachment_count > 0
        
        if (candidate_has_grounded_attachment != current_best_has_grounded_attachment):
            return candidate_has_grounded_attachment
        elif candidate_support_ratio != current_best_support_ratio:
            return candidate_support_ratio > current_best_support_ratio
        elif candidate_attachment_count != current_best_attachment_count:
            return candidate_attachment_count > current_best_attachment_count
        elif candidate.area() != current_best.area():
            return candidate.area() < current_best.area()
        elif candidate.brickType.name != current_best.brickType.name:
            return candidate.brickType.name < current_best.brickType.name
        elif candidate.orientation != current_best.orientation:
            return candidate.orientation < current_best.orientation
        else:
            candidate_position = (candidate.y, candidate.z, candidate.x)
            current_best_position = (current_best.y, current_best.z, current_best.x)
            
            if candidate_position != current_best_position:
                return candidate_position < current_best_position
            else:
                return candidate_neighbour_id < current_best_neighbour_id
            
    def select_best_merge_candidate(self, merge_evaluations: list[tuple[Brick, int, int, float, float, int]]) -> tuple[Brick, int, int, float, float, int] | None:
        
        if not merge_evaluations:
            return None
        else:
            best_evaluation = merge_evaluations[0]
            
            for evaluation in merge_evaluations[1:]:
                if self.is_merge_candidate_better(evaluation, best_evaluation):
                    best_evaluation = evaluation
            
            return best_evaluation