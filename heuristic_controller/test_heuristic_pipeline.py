import unittest

import numpy as np

from brick import BrickType
from brick import Brick_vocabulary
from brick_generation import CandidateGenerationStrategy

from brick_placement import PlacementResult

from .HeuristicPipeline import HeuristicPipeline

class TestHeuristicPipelineInitialisation(unittest.TestCase):
    
    def setUp(self) -> None:
        self.result_grid = np.array(
            [
                [
                    [True, True, True],
                    [True, True, True],
                ],
                [
                    [True, True, True],
                    [True, True, True]
                ],
            ],
            dtype=bool
        )
        
        self.brick_vocabulary = Brick_vocabulary(
            [
                BrickType("1x1", 1, 1),
                BrickType("1x2", 1, 2),
                BrickType("2x2", 2, 2),
            ]
        )
        
    def test_initialisation_does_not_place_bricks(self) -> None:
        pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
        
        self.assertEqual(len(pipeline.construction_grid.placed_bricks), 0)
        
        self.assertTrue(np.all(pipeline.construction_grid.current_grid == -1))
        
    def test_result_grid_is_moved_without_changes(self) -> None:
        pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
        
        self.assertEqual(pipeline.result_grid.shape, self.result_grid.shape)
        self.assertEqual(pipeline.result_grid.dtype, np.dtype(bool))
        np.testing.assert_array_equal(pipeline.result_grid, self.result_grid)
    
    def test_construction_grid_has_correct_result_copy(self) -> None:
        pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
        
        original_value = bool(pipeline.result_grid[0,0,0])
        
        self.result_grid[0,0,0] = False
        
        self.assertEqual(bool(pipeline.result_grid[0,0,0]), original_value)
        self.assertIs(pipeline.result_grid, pipeline.construction_grid.result_grid)
        
class TestHeuristicPipelineConstruction(unittest.TestCase):
    
    def setUp(self) -> None:
        self.result_grid = np.array(
            [
                [
                    [True, True, True],
                    [True, True, True],
                ],
                [
                    [True, True, True],
                    [True, True, True]
                ]
            ],
            dtype=bool
        )
        
        self.brick_vocabulary = Brick_vocabulary(
            [
                BrickType("1x1", 1,1),
                BrickType("1x2", 1, 2),
                BrickType("2x2", 2, 2)
            ]
        )
        
        self.generation_strategies = (
            CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC,
            CandidateGenerationStrategy.CandidateGenerationStrategy.INFORMED
        )
        
    def test_successful_construction_for_both_strategies(self) -> None:
        for strategy in self.generation_strategies:
            with self.subTest(strategy=strategy):
                pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, strategy)

                result = pipeline.create_structure()

                self.assertEqual(result.final_status, PlacementResult.STATUS_COMPLETE)

                self.assertEqual(result.placement_history[-1].status, PlacementResult.STATUS_COMPLETE)

                self.assertGreater(len(result.placed_bricks), 0)
                
    def test_final_grid_matches_result_grid(self) -> None:
        for strategy in self.generation_strategies:
            with self.subTest(strategy):
                pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, strategy)
                
                finished_structure = pipeline.create_structure()
                
                # Only the parts of the grid that are occupied
                final_grid = finished_structure.finished_grid != -1
                
                np.testing.assert_array_equal(final_grid, finished_structure.result_grid)
                
    def test_consistency_with_ids_and_placement_history(self) -> None:
        for strategy in self.generation_strategies:
            with self.subTest(strategy):
                pipeline = HeuristicPipeline(self.result_grid, self.brick_vocabulary, strategy)
                
                finished_structure = pipeline.create_structure()
                
                placed_results = [placement_result for placement_result in finished_structure.placement_history if (placement_result.status == PlacementResult.STATUS_PLACED)]
                
                self.assertEqual(len(placed_results), len(finished_structure.placed_bricks))
                
                for expected_id, brick in enumerate(finished_structure.placed_bricks):
                    self.assertEqual(brick.brick_id, expected_id)
                    
                for placement_result, placed_brick in zip(placed_results, finished_structure.placed_bricks):
                    self.assertIs(placement_result.selected_brick, placed_brick)
                
class TestHeuristicPipelineValidation(unittest.TestCase):
    
    def setUp(self) -> None:
        self.brick_vocabulary = Brick_vocabulary(
            [
                BrickType("1x1", 1, 1),
                BrickType("1x2", 1, 2),
                BrickType("2x2", 2, 2)
            ]
        )
        
    