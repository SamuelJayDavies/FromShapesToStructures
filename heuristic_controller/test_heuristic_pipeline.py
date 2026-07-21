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
        
    def test_binary_to_boolean_is_correct(self) -> None:
        integer_result_grid = np.array(
            [
                [
                    [1, 1, 0],
                    [1, 0, 0],
                ],
                [
                    [1, 0, 0],
                    [1, 0, 0],
                ]
            ],
            dtype=np.int32
        )
        
        expected_boolean_grid = np.array(
            [
                [
                    [True, True, False],
                    [True, False, False],
                ],
                [
                    [True, False, False],
                    [True, False, False]
                ]
            ],
            dtype=bool
        )
        
        pipeline = HeuristicPipeline(integer_result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
        
        self.assertEqual(pipeline.result_grid.dtype, np.dtype(bool))
        
        np.testing.assert_array_equal(pipeline.result_grid, expected_boolean_grid)
        
        self.assertIs(pipeline.result_grid, pipeline.construction_grid.result_grid)
        
    def test_incorrect_dimensional_grid_is_rejected(self) -> None:
        
        invalid_result_grid = np.array(
            [
                [True, True, False],
                [True, False, False],
            ],
            dtype=bool,
        )
        
        with self.assertRaises(ValueError):
            HeuristicPipeline(invalid_result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
            
    def test_grid_with_zero_axis_is_rejected(self) -> None:
        
        invalid_result_grid = np.empty(shape=(2, 0, 3), dtype=bool)
        
        with self.assertRaises(ValueError):
            HeuristicPipeline(invalid_result_grid, self.brick_vocabulary, CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
            
    def test_non_binary_numeric_grid_is_rejected(self) -> None:
        invalid_result_grid = np.array(
            [
                [
                    [1, 0, 2],
                    [1, 0, 0],
                ]
            ],
            dtype=np.int32,
        )

        with self.assertRaises(ValueError):
            HeuristicPipeline(
                invalid_result_grid,
                self.brick_vocabulary,
                CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC,
            )

class TestHeuristicPipelineOutcomes(unittest.TestCase):

    def setUp(self) -> None:
        self.brick_vocabulary = Brick_vocabulary(
            [
                BrickType("1x1", 1, 1),
                BrickType("1x2", 1, 2),
                BrickType("2x2", 2, 2),
            ]
        )

        self.generation_strategies = (
            CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC,
            CandidateGenerationStrategy.CandidateGenerationStrategy.INFORMED,
        )
        
    def test_empty_result_is_immediately_finished(self) -> None:
        empty_result_grid = np.zeros(
        shape=(2, 2, 3),
        dtype=bool,
    )

        for strategy in self.generation_strategies:
            with self.subTest(strategy=strategy):
                pipeline = HeuristicPipeline(
                    empty_result_grid,
                    self.brick_vocabulary,
                    strategy,
                )

                finished_structure = pipeline.create_structure()

                self.assertEqual(
                    finished_structure.final_status,
                    PlacementResult.STATUS_COMPLETE,
                )

                self.assertEqual(
                    len(finished_structure.placed_bricks),
                    0,
                )

                self.assertEqual(
                    len(finished_structure.placement_history),
                    1,
                )

                self.assertEqual(
                    finished_structure
                    .placement_history[-1]
                    .status,
                    PlacementResult.STATUS_COMPLETE,
                )

                self.assertTrue(
                    np.all(
                        finished_structure.finished_grid == -1
                    )
                )
                
    def test_unsupported_target_returns_no_valid_candidates(self) -> None:
        unsupported_result_grid = np.array(
            [
                [
                    [True, False],
                ],
                [
                    [False, True],
                ],
            ],
            dtype=bool,
        )

        expected_blocking_point = (1, 0, 1)

        for strategy in self.generation_strategies:
            with self.subTest(strategy=strategy):
                pipeline = HeuristicPipeline(
                    unsupported_result_grid,
                    self.brick_vocabulary,
                    strategy,
                )

                finished_structure = pipeline.create_structure()

                self.assertEqual(
                    finished_structure.final_status,
                    PlacementResult.STATUS_NO_VALID_CANDIDATES,
                )

                self.assertEqual(
                    finished_structure
                    .placement_history[-1]
                    .status,
                    PlacementResult.STATUS_NO_VALID_CANDIDATES,
                )

                self.assertEqual(
                    len(finished_structure.placed_bricks),
                    1,
                )