from brick_placement import ConstructionGrid
from brick_generation import CandidateGenerator
from brick_scoring import CandidateScorer
from brick_scoring import CandidateSelector

from .PlacementResult import PlacementResult

import numpy as np

class CandidatePlacementController:
    
    def __init__(self, construction_grid: ConstructionGrid, candidate_generator: CandidateGenerator, candidate_scorer: CandidateScorer, candidate_selector: CandidateSelector) -> None:
        self._validate_components(construction_grid, candidate_generator, candidate_scorer, candidate_selector)
        
        self.construction_grid = construction_grid
        self.candidate_generator = candidate_generator
        self.candidate_scorer = candidate_scorer
        self.candidate_selector = candidate_selector
        
    def _validate_components(self, construction_grid: ConstructionGrid, candidate_generator: CandidateGenerator, candidate_scorer: CandidateScorer, candidate_selector: CandidateSelector) -> None:
        if not isinstance(construction_grid, ConstructionGrid):
            raise TypeError("Construction grid needs to be of type ConstructionGrid")
        elif not isinstance(candidate_generator, CandidateGenerator):
            raise TypeError("Candidate generator needs to be of type CandidateGenerator")
        elif not isinstance(candidate_scorer, CandidateScorer):
            raise TypeError("Candidate scorer needs to be of type CandidateScorer")
        elif not isinstance(candidate_selector, CandidateSelector):
            raise TypeError("Candidate selector needs to be of type CandidateSelector")
        
    def _get_next_uncovered_layer(self) -> tuple[int, np.ndarray] | None:
        for y in range(self.construction_grid.result_shape[0]):
            uncovered_layer = self.construction_grid.get_uncovered_layer(y)
            
            if np.any(uncovered_layer):
                return y, uncovered_layer
        
        return None
        
    def place_next_brick(self) -> PlacementResult:
        layer_result = self._get_next_uncovered_layer()
        
        if layer_result is None:
            return PlacementResult(None, None, None, 0, status=PlacementResult.STATUS_COMPLETE)
        
        y, uncovered_layer = layer_result
        
        free_grid = np.zeros(self.construction_grid.result_shape, dtype=bool)
        
        free_grid[y] = uncovered_layer
        
        crucial_point = self.candidate_generator.find_next_crucial_point(free_grid)
        
        if crucial_point is None:
            return PlacementResult(None, None, None, 0, PlacementResult.STATUS_COMPLETE)
        
        candidates = self.candidate_generator.generate_candidates(free_grid, crucial_point)
        
        if not candidates:
            return PlacementResult(crucial_point, None, None, 0, PlacementResult.STATUS_NO_VALID_CANDIDATES)
        
        scored_candidates = self.candidate_scorer.score_current_candidates(candidates, self.construction_grid)
        
        selected_brick, selected_score = self.candidate_selector.select_best_candidate(scored_candidates)
        
        self.construction_grid.place_brick(selected_brick)
        
        return PlacementResult(crucial_point, selected_brick, selected_score, len(candidates), status=PlacementResult.STATUS_PLACED)
        
        
    