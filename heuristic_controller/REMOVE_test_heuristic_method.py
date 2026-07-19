import numpy as np

from brick import BrickType
from brick import Brick_vocabulary
from brick_placement import ConstructionGrid
from brick_generation import CandidateGenerator
from brick_generation import CandidateGenerationStrategy
from brick_scoring import CandidateScorer
from brick_scoring import CandidateSelector

from brick_placement.CandidatePlacementController import CandidatePlacementController
from .HeuristicController import (
    HeuristicController,
)
from brick_placement import PlacementResult 


BASIC_STRATEGY = (
    CandidateGenerationStrategy
    .CandidateGenerationStrategy
    .BASIC
)

INFORMED_STRATEGY = (
    CandidateGenerationStrategy
    .CandidateGenerationStrategy
    .INFORMED
)

SEARCH_STRATEGIES = (
    BASIC_STRATEGY,
    INFORMED_STRATEGY,
)


def create_construction_controller(
    search_strategy,
    result_grid: np.ndarray | None = None,
) -> tuple[
    HeuristicController,
    CandidatePlacementController,
    ConstructionGrid,
    CandidateGenerator,
]:
    if result_grid is None:
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

    candidate_placement_controller = (
        CandidatePlacementController(
            construction_grid=construction_grid,
            candidate_generator=candidate_generator,
            candidate_scorer=CandidateScorer(),
            candidate_selector=CandidateSelector(),
        )
    )

    construction_controller = (
        HeuristicController(
            candidate_placement_controller
        )
    )

    return (
        construction_controller,
        candidate_placement_controller,
        construction_grid,
        candidate_generator,
    )


def assert_target_is_fully_covered(
    construction_grid: ConstructionGrid,
) -> None:
    for y in range(
        construction_grid.result_shape[0]
    ):
        uncovered_layer = (
            construction_grid.get_uncovered_layer(y)
        )

        assert not np.any(uncovered_layer)

    target_coordinates = construction_grid.result_grid

    assert np.all(
        construction_grid.current_grid[
            target_coordinates
        ] >= 0
    )


def test_successful_complete_construction(
    search_strategy,
) -> None:
    (
        construction_controller,
        _,
        construction_grid,
        _,
    ) = create_construction_controller(
        search_strategy
    )

    placement_history = (
        construction_controller.construct_structure()
    )

    assert len(placement_history) > 1

    final_result = placement_history[-1]

    assert (
        final_result.status
        == PlacementResult.STATUS_COMPLETE
    )

    assert final_result.crucial_point is None
    assert final_result.selected_brick is None
    assert final_result.candidate_score is None
    assert final_result.candidate_count == 0

    placed_results = [
        result
        for result in placement_history
        if result.status
        == PlacementResult.STATUS_PLACED
    ]

    assert len(placed_results) > 1

    assert (
        len(placement_history)
        == len(placed_results) + 1
    )

    assert all(
        result.status
        == PlacementResult.STATUS_PLACED
        for result in placement_history[:-1]
    )

    assert (
        len(placed_results)
        == len(construction_grid.placed_bricks)
    )

    for brick_index, placement_result in enumerate(
        placed_results
    ):
        assert placement_result.crucial_point is not None
        assert placement_result.selected_brick is not None
        assert placement_result.candidate_score is not None
        assert placement_result.candidate_count > 0

        assert placement_result.selected_brick.is_placed()

        assert (
            placement_result.selected_brick.brick_id
            == brick_index
        )

        assert (
            construction_grid.placed_bricks[
                brick_index
            ]
            is placement_result.selected_brick
        )

    expected_brick_ids = list(
        range(len(construction_grid.placed_bricks))
    )

    actual_brick_ids = [
        brick.brick_id
        for brick in construction_grid.placed_bricks
    ]

    assert actual_brick_ids == expected_brick_ids

    assert_target_is_fully_covered(
        construction_grid
    )

    print(
        "Passed: test_successful_complete_construction "
        f"({search_strategy})"
    )


