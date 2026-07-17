from math import isclose
from numbers import Real 


# This is just a container class, all inputs have been pre-sanitised in the CandidateScorer.py file
class CandidateScore:
    """ Stores the contribution of each candidate-scoring criteria for an individual brick candidate
    
    Args:
        brick_efficency: Rewarding candidates that provide a larger coverage area upon placement
        support: Rewarding candidates with larger support from below
        connectivity: Rewarding candidates that bridge together multiple bricks on the layer below this
        gap_penalty: Rewarding candidates not leaving awkward spaces and gaps
    
    """

    def __init__(self, brick_efficency_score: float, support_score: float, connectivity_score: float, gap_penalty: float, total_score: float) -> None:
        
        self.brick_efficency_score = float(brick_efficency_score)
        self.support_score = float(support_score)
        self.connectivity_score = float(connectivity_score)
        self.gap_penalty = float(gap_penalty)
        self.total_score = float(total_score)
        
    def gap_avoidance_score(self) -> float:
        return 1.0 - self.gap_penalty
    
    def __repr__(self) -> str:
        return "CandidateScore(" + "brick_efficiency_score="+ str(self.brick_efficency_score) + ", support_score="+ str(self.support_score) + ", connectivity_score=" + str(self.connectivity_score) + ", gap_penalty=" + str(self.gap_penalty) + ", gap_avoidance_score=" + str(self.gap_avoidance_score()) + ", total_score=" + str(self.total_score) + ")"
    