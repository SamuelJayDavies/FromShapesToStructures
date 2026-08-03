from brick_placement import CandidatePlacementController
from brick_placement import PlacementResult

class HeuristicController:
    
    def __init__(self, candidate_placement_controller: CandidatePlacementController, defer_blocked_points: bool = False) -> None:
        
        if not isinstance(candidate_placement_controller, CandidatePlacementController):
            raise TypeError("Candidate placement controller is of the wrong type")
        
        self.candidate_placement_controller = candidate_placement_controller
        self.defer_blocked_points = defer_blocked_points
        self.maximum_iterations = self._calculate_maximum_iterations()
        
    # It can't possibly go any more than this maximum amount
    def _calculate_maximum_iterations(self) -> int:
        result_voxel_count = int(self.candidate_placement_controller.construction_grid.result_grid.sum())
        
        return result_voxel_count + 1
    
    def construct_structure(self) -> list[PlacementResult]:
        placement_history: list[PlacementResult] = []
        
        deferred_points: set[tuple[int, int, int]] = set()
        
        first_deferred_result: PlacementResult | None = None
        
        successful_placement_count = 0
        
        while successful_placement_count < self.maximum_iterations:
            
            excluded_points = deferred_points if self.defer_blocked_points else None
            current_placement_result = self.candidate_placement_controller.place_next_brick(excluded_points)
            
            
            if current_placement_result.status == PlacementResult.STATUS_COMPLETE:
                placement_history.append(current_placement_result)
                return placement_history
            
            if current_placement_result.status == PlacementResult.STATUS_PLACED:
                placement_history.append(current_placement_result)
                
                successful_placement_count += 1
                
                # If we have placed a brick, the environment has changed so these may no longer be blocked
                deferred_points.clear()
                first_deferred_result = None
                
            
            if current_placement_result.status == PlacementResult.STATUS_NO_VALID_CANDIDATES:
                if not self.defer_blocked_points:
                    placement_history.append(current_placement_result)
                    return placement_history
                
                # A point could not be covered, but my be able to be covered later, so sav it for alter if one isn't already there
                if current_placement_result.crucial_point is not None:
                    if first_deferred_result is None:
                        first_deferred_result = current_placement_result
                        
                        deferred_points.add(current_placement_result.crucial_point)
                        
                        continue
                
                # The layer has not been finished, but there are no valid candidates left
                if first_deferred_result is not None:
                    placement_history.append(first_deferred_result)
                else:
                    placement_history.append(current_placement_result)
                    
                return placement_history
            
            if current_placement_result.status != PlacementResult.STATUS_PLACED:
                raise RuntimeError("The status returned is unsupported")
        # If the code gets here something seriously wrong has happened
        raise RuntimeError("Maximum construction iterations reached what have you done!!!!!")
        