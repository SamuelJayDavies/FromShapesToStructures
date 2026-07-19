import numpy as np

from brick import BrickType
from brick import Brick_vocabulary
from brick_placement import ConstructionGrid
from brick_generation import CandidateGenerator
from brick_scoring import CandidateScorer
from brick_scoring import CandidateSelector
from brick_generation import CandidateGenerationStrategy

from .CandidatePlacementController import CandidatePlacementController
from .PlacementResult import PlacementResult


def create_test_coordinator(
    search_strategy: str,
) -> tuple[CandidatePlacementController, ConstructionGrid, CandidateGenerator]:
    result_grid = np.ones(
        shape=(1, 2, 3),
        dtype=bool,
    )

    construction_grid = ConstructionGrid(result_grid)

    brick_vocabulary = Brick_vocabulary(
        [
            BrickType("1x1", 1, 1),
            BrickType("1x2", 1, 2),
        ]
    )

    candidate_generator = CandidateGenerator(
        brick_vocabulary=brick_vocabulary,
        search_strategy=search_strategy,
    )

    coordinator = CandidatePlacementController(
        construction_grid=construction_grid,
        candidate_generator=candidate_generator,
        candidate_scorer=CandidateScorer(),
        candidate_selector=CandidateSelector(),
    )

    return coordinator, construction_grid, candidate_generator

def capture_generated_candidates(
    candidate_generator: CandidateGenerator,
) -> list:
    captured_candidates = []

    original_generate_candidates = (
        candidate_generator.generate_candidates
    )

    def wrapped_generate_candidates(*args, **kwargs):
        candidates = original_generate_candidates(*args, **kwargs)
        captured_candidates.extend(candidates)
        return candidates

    candidate_generator.generate_candidates = (
        wrapped_generate_candidates
    )

    return captured_candidates

def test_successful_candidate_placement(
    search_strategy: str,
) -> None:
    coordinator, construction_grid, candidate_generator = (
        create_test_coordinator(search_strategy)
    )

    generated_candidates = capture_generated_candidates(
        candidate_generator
    )

    result = coordinator.place_next_brick()

    assert result.status == PlacementResult.STATUS_PLACED

    assert result.crucial_point == (0, 0, 0)

    assert len(generated_candidates) > 1
    assert result.candidate_count == len(generated_candidates)

    assert result.selected_brick is not None
    assert result.candidate_score is not None

    assert result.selected_brick.is_placed()
    assert result.selected_brick.brick_id == 0

    assert len(construction_grid.placed_bricks) == 1
    assert construction_grid.placed_bricks[0] is result.selected_brick

    placed_coordinates = (
        construction_grid.current_grid
        == result.selected_brick.brick_id
    )

    assert np.any(placed_coordinates)

    for candidate in generated_candidates:
        if candidate is not result.selected_brick:
            assert not candidate.is_placed()
            assert candidate.brick_id is None

    placed_layer_y = result.crucial_point[0]

    uncovered_layer = construction_grid.get_uncovered_layer(
        placed_layer_y
    )

    assert np.any(uncovered_layer)

    print(
        "Passed: test_successful_candidate_placement "
        f"({search_strategy})"
    )
    
def create_single_voxel_coordinator(
    search_strategy: str,
) -> tuple[
    CandidatePlacementController,
    ConstructionGrid,
    CandidateGenerator,
]:
    result_grid = np.ones(
        shape=(1, 1, 1),
        dtype=bool,
    )

    construction_grid = ConstructionGrid(result_grid)

    brick_vocabulary = Brick_vocabulary(
        [
            BrickType("1x1", 1, 1),
        ]
    )

    candidate_generator = CandidateGenerator(
        brick_vocabulary=brick_vocabulary,
        search_strategy=search_strategy,
    )

    coordinator = CandidatePlacementController(
        construction_grid=construction_grid,
        candidate_generator=candidate_generator,
        candidate_scorer=CandidateScorer(),
        candidate_selector=CandidateSelector(),
    )

    return coordinator, construction_grid, candidate_generator

def test_completed_construction(
    search_strategy: str,
) -> None:
    coordinator, construction_grid, _ = (
        create_single_voxel_coordinator(search_strategy)
    )

    first_result = coordinator.place_next_brick()

    assert first_result.status == PlacementResult.STATUS_PLACED
    assert len(construction_grid.placed_bricks) == 1

    grid_before_complete_call = (
        construction_grid.current_grid.copy()
    )

    placed_brick_count = len(
        construction_grid.placed_bricks
    )

    complete_result = coordinator.place_next_brick()

    assert (
        complete_result.status
        == PlacementResult.STATUS_COMPLETE
    )

    assert complete_result.crucial_point is None
    assert complete_result.selected_brick is None
    assert complete_result.candidate_score is None
    assert complete_result.candidate_count == 0

    assert np.array_equal(
        construction_grid.current_grid,
        grid_before_complete_call,
    )

    assert (
        len(construction_grid.placed_bricks)
        == placed_brick_count
    )

    print(
        "Passed: test_completed_construction "
        f"({search_strategy})"
    )
    
def test_no_valid_candidates(
    search_strategy: str,
) -> None:
    coordinator, construction_grid, candidate_generator = (
        create_test_coordinator(search_strategy)
    )

    grid_before_iteration = (
        construction_grid.current_grid.copy()
    )

    placed_brick_count = len(
        construction_grid.placed_bricks
    )

    def return_no_candidates(*args, **kwargs):
        return []

    candidate_generator.generate_candidates = (
        return_no_candidates
    )

    result = coordinator.place_next_brick()

    assert (
        result.status
        == PlacementResult.STATUS_NO_VALID_CANDIDATES
    )

    assert result.crucial_point == (0, 0, 0)
    assert result.selected_brick is None
    assert result.candidate_score is None
    assert result.candidate_count == 0

    assert np.array_equal(
        construction_grid.current_grid,
        grid_before_iteration,
    )

    assert (
        len(construction_grid.placed_bricks)
        == placed_brick_count
    )

    print(
        "Passed: test_no_valid_candidates "
        f"({search_strategy})"
    )
    
def run_candidate_placement_tests() -> None:
    basic_strategy = (
        CandidateGenerationStrategy
        .CandidateGenerationStrategy
        .BASIC
    )

    informed_strategy = (
        CandidateGenerationStrategy
        .CandidateGenerationStrategy
        .INFORMED
    )

    test_successful_candidate_placement(
        basic_strategy
    )

    test_successful_candidate_placement(
        informed_strategy
    )

    test_completed_construction(
        basic_strategy
    )

    test_completed_construction(
        informed_strategy
    )

    test_no_valid_candidates(
        basic_strategy
    )

    test_no_valid_candidates(
        informed_strategy
    )

    print()
    print(
        "All candidate-placement verification tests passed."
    )


if __name__ == "__main__":
    run_candidate_placement_tests()
    
def run_successful_placement_tests() -> None:
    test_successful_candidate_placement(CandidateGenerationStrategy.CandidateGenerationStrategy.BASIC)
    test_successful_candidate_placement(CandidateGenerationStrategy.CandidateGenerationStrategy.INFORMED)

    print()
    print("Successful placement verification tests passed.")


if __name__ == "__main__":
    run_successful_placement_tests()