def test_construction_stops_when_no_candidates_exist(
    search_strategy,
) -> None:
    (
        construction_controller,
        _,
        construction_grid,
        candidate_generator,
    ) = create_construction_controller(
        search_strategy
    )

    grid_before_construction = (
        construction_grid.current_grid.copy()
    )

    def return_no_candidates(*args, **kwargs):
        return []

    candidate_generator.generate_candidates = (
        return_no_candidates
    )

    placement_history = (
        construction_controller.construct_structure()
    )

    assert len(placement_history) == 1

    final_result = placement_history[-1]

    assert (
        final_result.status
        == PlacementResult
        .STATUS_NO_VALID_CANDIDATES
    )

    assert final_result.crucial_point == (0, 0, 0)
    assert final_result.selected_brick is None
    assert final_result.candidate_score is None
    assert final_result.candidate_count == 0

    assert len(construction_grid.placed_bricks) == 0

    assert np.array_equal(
        construction_grid.current_grid,
        grid_before_construction,
    )

    assert np.any(
        construction_grid.get_uncovered_layer(0)
    )

    print(
        "Passed: "
        "test_construction_stops_when_no_candidates_exist "
        f"({search_strategy})"
    )


def test_construction_stops_after_partial_progress(
    search_strategy,
) -> None:
    (
        construction_controller,
        candidate_placement_controller,
        construction_grid,
        candidate_generator,
    ) = create_construction_controller(
        search_strategy
    )

    first_result = (
        candidate_placement_controller.place_next_brick()
    )

    assert (
        first_result.status
        == PlacementResult.STATUS_PLACED
    )

    assert len(construction_grid.placed_bricks) == 1

    grid_after_first_placement = (
        construction_grid.current_grid.copy()
    )

    def return_no_candidates(*args, **kwargs):
        return []

    candidate_generator.generate_candidates = (
        return_no_candidates
    )

    placement_history = (
        construction_controller.construct_structure()
    )

    assert len(placement_history) == 1

    final_result = placement_history[-1]

    assert (
        final_result.status
        == PlacementResult
        .STATUS_NO_VALID_CANDIDATES
    )

    assert final_result.crucial_point is not None
    assert final_result.selected_brick is None
    assert final_result.candidate_score is None
    assert final_result.candidate_count == 0

    assert len(construction_grid.placed_bricks) == 1

    assert np.array_equal(
        construction_grid.current_grid,
        grid_after_first_placement,
    )

    assert np.any(
        construction_grid.get_uncovered_layer(0)
    )

    print(
        "Passed: "
        "test_construction_stops_after_partial_progress "
        f"({search_strategy})"
    )


def test_already_complete_structure(
    search_strategy,
) -> None:
    result_grid = np.ones(
        shape=(1, 1, 1),
        dtype=bool,
    )

    (
        construction_controller,
        candidate_placement_controller,
        construction_grid,
        _,
    ) = create_construction_controller(
        search_strategy,
        result_grid,
    )

    initial_placement = (
        candidate_placement_controller.place_next_brick()
    )

    assert (
        initial_placement.status
        == PlacementResult.STATUS_PLACED
    )

    assert len(construction_grid.placed_bricks) == 1

    grid_before_construction_call = (
        construction_grid.current_grid.copy()
    )

    placement_history = (
        construction_controller.construct_structure()
    )

    assert len(placement_history) == 1

    final_result = placement_history[0]

    assert (
        final_result.status
        == PlacementResult.STATUS_COMPLETE
    )

    assert final_result.crucial_point is None
    assert final_result.selected_brick is None
    assert final_result.candidate_score is None
    assert final_result.candidate_count == 0

    assert len(construction_grid.placed_bricks) == 1

    assert np.array_equal(
        construction_grid.current_grid,
        grid_before_construction_call,
    )

    print(
        "Passed: test_already_complete_structure "
        f"({search_strategy})"
    )


