from brick import Brick
from brick_scoring import CandidateScore

class PlacementResult:
    
    STATUS_PLACED: str = "brick placed"
    STATUS_COMPLETE: str = "brick placement completed"
    STATUS_NO_VALID_CANDIDATES: str = "no valid bricks could be found"
    
    def __init__(self, crucial_point: tuple[int, int, int] | None, selected_brick: Brick | None, candidate_score: CandidateScore | None, candidate_count: int, status: str) -> None:
        if crucial_point is not None:
            if not isinstance(crucial_point, tuple) or len(crucial_point) != 3:
                raise TypeError("Crucial point must be a tuple containing y, z, x coordinates")
            elif any(coordinate < 0 for coordinate in crucial_point):
                raise ValueError("Crucial point coordinates cannot be negative")
        
        if status not in (self.STATUS_PLACED, self.STATUS_COMPLETE, self.STATUS_NO_VALID_CANDIDATES):
            raise ValueError("Placement status needs to be one of the valid placements statuses")
        
        self._validate_result_state(crucial_point, selected_brick, candidate_score, candidate_count, status)
        
        self.crucial_point = crucial_point
        self.selected_brick = selected_brick
        self.candidate_score = candidate_score
        self.candidate_count = candidate_count
        self.status = status
        
        
    def _validate_result_state(self, crucial_point: tuple[int, int, int] | None, selected_brick: Brick | None, candidate_score: CandidateScore | None, candidate_count: int, status: str) -> None:
        if status == self.STATUS_PLACED:
            if crucial_point is None:
                raise ValueError("Can't have a placed brick with no crucial point")
            elif selected_brick is None:
                raise ValueError("Cannot have a placed brick without the brick")
            elif candidate_score is None:
                raise ValueError("Cannot have a placed brick without its candidate score")
            elif candidate_count == 0:
                raise ValueError("Brick couldn't be placed without at least one candidate in the count")
            else:
                return
        elif selected_brick is not None:
            raise ValueError("If a brick is present it means brick placement isn't complete (STATUS_COMPLETE) or that no valid candidates are present (STATUS_N_VALID_CANDIDATES). Status should be placed")
        elif candidate_count != 0:
            raise ValueError("Placement can't be complete or failed to continue if a valid candidate is present")
        elif candidate_score is not None:
            raise ValueError("The presence of a candidate score means that placement isn't complete nor are there no valid candidates")
        elif status == self.STATUS_COMPLETE and crucial_point is not None:
            raise ValueError("Placement cannot be completed if a crucial point is still present")
        elif status == self.STATUS_NO_VALID_CANDIDATES and crucial_point is None:
            raise ValueError("No candidates being found needs to be in relation to a crucial point")
        
        else:
            return