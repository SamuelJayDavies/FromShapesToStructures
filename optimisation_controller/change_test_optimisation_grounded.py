import numpy as np

from brick_placement import ConstructionGrid


class TestBrick:
    def __init__(
        self,
        y: int,
        z: int,
        x: int,
        size_z: int = 1,
        size_x: int = 1,
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


def add_test_brick(
    construction_grid: ConstructionGrid,
    brick: TestBrick,
) -> int:

    brick_id = len(construction_grid.placed_bricks)

    construction_grid.placed_bricks.append(brick)

    construction_grid.current_grid[
        brick.y,
        brick.z:brick.z + brick.size_z(),
        brick.x:brick.x + brick.size_x(),
    ] = brick_id

    return brick_id


def test_above_and_below_brick_queries() -> None:
    result_grid = np.ones((3, 1, 1), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    bottom_brick = TestBrick(y=0, z=0, x=0)
    middle_brick = TestBrick(y=1, z=0, x=0)
    top_brick = TestBrick(y=2, z=0, x=0)

    bottom_id = add_test_brick(construction_grid, bottom_brick)
    middle_id = add_test_brick(construction_grid, middle_brick)
    top_id = add_test_brick(construction_grid, top_brick)

    print(construction_grid.get_bricks_above(bottom_brick))
    print(middle_id)
    assert construction_grid.get_bricks_above(bottom_brick) == {middle_id}

    assert construction_grid.get_support_bricks(middle_brick) == {bottom_id}
    assert construction_grid.get_bricks_above(middle_brick) == {top_id}

    assert construction_grid.get_support_bricks(top_brick) == {middle_id}
    assert construction_grid.get_bricks_above(top_brick) == set()

    print("Passed: test_above_and_below_brick_queries")


def test_vertical_connectivity_traversal() -> None:
    result_grid = np.ones((4, 1, 1), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    brick_0 = TestBrick(y=0, z=0, x=0)
    brick_1 = TestBrick(y=1, z=0, x=0)
    brick_2 = TestBrick(y=2, z=0, x=0)
    brick_3 = TestBrick(y=3, z=0, x=0)

    brick_0_id = add_test_brick(construction_grid, brick_0)
    brick_1_id = add_test_brick(construction_grid, brick_1)
    brick_2_id = add_test_brick(construction_grid, brick_2)
    brick_3_id = add_test_brick(construction_grid, brick_3)

    connected_ids = construction_grid.get_vertically_connected_brick_ids(
        starting_brick_ids={brick_1_id}
    )

    expected_ids = (
        brick_0_id,
        brick_1_id,
        brick_2_id,
        brick_3_id,
    )

    assert connected_ids == expected_ids

    print("Passed: test_vertical_connectivity_traversal")


def test_same_layer_side_contact_is_not_connected() -> None:
    result_grid = np.ones((1, 1, 2), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    left_brick = TestBrick(y=0, z=0, x=0)
    right_brick = TestBrick(y=0, z=0, x=1)

    left_id = add_test_brick(construction_grid, left_brick)
    add_test_brick(construction_grid, right_brick)

    connected_ids = construction_grid.get_vertically_connected_brick_ids(
        starting_brick_ids={left_id}
    )

    assert connected_ids == (left_id,)

    print("Passed: test_same_layer_side_contact_is_not_connected")


def test_excluded_brick_breaks_connectivity() -> None:
    result_grid = np.ones((4, 1, 1), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    brick_0 = TestBrick(y=0, z=0, x=0)
    brick_1 = TestBrick(y=1, z=0, x=0)
    brick_2 = TestBrick(y=2, z=0, x=0)
    brick_3 = TestBrick(y=3, z=0, x=0)

    brick_0_id = add_test_brick(construction_grid, brick_0)
    brick_1_id = add_test_brick(construction_grid, brick_1)
    brick_2_id = add_test_brick(construction_grid, brick_2)
    add_test_brick(construction_grid, brick_3)

    connected_ids = construction_grid.get_vertically_connected_brick_ids(
        starting_brick_ids={brick_0_id},
        excluded_brick_ids={brick_2_id},
    )

    assert connected_ids == (
        brick_0_id,
        brick_1_id,
    )

    print("Passed: test_excluded_brick_breaks_connectivity")


def test_grounded_connectivity_excludes_floating_component() -> None:
    result_grid = np.ones((3, 1, 3), dtype=bool)

    construction_grid = ConstructionGrid(
        result_grid=result_grid,
        force_support=False,
    )

    grounded_bottom = TestBrick(y=0, z=0, x=0)
    grounded_middle = TestBrick(y=1, z=0, x=0)
    grounded_top = TestBrick(y=2, z=0, x=0)

    floating_bottom = TestBrick(y=1, z=0, x=2)
    floating_top = TestBrick(y=2, z=0, x=2)

    grounded_bottom_id = add_test_brick(
        construction_grid,
        grounded_bottom,
    )
    grounded_middle_id = add_test_brick(
        construction_grid,
        grounded_middle,
    )
    grounded_top_id = add_test_brick(
        construction_grid,
        grounded_top,
    )

    add_test_brick(construction_grid, floating_bottom)
    add_test_brick(construction_grid, floating_top)

    grounded_ids = (
        construction_grid.get_grounded_brick_ids()
    )

    assert grounded_ids == (
        grounded_bottom_id,
        grounded_middle_id,
        grounded_top_id,
    )

    print("Passed: test_grounded_connectivity_excludes_floating_component")


def main() -> None:
    test_above_and_below_brick_queries()
    test_vertical_connectivity_traversal()
    test_same_layer_side_contact_is_not_connected()
    test_excluded_brick_breaks_connectivity()
    test_grounded_connectivity_excludes_floating_component()

    print("All structural connectivity tests passed.")


if __name__ == "__main__":
    main()