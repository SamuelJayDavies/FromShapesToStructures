from math import isclose, isfinite
from numbers import Real

from brick import Brick
from .CandidateScore import CandidateScore

class CandidateSelector:

    # In cases where the floating point arithmetic is very low and basically neglibable 
    ABSOLUTE_SCORE_TOLERANCE: float = 1e-10

    def __init__(self) -> None:
        self.absolute_score_tolerance = float(self.ABSOLUTE_SCORE_TOLERANCE)

    def _validate_candidate_tuple(self, scored_candidates: list[tuple[Brick, CandidateScore]]) -> bool:
        for _, scored_candidate in enumerate(scored_candidates):

            if(len(scored_candidate) != 2):
                raise TypeError("Each scored candidate needs a brick entity and a CandidateScore")
            else:
                candidate_brick, candidate_score = scored_candidate
                if not isinstance(candidate_brick, Brick):
                    print("Candidate brick is not of type Brick")
                    return False
                elif not isinstance(candidate_score, CandidateScore):
                    print("Candidate score is not of type CandidateScore")
                    return False
                else:
                    return True

    # Can't use boolean here because we have three outputs to understand
    def _compare_score_values(self, new_candidate_value: float, current_best_value: float) -> int:
        if isclose(new_candidate_value, current_best_value, rel_tol=0.0, abs_tol=self.absolute_score_tolerance):
            return 0 # Values are equal
        elif new_candidate_value > current_best_value:
            return 1 # New value is better
        else:
            return -1 # Old value is better
        
    """
    The Tie Breaking order is currently
    1. The highest score
    2. The highest support score
    3. The highest gap-avoidance score
    4. The highest connectivity score
    5. The largest brick area covered
    6. The smallest candidate positions numbers
    """
    def _candidate_is_preferred(self, new_candidate: Brick, new_candidate_score: CandidateScore, current_best_candidate: Brick, current_best_score: CandidateScore) -> bool:

        tie_breaking_order = ((new_candidate_score.total_score, current_best_score.total_score), # 1.
                              (new_candidate_score.support_score, current_best_score.support_score),  # 2.
                              (new_candidate_score.gap_avoidance_score(), current_best_score.gap_avoidance_score()), # 3.
                              (new_candidate_score.connectivity_score, current_best_score.connectivity_score)) # 4.
        
        for new_candidate_value, current_best_value in tie_breaking_order:

            result = self._compare_score_values(new_candidate_value, current_best_value)

            if result > 0:
                return True
            if result < 0:
                return False
        
        # 5.
        new_candidate_area = new_candidate.area()
        current_best_area = current_best_candidate.area()

        if new_candidate_area > current_best_area:
            return True
        if new_candidate_area < current_best_area:
            return False
        
        # 6.
        new_candidate_attributes = (new_candidate.y, new_candidate.z, new_candidate.x, new_candidate.orientation[0], new_candidate.orientation[1], new_candidate.brickType.name)
        current_best_attributes = (current_best_candidate.y, current_best_candidate.z, current_best_candidate.x, current_best_candidate.orientation[0], current_best_candidate.orientation[1], current_best_candidate.brickType.name)

        return new_candidate_attributes < current_best_attributes


    def select_best_candidate(self, scored_candidates: list[tuple[Brick, CandidateScore]]) -> tuple[Brick, CandidateScore]:

        if not isinstance(scored_candidates, list):
            raise TypeError("Scored_candidates must be a list of candidates")
        elif len(scored_candidates) == 0:
            raise ValueError("There needs to be at least one scored candidate")
        elif not self._validate_candidate_tuple(scored_candidates):
            raise TypeError("The candidate tuple failed to be validated for one of the above reasons")
        else:
            best_candidate, best_candidate_score = scored_candidates[0]

            for new_candidate, new_candidate_score in scored_candidates[1:]:

                if self._candidate_is_preferred(new_candidate, new_candidate_score, best_candidate, best_candidate_score):
                    best_candidate = new_candidate
                    best_candidate_score = new_candidate_score

            return best_candidate, best_candidate_score