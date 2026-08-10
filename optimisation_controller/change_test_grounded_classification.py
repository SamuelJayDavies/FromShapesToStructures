from brick_placement import ConstructionGrid
from optimisation_controller.test_brick import TestBrick
from optimisation_controller.test_brick import add_test_brick

from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker

import numpy as np 

class TestViolationCluster:
    """Minimal test double representing the brick IDs of a violation cluster."""

    def __init__(
        self,
        violating_brick_ids: tuple[int, ...],
    ) -> None:
        self.violation_brick_ids = violating_brick_ids


def test_disconnected_cluster_classification() -> None:
    """Verifies that a weak cluster with no grounded boundary connection is
    classified as DISCONNECTED.
    """

    result_grid = np.ones((2, 1, 2), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    ground_brick = TestBrick(
    y=0,
    z=0,
    x=0,
    size_z=1,
    size_x=1,
    )


    weak_brick = TestBrick(
    y=1,
    z=0,
    x=1,
    size_z=1,
    size_x=1,
    )

    add_test_brick(
        construction_grid,
        ground_brick,
    )

    weak_brick_id = add_test_brick(
        construction_grid,
        weak_brick,
    )

    cluster = TestViolationCluster(
        violating_brick_ids=(weak_brick_id,)
    )

    grounded_checker = StructuralGroundedChecker(
        construction_grid
    )

    assert (
        grounded_checker.get_cluster_boundary_brick_ids(cluster)
        == ()
    )

    assert (
        grounded_checker.get_grounded_boundary_brick_ids(cluster)
        == ()
    )

    assert (
        grounded_checker.get_grounded_regions(cluster)
        == ()
    )

    assert (
        grounded_checker.classify_cluster_support(cluster)
        == grounded_checker.CLASSIFICATION_DISCONNECTED
    )

    print("Passed: test_disconnected_cluster_classification")


def test_single_anchored_cluster_classification() -> None:
    """Verifies that a weak cluster attached to one independent grounded
    region is classified as SINGLE_ANCHORED.
    """

    result_grid = np.ones((2, 1, 2), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    ground_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=1,
        size_x=1,
    )

    weak_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=1,
        size_x=2,
    )

    ground_brick_id = add_test_brick(
        construction_grid,
        ground_brick,
    )

    weak_brick_id = add_test_brick(
        construction_grid,
        weak_brick,
    )

    cluster = TestViolationCluster(
        violating_brick_ids=(weak_brick_id,)
    )

    grounded_checker = StructuralGroundedChecker(
        construction_grid
    )

    assert (
        grounded_checker.get_cluster_boundary_brick_ids(cluster)
        == (ground_brick_id,)
    )

    assert (
        grounded_checker.get_grounded_boundary_brick_ids(cluster)
        == (ground_brick_id,)
    )

    assert (
        grounded_checker.get_grounded_regions(cluster)
        == ((ground_brick_id,),)
    )

    assert (
        grounded_checker.classify_cluster_support(cluster)
        == grounded_checker.CLASSIFICATION_SINGLE_ANCHORED
    )

    print("Passed: test_single_anchored_cluster_classification")


def test_multi_anchored_cluster_classification() -> None:
    """Verifies that a weak cluster connected to two independently grounded
    regions is classified as MULTI_ANCHORED.
    """

    result_grid = np.ones((2, 1, 3), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    left_ground_brick = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=1,
        size_x=1,
    )

    right_ground_brick = TestBrick(
        y=0,
        z=0,
        x=2,
        size_z=1,
        size_x=1,
    )

    weak_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=1,
        size_x=3,
    )

    left_ground_id = add_test_brick(
        construction_grid,
        left_ground_brick,
    )

    right_ground_id = add_test_brick(
        construction_grid,
        right_ground_brick,
    )

    weak_brick_id = add_test_brick(
        construction_grid,
        weak_brick,
    )

    cluster = TestViolationCluster(
        violating_brick_ids=(weak_brick_id,)
    )

    grounded_checker = StructuralGroundedChecker(
        construction_grid
    )

    assert (
        grounded_checker.get_grounded_boundary_brick_ids(cluster)
        == (
            left_ground_id,
            right_ground_id,
        )
    )

    assert (
        grounded_checker.get_grounded_regions(cluster)
        == (
            (left_ground_id,),
            (right_ground_id,),
        )
    )

    assert (
        grounded_checker.classify_cluster_support(cluster)
        == grounded_checker.CLASSIFICATION_MULTI_ANCHORED
    )

    print("Passed: test_multi_anchored_cluster_classification")


def test_multiple_boundary_bricks_same_attachment_region() -> None:
    """Verifies that multiple grounded boundary bricks belonging to the same
    connected component count as one attachment region.
    """

    result_grid = np.ones((3, 1, 2), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    ground_base = TestBrick(
        y=0,
        z=0,
        x=0,
        size_z=1,
        size_x=2,
    )

    left_boundary_brick = TestBrick(
        y=1,
        z=0,
        x=0,
        size_z=1,
        size_x=1,
    )

    right_boundary_brick = TestBrick(
        y=1,
        z=0,
        x=1,
        size_z=1,
        size_x=1,
    )

    weak_brick = TestBrick(
        y=2,
        z=0,
        x=0,
        size_z=1,
        size_x=2,
    )

    add_test_brick(
        construction_grid,
        ground_base,
    )

    left_boundary_id = add_test_brick(
        construction_grid,
        left_boundary_brick,
    )

    right_boundary_id = add_test_brick(
        construction_grid,
        right_boundary_brick,
    )

    weak_brick_id = add_test_brick(
        construction_grid,
        weak_brick,
    )

    cluster = TestViolationCluster(
        violating_brick_ids=(weak_brick_id,)
    )

    grounded_checker = StructuralGroundedChecker(
        construction_grid
    )

    assert (
        grounded_checker.get_grounded_boundary_brick_ids(cluster)
        == (
            left_boundary_id,
            right_boundary_id,
        )
    )

    assert (
        grounded_checker.get_grounded_regions(cluster)
        == (
            (
                left_boundary_id,
                right_boundary_id,
            ),
        )
    )

    assert (
        grounded_checker.classify_cluster_support(cluster)
        == grounded_checker.CLASSIFICATION_SINGLE_ANCHORED
    )

    print(
        "Passed: "
        "test_multiple_boundary_bricks_same_attachment_region"
    )
    
def main() -> None:
    test_disconnected_cluster_classification()
    test_single_anchored_cluster_classification()
    test_multi_anchored_cluster_classification()
    test_multiple_boundary_bricks_same_attachment_region()

    print(
        "All structural connectivity and grounding tests passed."
    )
    
if __name__ == "__main__":
    main()