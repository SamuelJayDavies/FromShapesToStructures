import numpy as np

from brick.Brick import Brick
from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolationDetector import (
    StructuralViolationDetector
)


class TestBrick(Brick):
    """
    Minimal Brick implementation containing only the properties needed
    by ConstructionGrid and StructuralViolationDetector.
    """

    def __init__(
        self,
        y: int,
        z: int,
        x: int,
        size_z: int,
        size_x: int
    ) -> None:
        self.y = y
        self.z = z
        self.x = x

        self._size_z = size_z
        self._size_x = size_x

    def size_z(self) -> int:
        return self._size_z

    def size_x(self) -> int:
        return self._size_x


def create_construction_grid(
    shape: tuple[int, int, int] = (4, 4, 4)
) -> ConstructionGrid:
    result_grid = np.ones(
        shape=shape,
        dtype=bool
    )

    return ConstructionGrid(
        result_grid=result_grid,
        minimum_support_ratio=0.5,
        force_support = False
    )


def add_test_brick(
    construction_grid: ConstructionGrid,
    brick: TestBrick
) -> int:
    """
    Adds a brick directly to the test construction state.

    Direct insertion is used so unsupported bricks can be created
    without passing through normal placement validation.
    """

    brick_id = len(
        construction_grid.placed_bricks
    )

    construction_grid.placed_bricks.append(
        brick
    )

    construction_grid.current_grid[
        brick.y,
        brick.z:brick.z + brick.size_z(),
        brick.x:brick.x + brick.size_x()
    ] = brick_id

    return brick_id


def test_ground_brick_does_not_create_violation() -> None:
    construction_grid = create_construction_grid()

    ground_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=ground_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert violations == []

    print(
        "Passed: ground brick did not create a violation"
    )


def test_fully_supported_brick_does_not_create_violation(
) -> None:
    construction_grid = create_construction_grid()

    supporting_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    upper_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=supporting_brick
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=upper_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert violations == []

    print(
        "Passed: fully supported brick did not create "
        "a violation"
    )


def test_exact_threshold_does_not_create_violation() -> None:
    construction_grid = create_construction_grid()

    # Supports two of the four cells beneath the upper brick.
    supporting_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=1,
        size_x=2
    )

    upper_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=supporting_brick
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=upper_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert violations == []

    print(
        "Passed: brick exactly at the support threshold "
        "did not create a violation"
    )


def test_partially_supported_brick_creates_violation() -> None:
    construction_grid = create_construction_grid()

    # Supports one of the four cells beneath the upper brick.
    supporting_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=1,
        size_x=1
    )

    upper_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=supporting_brick
    )

    upper_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=upper_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert len(violations) == 1

    violation = violations[0]

    assert violation.brick_id == upper_brick_id
    assert violation.brick is upper_brick
    assert violation.layer == 1

    assert violation.actual_support_ratio == 0.25
    assert violation.minimum_support_ratio == 0.5
    assert violation.support_diff == 0.25

    assert violation.total_footprint_coordinates_count == 4
    assert violation.supported_footprint_coordinates_count == 1
    assert violation.unsupported_footprint_coordinates_count == 3
    
    print(violation.footprint_coordinates)

    assert violation.footprint_coordinates == (
        (1, 0, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 1, 1)
    )

    assert (
        violation.unsupported_footprint_coordinates
        == (
            (1, 0, 1),
            (1, 1, 0),
            (1, 1, 1)
        )
    )

    print(
        "Passed: partially supported brick created "
        "the correct violation"
    )


def test_floating_brick_creates_violation() -> None:
    construction_grid = create_construction_grid()

    floating_brick = TestBrick(
        y=2,
        z=1,
        x=1,
        size_z=1,
        size_x=2
    )

    floating_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=floating_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert len(violations) == 1

    violation = violations[0]

    assert violation.brick_id == floating_brick_id
    assert violation.actual_support_ratio == 0.0
    assert violation.minimum_support_ratio == 0.5
    assert violation.support_diff == 0.5

    assert violation.total_footprint_coordinates_count == 2
    assert violation.supported_footprint_coordinates_count == 0
    assert violation.unsupported_footprint_coordinates_count == 2

    assert (
        violation.unsupported_footprint_coordinates
        == (
            (2, 1, 1),
            (2, 1, 2)
        )
    )

    print(
        "Passed: floating brick created the correct violation"
    )


def test_multiple_violations_are_returned_deterministically(
) -> None:
    construction_grid = create_construction_grid(
        shape=(4, 5, 5)
    )

    # Added in a deliberately different order from their spatial order.
    higher_brick = TestBrick(
        y=3,
        z=0,
        x=0,
        size_z=1,
        size_x=1
    )

    right_brick = TestBrick(
        y=1,
        z=2,
        x=2,
        size_z=1,
        size_x=1
    )

    left_brick = TestBrick(
        y=1,
        z=0,
        x=1,
        size_z=1,
        size_x=1
    )

    higher_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=higher_brick
    )

    right_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=right_brick
    )

    left_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=left_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert len(violations) == 3

    # Expected ordering is y, then z, then x, then brick ID.
    assert [
        violation.brick_id
        for violation in violations
    ] == [
        left_brick_id,
        right_brick_id,
        higher_brick_id
    ]

    assert [
        violation.layer
        for violation in violations
    ] == [
        1,
        1,
        3
    ]

    print(
        "Passed: multiple violations were returned "
        "in deterministic spatial order"
    )


def test_supported_and_unsupported_bricks_are_separated(
) -> None:
    construction_grid = create_construction_grid()

    ground_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=2,
        size_x=2
    )

    supported_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=1,
        size_x=2
    )

    floating_brick = TestBrick(
        y=2,
        z=2,
        x=2,
        size_z=1,
        size_x=1
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=ground_brick
    )

    add_test_brick(
        construction_grid=construction_grid,
        brick=supported_brick
    )

    floating_brick_id = add_test_brick(
        construction_grid=construction_grid,
        brick=floating_brick
    )

    detector = StructuralViolationDetector(
        minimum_support_ratio=0.5
    )

    violations = detector.detect_violations(
        construction_grid
    )

    assert len(violations) == 1
    assert violations[0].brick_id == floating_brick_id
    assert violations[0].brick is floating_brick

    print(
        "Passed: detector returned only the unsupported brick"
    )


def test_invalid_detector_threshold_is_rejected() -> None:
    try:
        StructuralViolationDetector(
            minimum_support_ratio=1.1
        )

        raise AssertionError(
            "A support ratio above 1.0 should have been rejected."
        )

    except ValueError:
        pass

    print(
        "Passed: invalid detector thresholds were rejected"
    )


def main() -> None:
    test_ground_brick_does_not_create_violation()

    test_fully_supported_brick_does_not_create_violation()

    test_exact_threshold_does_not_create_violation()

    test_partially_supported_brick_creates_violation()

    test_floating_brick_creates_violation()

    test_multiple_violations_are_returned_deterministically()

    test_supported_and_unsupported_bricks_are_separated()

    test_invalid_detector_threshold_is_rejected()

    print(
        "\nAll StructuralViolationDetector tests passed."
    )


if __name__ == "__main__":
    main()