from typing import Callable

from brick import Brick
from brick import BrickType

from brick_scoring import CandidateScore
from brick_scoring import CandidateSelector


BRICK_EFFICIENCY_WEIGHT: float = 0.30
SUPPORT_WEIGHT: float = 0.40
CONNECTIVITY_WEIGHT: float = 0.20
GAP_AVOIDANCE_WEIGHT: float = 0.10


def create_candidate_score(
    brick_efficiency_score: float,
    support_score: float,
    connectivity_score: float,
    gap_penalty: float,
) -> CandidateScore:

    gap_avoidance_score = 1.0 - gap_penalty

    total_score = (
        BRICK_EFFICIENCY_WEIGHT * brick_efficiency_score
        + SUPPORT_WEIGHT * support_score
        + CONNECTIVITY_WEIGHT * connectivity_score
        + GAP_AVOIDANCE_WEIGHT * gap_avoidance_score
    )

    return CandidateScore(
        brick_efficiency_score=brick_efficiency_score,
        support_score=support_score,
        connectivity_score=connectivity_score,
        gap_penalty=gap_penalty,
        total_score=total_score,
    )


def assert_raises(
    expected_exception: type[Exception],
    function: Callable,
    *arguments: object,
) -> None:

    try:
        function(*arguments)

    except expected_exception:
        return

    except Exception as exception:
        raise AssertionError(
            f"Expected {expected_exception.__name__}, "
            f"but {type(exception).__name__} was raised."
        ) from exception

    raise AssertionError(
        f"Expected {expected_exception.__name__} to be raised."
    )


def test_clear_highest_scoring_candidate() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)
    two_by_two = BrickType("2x2", 2, 2)

    lower_scoring_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    highest_scoring_candidate = Brick(
        brickType=two_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 2),
    )

    lower_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.50,
        connectivity_score=0.50,
        gap_penalty=0.50,
    )

    highest_score = create_candidate_score(
        brick_efficiency_score=1.00,
        support_score=1.00,
        connectivity_score=1.00,
        gap_penalty=0.00,
    )

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (lower_scoring_candidate, lower_score),
                (highest_scoring_candidate, highest_score),
            ]
        )
    )

    assert selected_candidate is highest_scoring_candidate
    assert selected_score is highest_score

    assert not lower_scoring_candidate.is_placed()
    assert not highest_scoring_candidate.is_placed()


def test_equal_total_resolved_by_support() -> None:

    selector = CandidateSelector()

    one_by_three = BrickType("1x3", 1, 3)
    one_by_four = BrickType("1x4", 1, 4)

    larger_candidate = Brick(
        brickType=one_by_four,
        y=0,
        z=0,
        x=0,
        orientation=(4, 1),
    )

    stronger_support_candidate = Brick(
        brickType=one_by_three,
        y=0,
        z=0,
        x=0,
        orientation=(3, 1),
    )

    larger_candidate_score = create_candidate_score(
        brick_efficiency_score=1.00,
        support_score=0.80,
        connectivity_score=0.50,
        gap_penalty=0.20,
    )

    stronger_support_score = create_candidate_score(
        brick_efficiency_score=0.75,
        support_score=0.90,
        connectivity_score=0.625,
        gap_penalty=0.10,
    )

    assert selector._compare_score_values(
        larger_candidate_score.total_score,
        stronger_support_score.total_score,
    ) == 0

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (larger_candidate, larger_candidate_score),
                (
                    stronger_support_candidate,
                    stronger_support_score,
                ),
            ]
        )
    )

    assert larger_candidate.area() > stronger_support_candidate.area()

    assert selected_candidate is stronger_support_candidate
    assert selected_score is stronger_support_score


def test_equal_total_and_support_resolved_by_gap_avoidance() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    weaker_gap_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=1,
        orientation=(2, 1),
    )

    stronger_gap_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    weaker_gap_score = create_candidate_score(
        brick_efficiency_score=1.00,
        support_score=0.80,
        connectivity_score=0.30,
        gap_penalty=0.30,
    )

    stronger_gap_score = create_candidate_score(
        brick_efficiency_score=0.80,
        support_score=0.80,
        connectivity_score=0.50,
        gap_penalty=0.10,
    )

    assert selector._compare_score_values(
        weaker_gap_score.total_score,
        stronger_gap_score.total_score,
    ) == 0

    assert selector._compare_score_values(
        weaker_gap_score.support_score,
        stronger_gap_score.support_score,
    ) == 0

    assert (
        stronger_gap_score.gap_avoidance_score()
        > weaker_gap_score.gap_avoidance_score()
    )

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (weaker_gap_candidate, weaker_gap_score),
                (stronger_gap_candidate, stronger_gap_score),
            ]
        )
    )

    assert selected_candidate is stronger_gap_candidate
    assert selected_score is stronger_gap_score


def test_equal_earlier_scores_resolved_by_connectivity() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    lower_connectivity_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    higher_connectivity_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=1,
        orientation=(2, 1),
    )

    lower_connectivity_score = create_candidate_score(
        brick_efficiency_score=0.80,
        support_score=0.80,
        connectivity_score=0.50,
        gap_penalty=0.20,
    )

    higher_connectivity_score = create_candidate_score(
        brick_efficiency_score=0.60,
        support_score=0.80,
        connectivity_score=0.80,
        gap_penalty=0.20,
    )

    assert selector._compare_score_values(
        lower_connectivity_score.total_score,
        higher_connectivity_score.total_score,
    ) == 0

    assert selector._compare_score_values(
        lower_connectivity_score.support_score,
        higher_connectivity_score.support_score,
    ) == 0

    assert selector._compare_score_values(
        lower_connectivity_score.gap_avoidance_score(),
        higher_connectivity_score.gap_avoidance_score(),
    ) == 0

    assert (
        higher_connectivity_score.connectivity_score
        > lower_connectivity_score.connectivity_score
    )

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (
                    lower_connectivity_candidate,
                    lower_connectivity_score,
                ),
                (
                    higher_connectivity_candidate,
                    higher_connectivity_score,
                ),
            ]
        )
    )

    assert selected_candidate is higher_connectivity_candidate
    assert selected_score is higher_connectivity_score


