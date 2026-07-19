from math import isclose
from numbers import Real

from .CandidateScore import CandidateScore
from brick import Brick
from brick_placement import ConstructionGrid

class CandidateScorer:

    BRICK_EFFICIENCY_WEIGHT: float = 0.30
    SUPPORT_WEIGHT: float = 0.40
    CONNECTIVITY_WEIGHT: float = 0.20
    GAP_AVOIDANCE_WEIGHT: float = 0.10

    # This variable controls how many bricks that become interlocked from an above candidate placement are needed for a perfect score of 1.0
    CONNECTIVITY_SUPPORT_BOUND: float = 2.0

    # The best score a calculation method can return
    MAXIMUM_SCORE: float = 1.0

    def __init__(self) -> None:
        self.brick_efficiency_weight = self.BRICK_EFFICIENCY_WEIGHT
        self.support_weight = self.SUPPORT_WEIGHT
        self.connectivity_weight = self.CONNECTIVITY_WEIGHT
        self.gap_avoidance_weight = self.GAP_AVOIDANCE_WEIGHT

    def _validate_score_component(self, name: str, value: float) -> bool:
        if not isinstance(value, Real):
            print("Value of the score component is of the wrong type needs to be float")
            return False
        elif value < 0.0 or value > self.MAXIMUM_SCORE:
            print(name + " must be between 0 and 1 not " + str(value))
            return False
        else:
            return True
        
    def calculate_maximum_candidate_area(self, candidates: list[Brick]):
        return max(candidate.area() for candidate in candidates)
        
    def calculate_brick_efficiency_score(self, candidate: Brick, maximum_candidate_area: int) -> float:
        if not isinstance(maximum_candidate_area, int):
            raise TypeError("Maximum candidate area needs to be a integer")
        elif maximum_candidate_area < 1:
            raise ValueError("Maximum candidate area should be at least 1 stud in size")
        else:
            # This max candidate area should come from the set of valid candidates and not generally from teh vocabulary because this is distoring the score with a candidate that can never be picked
            return candidate.area() / maximum_candidate_area
        
    def calculate_support_score(self, candidate: Brick, construction_grid: ConstructionGrid) -> float:
        return construction_grid.calculate_support_ratio(candidate)
    
    def calculate_connectivity_score(self, candidate: Brick, construction_grid: ConstructionGrid) -> float:
        if candidate.y == 0:
            return self.MAXIMUM_SCORE
        else:
            supporting_bricks = construction_grid.get_support_bricks(candidate)
            # Return the min of 0 - 1.0 or if larger just return 1.0
            return min(len(supporting_bricks) / self.CONNECTIVITY_SUPPORT_BOUND, self.MAXIMUM_SCORE)
        
    def calculate_gap_penalty(self, candidate: Brick, construction_grid: ConstructionGrid) -> float:
        uncovered_before = construction_grid.get_uncovered_layer(candidate.y)
        uncovered_after = construction_grid.get_uncovered_layer_after_candidate(candidate)

        alone_before = set(construction_grid.get_alone_coordinates(uncovered_before))
        alone_after = set(construction_grid.get_alone_coordinates(uncovered_after))

        # We need to distinguish between what new alone coordinates were introduced after this coordinate was considered
        # Alternatively, if an isolated coordinate already existed, punishing the new placement for this doesn't help distinguish between candidates
        # This would now be penalising all future placements for a placement not relevant to the current one 
        new_alone_coordinates = alone_after - alone_before

        remaining_empty_cells = int(uncovered_after.sum())

        # If the candidate placement creates no new isolated coordinates or if no empty cells now exist, it gets no penalty
        if (remaining_empty_cells == 0 or not new_alone_coordinates):
            return 0.0
        else:
            gap_penalty = len(new_alone_coordinates) / remaining_empty_cells

            return gap_penalty
        
        # MENTION IN REPORT THE DOWNSIDES OF THIS METHOD, WHICH CAN BE FOUND IN CHAPTER 9


    def calculate_total_score(self, brick_efficiency_score: float, brick_support_score: float, brick_connectivity_score: float, brick_gap_penalty: float) -> float:
        # This classes scores are in relation to the brick placement and not the weights

        score_components = {"brick_efficiency_score": brick_efficiency_score, "support_score": brick_support_score, "connectivity_score": brick_connectivity_score, "gap_penalty": brick_gap_penalty}

        for name, value in score_components.items():
            if not (self._validate_score_component(name, value)):
                raise TypeError("Value of the score component has failed to validate for the above reason")
        
        gap_avoidance_score = 1.0 - float(brick_gap_penalty)

        total_score = (self.brick_efficiency_weight * float(brick_efficiency_score)
                     + self.support_weight * float(brick_support_score)
                     + self.connectivity_weight * float(brick_connectivity_score)
                     + self.gap_avoidance_weight * float(gap_avoidance_score))
        
        # In case of floating point problems
        return min(max(total_score, 0.0), self.MAXIMUM_SCORE)
    
    def create_candidate_score(self, candidate: Brick, construction_grid: ConstructionGrid, maximum_candidate_area: int) -> CandidateScore:
        brick_e_score = self.calculate_brick_efficiency_score(candidate, maximum_candidate_area)
        brick_s_score = self.calculate_support_score(candidate, construction_grid)
        brick_c_score = self.calculate_connectivity_score(candidate, construction_grid)
        brick_g_penalty = self.calculate_gap_penalty(candidate, construction_grid)
        
        total_score = self.calculate_total_score(brick_e_score, brick_s_score, brick_c_score, brick_g_penalty)

        return CandidateScore(brick_e_score, brick_s_score, brick_c_score, brick_g_penalty, total_score)


    """
    def create_candidate_score(self, brick_efficency_score: float, brick_support_score: float, brick_connectivity_score: float, brick_gap_penalty: float) -> CandidateScore:
        total_score = self.calculate_total_score(brick_efficency_score, brick_support_score, brick_connectivity_score, brick_gap_penalty)

        return CandidateScore(brick_efficency_score, brick_support_score, brick_connectivity_score, brick_gap_penalty, total_score)
    """

    def score_current_candidates(self, candidates: list[Brick], construction_grid: ConstructionGrid) -> list[tuple[Brick, CandidateScore]]:
        # This saves maximum candidate area from crashing later if so, praying it never actually happens where theres no candidates
        if not candidates:
            return []
        else:
            # also don't recalculate this, should be the same for all candidates currently
            maximum_candidate_area = self.calculate_maximum_candidate_area(candidates)

            current_scored_candidates: list[tuple[Brick, CandidateScore]] = []

            for candidate in candidates:
                candidate_score = self.create_candidate_score(candidate, construction_grid, maximum_candidate_area)
                current_scored_candidates.append([candidate, candidate_score])

            return current_scored_candidates

