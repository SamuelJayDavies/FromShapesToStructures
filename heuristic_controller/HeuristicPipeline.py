import numpy as np

from brick import Brick_vocabulary
from brick_generation import CandidateGenerationStrategy
from brick_generation.CandidateGenerator import CandidateGenerator
from brick_placement import ConstructionGrid

from brick_scoring import CandidateScorer
from brick_scoring import CandidateScore
from brick_scoring import CandidateSelector

from brick_placement import CandidatePlacementController
from brick_placement import PlacementResult

from .HeuristicController import HeuristicController
from .HeuristicResult import HeuristicResult

class HeuristicPipeline:
    
    def __init__(self, result_grid: np.ndarray, brick_vocabulary: Brick_vocabulary, generation_strategy: CandidateGenerationStrategy, minimum_support_ratio: float) -> None:
        prepared_result_grid = self._validate_result_grid(result_grid)
        self.brick_vocabulary = brick_vocabulary
        self.generation_strategy = generation_strategy
            
        self.construction_grid = ConstructionGrid(prepared_result_grid, minimum_support_ratio=minimum_support_ratio)
        
        # Neeed to make sure the copied version is being used here
        self.result_grid = self.construction_grid.result_grid
        
        self._build_components()
    
        
    def _validate_result_grid(self, result_grid: np.ndarray) -> np.ndarray:
        if not isinstance(result_grid, np.ndarray):
            raise TypeError("result_grid needs to be of type numpy array")
        
        if result_grid.ndim != 3 or any(dimension_size == 0 for dimension_size in result_grid.shape):
            raise ValueError("Result_grid must be 3-dimensional and have a non-zero size in every dimension [y,z, x]")
        
        if np.issubdtype(result_grid.dtype, np.bool_):
            return result_grid
        elif np.issubdtype(result_grid.dtype, np.number):
            
            if np.all( (result_grid == 0) | (result_grid == 1)):
                return result_grid.astype(bool)
            else:
                raise ValueError("All numbers within result_grid need to be either a 0 or 1")
        else:
            raise TypeError("Result grid needs to be either boolean values or numbers that can only be 0 or 1 (False and True respectivley)")
        
    def _build_components(self) -> None:
        self.candidate_generator = CandidateGenerator(self.brick_vocabulary, self.generation_strategy)
        
        self.candidate_scorer = CandidateScorer()
        self.candidate_selector = CandidateSelector()
        
        self.placement_controller = CandidatePlacementController(self.construction_grid, self.candidate_generator, self.candidate_scorer, self.candidate_selector)
        
        self.heuristic_controller = HeuristicController(self.placement_controller)
        
    def _create_heuristic_result(self, placement_history: list[PlacementResult]) -> HeuristicResult:
        if not placement_history:
            raise RuntimeError("There is no placement history to create a heuristic result of")
        
        final_placement_result = placement_history[-1]
        
        if final_placement_result.status == PlacementResult.STATUS_COMPLETE:
            final_status = PlacementResult.STATUS_COMPLETE
        elif final_placement_result.status == PlacementResult.STATUS_NO_VALID_CANDIDATES:
            final_status = PlacementResult.STATUS_NO_VALID_CANDIDATES
        elif final_placement_result.status == PlacementResult.STATUS_PLACED:
            final_status = HeuristicResult.STATUS_MAXIMUM_ITERATIONS_HIT
        else:
            raise RuntimeError("The final placement status is unrecongnisable")
        
        return HeuristicResult(self.construction_grid, placement_history, final_status)
        
    def create_structure(self) -> HeuristicResult:
        placement_history = self.heuristic_controller.construct_structure()
        
        return self._create_heuristic_result(placement_history)
        