def test_equal_scores_resolved_by_area() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)
    two_by_two = BrickType("2x2", 2, 2)

    smaller_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    larger_candidate = Brick(
        brickType=two_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 2),
    )

    smaller_candidate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    larger_candidate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    assert larger_candidate.area() > smaller_candidate.area()

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (smaller_candidate, smaller_candidate_score),
                (larger_candidate, larger_candidate_score),
            ]
        )
    )

    assert selected_candidate is larger_candidate
    assert selected_score is larger_candidate_score


def test_canonical_coordinate_tie_resolution() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    lower_coordinate_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=2,
        x=0,
        orientation=(2, 1),
    )

    higher_coordinate_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=2,
        x=1,
        orientation=(2, 1),
    )

    lower_coordinate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    higher_coordinate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    selected_candidate, selected_score = (
        selector.select_best_candidate(
            [
                (
                    higher_coordinate_candidate,
                    higher_coordinate_score,
                ),
                (
                    lower_coordinate_candidate,
                    lower_coordinate_score,
                ),
            ]
        )
    )

    assert selected_candidate is lower_coordinate_candidate
    assert selected_score is lower_coordinate_score


def test_input_order_independence() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    lower_coordinate_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=1,
        x=0,
        orientation=(2, 1),
    )

    higher_coordinate_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=1,
        x=1,
        orientation=(2, 1),
    )

    lower_coordinate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    higher_coordinate_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    first_order_candidate, _ = selector.select_best_candidate(
        [
            (
                higher_coordinate_candidate,
                higher_coordinate_score,
            ),
            (
                lower_coordinate_candidate,
                lower_coordinate_score,
            ),
        ]
    )

    reversed_order_candidate, _ = selector.select_best_candidate(
        [
            (
                lower_coordinate_candidate,
                lower_coordinate_score,
            ),
            (
                higher_coordinate_candidate,
                higher_coordinate_score,
            ),
        ]
    )

    assert first_order_candidate is lower_coordinate_candidate
    assert reversed_order_candidate is lower_coordinate_candidate


def test_repeatability_across_multiple_calls() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    deterministic_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=3,
        x=0,
        orientation=(2, 1),
    )

    other_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=3,
        x=1,
        orientation=(2, 1),
    )

    deterministic_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    other_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.75,
        connectivity_score=0.50,
        gap_penalty=0.25,
    )

    for iteration in range(20):

        if iteration % 2 == 0:
            scored_candidates = [
                (other_candidate, other_score),
                (deterministic_candidate, deterministic_score),
            ]

        else:
            scored_candidates = [
                (deterministic_candidate, deterministic_score),
                (other_candidate, other_score),
            ]

        selected_candidate, selected_score = (
            selector.select_best_candidate(scored_candidates)
        )

        assert selected_candidate is deterministic_candidate
        assert selected_score is deterministic_score


def test_selection_does_not_place_candidates() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    first_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    second_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=1,
        orientation=(2, 1),
    )

    first_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.50,
        connectivity_score=0.50,
        gap_penalty=0.50,
    )

    second_score = create_candidate_score(
        brick_efficiency_score=1.00,
        support_score=1.00,
        connectivity_score=1.00,
        gap_penalty=0.00,
    )

    selector.select_best_candidate(
        [
            (first_candidate, first_score),
            (second_candidate, second_score),
        ]
    )

    assert not first_candidate.is_placed()
    assert not second_candidate.is_placed()


def test_invalid_input_validation() -> None:

    selector = CandidateSelector()

    one_by_two = BrickType("1x2", 1, 2)

    valid_candidate = Brick(
        brickType=one_by_two,
        y=0,
        z=0,
        x=0,
        orientation=(2, 1),
    )

    valid_score = create_candidate_score(
        brick_efficiency_score=0.50,
        support_score=0.50,
        connectivity_score=0.50,
        gap_penalty=0.50,
    )

    assert_raises(
        TypeError,
        selector.select_best_candidate,
        "not a list",
    )

    assert_raises(
        ValueError,
        selector.select_best_candidate,
        [],
    )

    assert_raises(
        TypeError,
        selector.select_best_candidate,
        [(valid_candidate,)],
    )

    assert_raises(
        TypeError,
        selector.select_best_candidate,
        [("not a Brick", valid_score)],
    )

    assert_raises(
        TypeError,
        selector.select_best_candidate,
        [(valid_candidate, "not a CandidateScore")],
    )


def run_candidate_selection_tests() -> None:

    tests = [
        test_clear_highest_scoring_candidate,
        test_equal_total_resolved_by_support,
        test_equal_total_and_support_resolved_by_gap_avoidance,
        test_equal_earlier_scores_resolved_by_connectivity,
        test_equal_scores_resolved_by_area,
        test_canonical_coordinate_tie_resolution,
        test_input_order_independence,
        test_repeatability_across_multiple_calls,
        test_selection_does_not_place_candidates,
        test_invalid_input_validation,
    ]

    for test in tests:
        test()
        print(f"Passed: {test.__name__}")

    print()
    print("All candidate-selection verification tests passed.")


if __name__ == "__main__":
    run_candidate_selection_tests()