def test_maximum_iteration_safeguard(
    search_strategy,
) -> None:
    (
        construction_controller,
        candidate_placement_controller,
        _,
        _,
    ) = create_construction_controller(
        search_strategy
    )

    valid_placed_result = (
        candidate_placement_controller.place_next_brick()
    )

    assert (
        valid_placed_result.status
        == PlacementResult.STATUS_PLACED
    )

    def repeatedly_report_placement():
        return valid_placed_result

    candidate_placement_controller.place_next_brick = (
        repeatedly_report_placement
    )

    construction_controller.maximum_iterations = 3

    try:
        construction_controller.construct_structure()

    except RuntimeError as error:
        assert (
            "Maximum construction iterations reached"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected the maximum-iteration safeguard "
            "to raise RuntimeError"
        )

    print(
        "Passed: test_maximum_iteration_safeguard "
        f"({search_strategy})"
    )


def test_invalid_placement_controller() -> None:
    try:
        HeuristicController(
            candidate_placement_controller=None
        )

    except TypeError:
        pass

    else:
        raise AssertionError(
            "Expected invalid placement controller "
            "to raise TypeError"
        )

    print(
        "Passed: test_invalid_placement_controller"
    )
    
def create_multi_layer_target() -> np.ndarray:
    return np.array(
        [
            [
                [True, True, True],
                [True, True, True],
            ],
            [
                [True, True, False],
                [True, True, False],
            ],
        ],
        dtype=bool,
    )
    
def test_multi_layer_complete_construction(
    search_strategy,
) -> None:
    result_grid = create_multi_layer_target()

    (
        construction_controller,
        _,
        construction_grid,
        _,
    ) = create_construction_controller(
        search_strategy,
        result_grid,
    )

    placement_history = (
        construction_controller.construct_structure()
    )

    assert (
        placement_history[-1].status
        == PlacementResult.STATUS_COMPLETE
    )

    placed_results = [
        result
        for result in placement_history
        if result.status
        == PlacementResult.STATUS_PLACED
    ]

    placed_layers = [
        result.selected_brick.y
        for result in placed_results
    ]

    assert 0 in placed_layers
    assert 1 in placed_layers

    assert placed_layers == sorted(placed_layers)

    first_upper_layer_index = placed_layers.index(1)

    assert all(
        layer == 0
        for layer in placed_layers[
            :first_upper_layer_index
        ]
    )

    assert all(
        layer == 1
        for layer in placed_layers[
            first_upper_layer_index:
        ]
    )

    for y in range(construction_grid.result_shape[0]):
        assert not np.any(
            construction_grid.get_uncovered_layer(y)
        )

    assert np.all(
        construction_grid.current_grid[
            construction_grid.result_grid
        ] >= 0
    )

    assert np.all(
        construction_grid.current_grid[
            ~construction_grid.result_grid
        ] == -1
    )

    total_placed_area = sum(
        brick.orientation[0] * brick.orientation[1]
        for brick in construction_grid.placed_bricks
    )

    assert total_placed_area == int(
        construction_grid.result_grid.sum()
    )

    assert (
        len(placed_results)
        == len(construction_grid.placed_bricks)
    )

    print(
        "Passed: test_multi_layer_complete_construction "
        f"({search_strategy})"
    )
    
    
    
    
    
    
    
    
    
    
def run_heuristic_construction_tests() -> None:
    for search_strategy in SEARCH_STRATEGIES:
        test_successful_complete_construction(
            search_strategy
        )

        test_construction_stops_when_no_candidates_exist(
            search_strategy
        )

        test_construction_stops_after_partial_progress(
            search_strategy
        )

        test_already_complete_structure(
            search_strategy
        )

        test_maximum_iteration_safeguard(
            search_strategy
        )

        test_multi_layer_complete_construction(
            search_strategy
        )

    test_invalid_placement_controller()

    print()
    print(
        "All heuristic-construction verification "
        "tests passed."
    )


if __name__ == "__main__":
    run_heuristic_construction_tests()