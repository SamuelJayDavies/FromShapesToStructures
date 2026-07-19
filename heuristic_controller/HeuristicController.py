from brick_placement import CandidatePlacementController
from brick_placement import PlacementResult

class HeuristicController:
    
    def __init__(self, candidate_placement_controller: CandidatePlacementController) -> None:
        
        if not isinstance(candidate_placement_controller, CandidatePlacementController):
            raise TypeError("Candidate placement controller is of the wrong type")
        
        self.candidate_placement_controller = candidate_placement_controller
        self.maximum_iterations = self._calculate_maximum_iterations()
        
    # It can't possibly go any more than this maximum amount
    def _calculate_maximum_iterations(self) -> int:
        result_voxel_count = int(self.candidate_placement_controller.construction_grid.result_grid.sum())
        
        return result_voxel_count + 1
    
    def construct_structure(self) -> list[PlacementResult]:
        placement_history: list[PlacementResult] = []
        
        for _ in range(self.maximum_iterations):
            current_placement_result = self.candidate_placement_controller.place_next_brick()
            
            placement_history.append(current_placement_result)
            
            if current_placement_result.status == PlacementResult.STATUS_COMPLETE:
                return placement_history
            
            if current_placement_result.status == PlacementResult.STATUS_NO_VALID_CANDIDATES:
                return placement_history
            
            if current_placement_result.status != PlacementResult.STATUS_PLACED:
                raise RuntimeError("The status returned is unsupported")
        # If the code gets here something seriously wrong has happened
        raise RuntimeError("Maximum construction iterations reached what have you done!!!!!")
        