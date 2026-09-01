import numpy as np

from brick.Brick import Brick
from brick.BrickType import BrickType
from brick.Brick_vocabulary import BASIC_BRICK_VOCABULARY

from brick_placement.ConstructionGrid import ConstructionGrid

from brick_generation.CandidateGenerator import CandidateGenerator
from brick_generation.CandidateGenerationStrategy import CandidateGenerationStrategy

from optimisation_controller.StructuralViolationDetector import StructuralViolationDetector

from optimisation_controller.ViolationGrouper import ViolationGrouper

from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker

from optimisation_controller.UnsupportedDistanceEvaluator import UnsupportedDistanceEvaluator
from optimisation_controller.StructuralRepairEvaluator import StructuralRepairEvaluator

from optimisation_controller.ReplacementCandidateGenerator import ReplacementCandidateGenerator
from optimisation_controller.ReplacementCandidateEvaluator import ReplacementCandidateEvaluator

from evaluation.EvaluationStatistics import EvaluationStatistics

def get_basic_brick_type(name: str) -> BrickType:
    for brick_type in BASIC_BRICK_VOCABULARY.bricks():
        if brick_type.name == name:
            return brick_type
    
    raise ValueError("Brick type " + name + " was not found in BASIC vocabulary")


# Test 1
def test_construction_grid_validation() -> None:
    
    result_grid = np.ones((2, 4, 4), dtype=bool)
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=True)
    
    brick_1x1 = get_basic_brick_type("1x1")
    brick_1x2 = get_basic_brick_type("1x2")
    
    # Test 1.1 - Ground bricks should be valid
    
    ground_brick = Brick(brick_1x1, 0, 1, 1, brick_1x1.orientations()[0])
    
    assert construction_grid.can_place_brick(ground_brick)
    
    construction_grid.place_brick(ground_brick)
    
    # Test 1.2 - Brick overlaps should be rejected
    overlapping_brick = Brick(brick_1x1, 0, 1, 1, brick_1x1.orientations()[0])
    
    assert not construction_grid.can_place_brick(overlapping_brick)
    
    # Test 1.3 - Out-of-bounds brick should be rejected
    out_of_bounds_brick = Brick(brick_1x2, 0, 3, 3, brick_1x2.orientations()[0])
    
    assert not construction_grid.validate_brick_in_bounds(out_of_bounds_brick)
    
    # Test 1.4 - Verify support ratio is calculated correctly at 0.5
    candidate_orientation = brick_1x2.orientations()[0]
    
    partially_supported_brick = Brick(brick_1x2, 1, 1, 1, candidate_orientation)
    
    support_ratio = construction_grid.calculate_support_ratio(partially_supported_brick)
    
    assert support_ratio == 0.5
    
    assert construction_grid.can_place_brick(partially_supported_brick)

# Test 2
def test_candidate_generation() -> None:
    
    result_grid = np.zeros((2, 4, 4), dtype=bool)
    
    result_grid[0, 1, 1] = True
    
    result_grid[1, 1:3, 1:4] = True
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=True)
    
    brick_1x1 = get_basic_brick_type("1x1")
    
    ground_brick = Brick(brick_1x1, 0, 1, 1, brick_1x1.orientations()[0])
    
    construction_grid.place_brick(ground_brick)
    
    free_grid = construction_grid.result_grid & ~construction_grid.convert_to_result_grid()
    
    generator = CandidateGenerator(BASIC_BRICK_VOCABULARY, CandidateGenerationStrategy.BASIC)
    
    # Test 2.1 - Crucial point should be in the correct format
    crucial_point = generator.find_next_crucial_point(free_grid, excluded_points=set())
    
    assert crucial_point == (1, 1, 1)
    
    # Test 2.2 - Generates a candidate at a crucial point
    candidates = generator.generate_candidates(free_grid, crucial_point, construction_grid)
    
    assert len(candidates) > 0
    
    # Test 2.3 - Every generated candidate covers the crucial point
    # Test 2.4 - Every generated candidate remains inside the free target geometry
    # Test 2.5 - Every generated candidate satisfies the ConstructionGrid placement rules
    # Test 2.6 - Every generated candidate has sufficient support ratio
    for candidate in candidates:
        
        candidate_coordinates = {(candidate.y, z, x) for z in range(candidate.z, candidate.z + candidate.size_z()) for x in range(candidate.x, candidate.x + candidate.size_x())}
        
        assert crucial_point in candidate_coordinates
        
        for y, z, x in candidate_coordinates:
            assert free_grid[y, z, x]
            
        assert construction_grid.can_place_brick(candidate)
        
        assert construction_grid.calculate_support_ratio(candidate) >= 0.5
    
    # Test 2.7 - Every generated candidate list has a fallback 1x1 brick
    one_by_one_candiates = [candidate for candidate in candidates if candidate.brickType.name == "1x1"]
    
    assert len(one_by_one_candiates) >= 1
        
    
    
    
# Test 3 - Structural Violation Detection
def test_structural_violation_detection() -> None:
    
    result_grid = np.ones((2, 5, 5), dtype=bool)
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=False)
    
    brick_1x1 = get_basic_brick_type("1x1")
    brick_2x2 = get_basic_brick_type("2x2")
    
    orientation_1x1 = brick_1x1.orientations()[0]
    orientation_2x2 = brick_2x2.orientations()[0]
    
    # Fully supported brick
    
    full_support_ground = Brick(brick_1x1, 0, 0, 0, orientation_1x1)
    
    construction_grid.place_brick(full_support_ground)
    
    fully_supported_brick = Brick(brick_1x1, 1, 0, 0, orientation_1x1)
    
    construction_grid.place_brick(fully_supported_brick)
    
    fully_supported_id = fully_supported_brick.brick_id
    
    # Partially supported brick
    
    partial_support_ground = Brick(brick_1x1, 0, 2, 0, orientation_1x1)
    
    construction_grid.place_brick(partial_support_ground)
    
    partially_supported_brick = Brick(brick_2x2, 1, 2, 0, orientation_2x2)
    
    construction_grid.place_brick(partially_supported_brick)
    
    partially_supported_id = partially_supported_brick.brick_id
    
    # Floating brick
    
    floating_brick = Brick(brick_1x1, 1, 4, 4, orientation_1x1)
    
    construction_grid.place_brick(floating_brick)
    
    floating_id = floating_brick.brick_id
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    violations = detector.detect_violations(construction_grid)
    
    violation_by_id = {violation.brick_id: violation for violation in violations}
    
    
    # Test 3.1 - Detecting the correct amount of violations
    assert len(violations) == 2
    
    # Test 3.2 - Correctly identifying a supported brick as a non-violation
    assert fully_supported_id not in violation_by_id
    
    # Test 3.3 - Correctly identifying a partial supported brick as a violation
    assert partially_supported_id in violation_by_id
    
    # Test 3.4 - Partial brick has the correct support ratio
    partial_violation = violation_by_id[partially_supported_id]
    
    assert np.isclose(partial_violation.actual_support_ratio, 0.25)
    
    # Test 3.5 - Partial brick has the correct supported footprint coordinate count
    assert partial_violation.supported_footprint_coordinates_count == 1
    
    # Test 3.6 - Partial brick has the correct unsupported footprint coordinate count
    assert len(partial_violation.unsupported_footprint_coordinates) == 3
    
    # Test 3.7 - Floating brick has zero support
    assert floating_id in violation_by_id
    
    floating_violation = violation_by_id[floating_id]
    
    assert np.isclose(floating_violation.actual_support_ratio, 0.0)
    
    # Test 3.8 - Floating brick has no supported footprint coordinates
    assert floating_violation.supported_footprint_coordinates_count == 0
    
    # Test 3.9 - Floating brick has the correct unsupported footprint count
    assert len(floating_violation.unsupported_footprint_coordinates) == 1
    

# Test 4 - Violation Grouping
def test_violation_grouping() -> None:
    
    result_grid = np.ones((3, 6, 6), dtype=bool)
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=False)
    
    brick_1x1 = get_basic_brick_type("1x1")
    brick_2x2 = get_basic_brick_type("2x2")
        
    orientation_1x1 = brick_1x1.orientations()[0]
    orientation_2x2 = brick_2x2.orientations()[0]
    
    violation_a_brick = Brick(brick_1x1, 1, 1, 1, orientation_1x1)
    
    construction_grid.place_brick(violation_a_brick)
    
    violation_b_brick = Brick(brick_1x1, 1, 1, 2, orientation_1x1)
    
    construction_grid.place_brick(violation_b_brick)
    
    violation_c_brick = Brick(brick_2x2, 2, 1, 2, orientation_2x2)
    
    construction_grid.place_brick(violation_c_brick)
    
    isolated_brick = Brick(brick_1x1, 1, 4, 4, orientation_1x1)
    
    construction_grid.place_brick(isolated_brick)
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    violations = detector.detect_violations(construction_grid)
    
    # Test 4.1 - Correctly detecting the correct number of violations
    assert len(violations) == 4
    
    grouper = ViolationGrouper()
    
    clusters = grouper.group_violations(violations)
    
    # Test 4.2 - Forming The correct amount of clusters 
    assert len(clusters) == 2
    
    cluster_id_sets = [{violation.brick_id for violation in cluster.violations} for cluster in clusters]
    
    connected_ids = {violation_a_brick.brick_id, violation_b_brick.brick_id, violation_c_brick.brick_id}
    
    isolated_ids = {isolated_brick.brick_id}
    
    # Test 4.3 - Forming the cluster with the correct violations
    assert connected_ids in cluster_id_sets
    
    # Test 4.4 - Excluding an incorrect violation from the cluster
    assert isolated_ids in cluster_id_sets
    
    cluster_sizes = sorted(len(cluster.violations) for cluster in clusters)
    
    # Test 4.5 - Ensuring both clusters have been formed with the correct violation counts
    assert cluster_sizes == [1, 3]
    
    
# Test 5 - Grounded Connectivity Classification
def test_grounded_connectivity_classification() -> None:
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    grouper = ViolationGrouper()

    brick_1x1 = get_basic_brick_type("1x1")
    brick_2x2 = get_basic_brick_type("2x2")
    brick_2x4 = get_basic_brick_type("2x4")

    orientation_1x1 = brick_1x1.orientations()[0]
    orientation_2x2 = brick_2x2.orientations()[0]
    orientation_2x4 = brick_2x4.orientations()[0]
    
    disconnected_target = np.ones((2, 5, 5), dtype=bool)
    
    disconnected_brick = Brick(brick_1x1, 1, 2, 2, orientation_1x1)
    
    disconnected_grid = ConstructionGrid(disconnected_target, minimum_support_ratio=0.5, force_support=False)
    
    disconnected_grid.place_brick(disconnected_brick)
    
    disconnected_violations = detector.detect_violations(disconnected_grid)
    
    disconnected_clusters = grouper.group_violations(disconnected_violations)
    
    # Test 5.1 - Ensuring the amount of disconnected clusters is correct
    assert len(disconnected_clusters) == 1
    
    disconnected_cluster = disconnected_clusters[0]
    
    disconnected_checker = StructuralGroundedChecker(disconnected_grid)
    
    disconnected_regions = disconnected_checker.get_grounded_regions(disconnected_cluster)
    
    # Test 5.2 - Ensuring no externel grounded attachment with a disconnected cluster
    assert len(disconnected_regions) == 0
    
    single_target = np.ones((2, 5, 5), dtype=bool)

    single_grid = ConstructionGrid(single_target, minimum_support_ratio=0.5, force_support=False)

    single_ground_brick = Brick(brick_1x1, 0, 1, 1, orientation_1x1)

    single_grid.place_brick(single_ground_brick)

    single_weak_brick = Brick(brick_2x2, 1, 1, 1, orientation_2x2)

    single_grid.place_brick(single_weak_brick)
    
    # Test 5.3 - Ensuring weak brick has the correct support
    assert np.isclose(single_grid.calculate_support_ratio(single_weak_brick), 0.25)
    
    single_violations = detector.detect_violations(single_grid)

    single_clusters = grouper.group_violations(single_violations)

    # Test 5.4 - Ensuring the cluster grouping contains only one cluster
    assert len(single_clusters) == 1

    single_cluster = single_clusters[0]

    single_checker = StructuralGroundedChecker(single_grid)

    single_regions = (single_checker.get_grounded_regions(single_cluster))
    
    # Test 5.5 - Ensuring a brick produces exactly one independent grounded region
    assert len(single_regions) == 1

    single_region_ids = set(single_regions[0])

    # Test 5.6 - Ensuring the grouned brick is from the correct region
    assert (single_ground_brick.brick_id in single_region_ids)
    
    multi_target = np.ones((2, 6, 7), dtype=bool)

    multi_grid = ConstructionGrid(multi_target, minimum_support_ratio=0.5, force_support=False)

    size_z = orientation_2x4[1]
    size_x = orientation_2x4[0]

    weak_z = 1
    weak_x = 1

    first_ground_brick = Brick(brick_1x1, 0, weak_z, weak_x, orientation_1x1)

    multi_grid.place_brick(first_ground_brick)

    second_ground_brick = Brick(brick_1x1, 0, weak_z + size_z - 1, weak_x + size_x - 1, orientation_1x1)

    multi_grid.place_brick(second_ground_brick)

    multi_weak_brick = Brick(brick_2x4, 1, weak_z, weak_x, orientation_2x4)

    multi_grid.place_brick(multi_weak_brick)

    # Test 5.7 - Ensuring two support weak brick has the correct ratio
    assert np.isclose(multi_grid.calculate_support_ratio(multi_weak_brick), 0.25)

    multi_violations = detector.detect_violations(multi_grid)

    multi_clusters = grouper.group_violations(multi_violations)

    # Test 5.8 - Ensuring the two support weak brick cluster contains only one cluster
    assert len(multi_clusters) == 1

    multi_cluster = multi_clusters[0]

    multi_checker = StructuralGroundedChecker(multi_grid)

    multi_regions = multi_checker.get_grounded_regions(multi_cluster)

    # Test 5.9 - Ensuring a brick produces exactly two independent grounded region
    assert len(multi_regions) == 2

    multi_region_sets = [set(region) for region in multi_regions]

    # Test 5.10 - Ensuring the first grounded brick is from the correct region
    assert any(first_ground_brick.brick_id in region for region in multi_region_sets)

    # Test 5.11 - Ensuring the second grounded brick is from the correct region
    assert any(second_ground_brick.brick_id in region for region in multi_region_sets)


# Test 6 - Unsupported Distance and Repair Classification
def test_unsupported_distance_analysis() -> None:
    
    result_grid = np.ones((2, 7, 7), dtype=bool)
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=False)
    
    brick_1x1 = get_basic_brick_type("1x1")
    brick_2x4 = get_basic_brick_type("2x4")
    
    orientation_1x1 = brick_1x1.orientations()[0]
    orientation_2x4 = brick_2x4.orientations()[0]
    
    weak_y = 1
    weak_z = 1
    weak_x = 1
    
    ground_support = Brick(brick_1x1, 0, weak_z, weak_x, orientation_1x1)
    
    construction_grid.place_brick(ground_support)
    
    weak_brick = Brick(brick_2x4, weak_y, weak_z, weak_x, orientation_2x4)
    
    construction_grid.place_brick(weak_brick)
    
    # Test 6.1 - Ensuring a weak brick has only one supported footprint coordinate
    assert np.isclose(construction_grid.calculate_support_ratio(weak_brick), 1.0 / weak_brick.area())
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    violations = detector.detect_violations(construction_grid)
    
    # Test 6.2 - Ensuring a weak brick is correctly detected as the only structural violation
    assert len(violations) == 1
    
    grouper = ViolationGrouper()
    
    clusters = grouper.group_violations(violations)
    
    # Test 6.3 - Ensuring the single violation forms one violation cluster
    assert len(clusters) == 1
    
    cluster = clusters[0]
    
    grounded_checker = StructuralGroundedChecker(construction_grid)
    
    distance_evaluator = UnsupportedDistanceEvaluator(construction_grid, grounded_checker)
    
    grounded_regions = distance_evaluator.get_grounded_regions(cluster)
    
    # Test 6.4 - Ensuring the weak cluster has exactly one independently grounded region
    assert len(grounded_regions) == 1
    
    contact_coordinates = distance_evaluator.get_grounded_contact_coordinates(cluster, grounded_regions[0])
    
    expected_contact = (weak_y, weak_z, weak_x)
    
    # Test 6.5 - Ensuring the grounded-contact coordinate is correctly identified
    assert contact_coordinates == (expected_contact,)
    
    expected_max_distance = ((weak_brick.size_z() - 1) + (weak_brick.size_x() - 1))
    
    expected_furthest_coordinate = (weak_y, weak_z + weak_brick.size_z() - 1, weak_x + weak_brick.size_x() - 1)
    
    furthest_result = distance_evaluator.get_furthest_unsupported_coordinate(cluster)
    
    # Test 6.6 - Ensuring furthest unsupported coordinate is successfully identified
    assert furthest_result is not None
    
    furthest_coordinate, furthest_distance = furthest_result
    
    # Test 6.7 - Ensuring the correct furthest unsupported coordinate is selected
    assert furthest_coordinate == expected_furthest_coordinate
    
    # Test 6.8 - Ensuring the BFS distance to the furthest unsupported coordinate is correct
    assert furthest_distance == expected_max_distance
    
    # Test 6.9 - Ensuring maximum unsupported distance reports the expected value
    assert (distance_evaluator.get_maximum_unsupported_distance(cluster) == expected_max_distance)
    
    # Test 6.10 - Ensuring all footprint coordinates except the grounded contact are unsupported
    assert (distance_evaluator.get_unsupported_coordinate_count(cluster) == weak_brick.area() - 1)
    
    accepted_evaluator = StructuralRepairEvaluator(grounded_checker, distance_evaluator, expected_max_distance)
    
    # Test 6.11 - Ensuring unsupported distance equaling to the accepted threshold does not require repair
    assert not accepted_evaluator.requires_repair(cluster)
    
    stricter_evaluator = StructuralRepairEvaluator(grounded_checker, distance_evaluator, expected_max_distance - 1)
    
    # Test 6.12 - Ensuring unsupported distance exceeding the accepted threshold requires repair
    assert stricter_evaluator.requires_repair(cluster)


# Test 7 - Structural Repairing
def test_structural_repair_candidates() -> None:
    
    brick_1x1 = get_basic_brick_type("1x1")
    brick_1x2 = get_basic_brick_type("1x2")
    
    orientation_1x1 = brick_1x1.orientations()[0]
    
    orientation_1x2 = next(orientation for orientation in brick_1x2.orientations() if orientation[0] == 2 and orientation[1] == 1)
    
    replacement_target = np.zeros((2, 5, 5), dtype=bool)
    
    replacement_target[1, 2, 2] = True
    replacement_target[1, 2, 1] = True
    replacement_target[0, 2, 3] = True
    
    replacement_grid = ConstructionGrid(replacement_target, minimum_support_ratio=0.5, force_support=False)
    
    ground_support = Brick(brick_1x1, 0, 2, 3, orientation_1x1)
    
    replacement_grid.place_brick(ground_support)
    
    target_brick = Brick(brick_1x1, 1, 2, 2, orientation_1x1)
    
    replacement_grid.place_brick(target_brick)
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    violations = detector.detect_violations(replacement_grid)
    
    target_violation = next(violation for violation in violations if violation.brick_id == target_brick.brick_id)
    
    grouper = ViolationGrouper()
    
    cluster = grouper.group_violations([target_violation])[0]
    
    replacement_generator = ReplacementCandidateGenerator(BASIC_BRICK_VOCABULARY)
    
    candidates = replacement_generator.generate_replacement_candidates(target_violation)
    
    # Test 7.1 - Ensuring at least one larger replacement candidate is generated
    assert len(candidates) > 0
    
    target_coordinates = set(replacement_grid.get_brick_footprint_coordinates(target_brick))
    
    for candidate in candidates:
        
        candidate_coordinates = { (candidate.y, z, x) for z in range(candidate.z, candidate.z + candidate.size_z()) for x in range(candidate.x, candidate.x + candidate.size_x())}
        
        # Test 7.2 - Ensuring every replacement candidate is strictly larger than the target brick
        assert candidate.area() > target_brick.area()
        
        # Test 7.3 - Ensuring every replacement candidate completely contains the original target footprint
        assert target_coordinates.issubset(candidate_coordinates)
    
    useful_candidate = Brick(brick_1x2, 1, 2, 2, orientation_1x2)
    
    evaluator = ReplacementCandidateEvaluator(replacement_grid)
    
    valid_candidates = [candidate for candidate in candidates if evaluator.validate_candidate_does_not_conflict(candidate, target_violation)]

    # Test 7.4 - Ensuring At least one generated replacement candidate also passes grid-bound and conflict validation
    assert len(valid_candidates) > 0
    
    evaluation = evaluator.evaluate_candidate(useful_candidate, target_violation, cluster)
    
    # Test 7.5 - Ensuring a valid structurally useful replacement candidate is successfully evaluated
    assert evaluation is not None
    
    _, support_improvement, grounded_attachment_count, outside_target_count = evaluation
    
    # Test 7.6 - Ensuring replacement improves the original floating brick support ratio by 0.5
    assert np.isclose(support_improvement, 0.5)
    
    # Test 7.7 - Ensuring replacement establishes one independently grounded attachment
    assert grounded_attachment_count == 1
    
    # Test 7.8 - Ensuring replacement correctly records one coordinate outside the target geometry
    assert outside_target_count == 1
    
    # Test 7.9 - Ensuring the candidate is recognised as structurally beneficial
    assert evaluator.has_structural_improvement(support_improvement, grounded_attachment_count)
    
    support_only_candidate = Brick(brick_1x2, 1, 1, 2, orientation_1x2)
    
    selected_candidate = evaluator.select_best_candidate([(support_only_candidate, 0.9, 0, 0), (useful_candidate, 0.5, 1, 1)])
    
    # Test 7.10 - Ensuring independent grounding is prioritised over greater raw support improvement
    assert selected_candidate is useful_candidate
    
    unrelated_brick = Brick(brick_1x1, 1, 2, 1, orientation_1x1)
    
    replacement_grid.place_brick(unrelated_brick)
    
    conflicting_candidate = Brick(brick_1x2, 1, 2, 1, orientation_1x2)
    
    # Test 7.11 - Ensuring replacement candidate conflicting with an unrelated brick is rejected
    assert not evaluator.validate_candidate_does_not_conflict(conflicting_candidate, target_violation)
    
    merge_target = np.zeros((2, 4, 4), dtype=bool)
    
    merge_target[1, 1, 1] = True
    merge_target[1, 1, 2] = True
    
    merge_grid = ConstructionGrid(merge_target, minimum_support_ratio=0.5, force_support=False)
    
    first_brick = Brick(brick_1x1, 1, 1, 1, orientation_1x1)
    
    second_brick = Brick(brick_1x1, 1, 1, 2, orientation_1x1)
    
    merge_grid.place_brick(first_brick)
    merge_grid.place_brick(second_brick)
    
    merge_violations = detector.detect_violations(merge_grid)
    
    # Test 7.12 - Ensuring both floating merge bricks are detected as violations
    assert len(merge_violations) == 2
    
    merge_clusters = grouper.group_violations(merge_violations)
    
    # Test 7.13 - Ensuring adjacent merge violations form one cluster
    assert len(merge_clusters) == 1
    
    merge_cluster = merge_clusters[0]
    
    target_merge_violation = next(violation for violation in merge_violations if violation.brick_id == first_brick.brick_id)
    
    merge_generator = ReplacementCandidateGenerator(BASIC_BRICK_VOCABULARY)
    
    merge_candidates = merge_generator.generate_merge_candidates(merge_grid, target_merge_violation)
    
    # Test 7.14 - Ensuring at least one valid exact-footprint merge candidate is generated
    assert len(merge_candidates) > 0
    
    original_combined_coordinates = set(merge_grid.get_brick_footprint_coordinates(first_brick)) | set(merge_grid.get_brick_footprint_coordinates(second_brick))
    
    exact_merge = None
    
    for candidate, target_id, neighbour_id in merge_candidates:
        
        candidate_coordinates = set(merge_grid.get_brick_footprint_coordinates(candidate))
        
        if (candidate.brickType.name == "1x2" and candidate_coordinates == original_combined_coordinates):
            
            exact_merge = (candidate, target_id, neighbour_id)
            break
    
    # Test 7.15 - ENsuring the exact rectangular 1x2 merge candidate is identified
    assert exact_merge is not None
    
    merged_brick, target_id, neighbour_id = exact_merge
    
    merge_evaluator = ReplacementCandidateEvaluator(merge_grid)
    
    merge_evaluation = merge_evaluator.evaluate_merge_candidate(merged_brick, target_id, neighbour_id, target_merge_violation, merge_cluster)
    
    # Test 7.16 - Ensuring exact merge candidate pass merge validation and evaluation
    assert merge_evaluation is not None
    
    occupancy_before = merge_grid.convert_to_result_grid().copy()
    
    active_count_before = merge_grid.get_active_brick_count()
    
    merge_grid.merge_bricks(target_id, neighbour_id, merged_brick)
    
    occupancy_after = merge_grid.convert_to_result_grid()
    
    active_count_after = merge_grid.get_active_brick_count()
    
    # Test 7.17 - Ensuring two-brick merge reduces active brick count by exactly one
    assert active_count_after == active_count_before - 1
    
    # Test 7.18 - Ensuring the merge preserves the exact occupied geometry
    assert np.array_equal(occupancy_before, occupancy_after)
    
    # Test 7.19 - Ensuring the merged neighbour brick ID is correctly retired
    assert neighbour_id in merge_grid.retired_brick_ids
    
    # Test 7.20 - Ensuring the original target ID remains active after merging
    assert merge_grid.is_active_brick_id(target_id)

# Test 8 - Evaluation Statistics Functioning
def test_evaluation_statistics_functioning() -> None:
    
    result_grid = np.zeros((2, 2, 2), dtype=bool)
    
    result_grid[0, 0, 0:2] = True
    result_grid[1, 0, 0:2] = True
    
    construction_grid = ConstructionGrid(result_grid, minimum_support_ratio=0.5, force_support=True)
    
    brick_1x2 = get_basic_brick_type("1x2")
    
    orientation_1x2 = next(orientation for orientation in brick_1x2.orientations() if orientation[0] == 2 and orientation[1] == 1)
    
    ground_brick = Brick(brick_1x2, 0, 0, 0, orientation_1x2)
    
    construction_grid.place_brick(ground_brick)
    
    upper_brick = Brick(brick_1x2, 1, 0, 0, orientation_1x2)
    
    construction_grid.place_brick(upper_brick)
    
    detector = StructuralViolationDetector(minimum_support_ratio=0.5)
    
    statistics = EvaluationStatistics(construction_grid, detector)
    
    statistics.evaluate(2.0)
    
    # Test 8.1 - Ensuring the correct number of target voxels are recorded
    assert statistics.target_voxel_count == 4
    
    # Test 8.2 - Ensuring all four target voxels are correctly covered
    assert statistics.correctly_covered_voxel_count == 4
    
    # Test 8.3 - Ensuring no target voxels are missed
    assert statistics.missed_target_voxel_count == 0
    
    # Test 8.4 - Ensuring no geometry extends outside the target
    assert statistics.outside_target_voxel_count == 0
    
    # Test 8.5 - Ensuring the coverage ratio correctly reports complete reconstruction
    assert np.isclose(statistics.coverage_ratio, 1.0)
    
    # Test 8.6 - Ensuring reconstruction is correctly classified as geometrically complete
    assert statistics.reconstruction_completed
    
    # Test 8.7 - Ensuring fully supported construction contains no local support violations
    assert statistics.local_support_violation_count == 0
    
    # Test 8.8 - Ensuring fully supported construction contains no floating bricks
    assert statistics.floating_brick_count == 0
    
    # Test 8.9 - Ensuring the mean non-ground support ratio is correctly calculated as 1.0
    assert np.isclose(statistics.mean_support_ratio, 1.0)
    
    # Test 8.10 - Ensuring the active brick count correctly reports two placed bricks
    assert statistics.active_brick_count == 2
    
    # Test 8.11 - Ensuring the covered voxels per brick is correctly calculated as 2.0
    assert np.isclose(statistics.covered_voxels_per_brick, 2.0)
    
    # Test 8.12 - Ensuring the supplied runtime is correctly recorded
    assert np.isclose(statistics.total_runtime_seconds, 2.0)
    
    # Test 8.13 - Ensuring the covered voxels per second is correctly calculated as 2.0
    assert np.isclose(statistics.covered_voxels_per_second, 2.0)


def main() -> None:
    
    tests = [
        
        (
            "Construction Grid Placement and Support", test_construction_grid_validation
        ),
        (
            "Candidate Generation", test_candidate_generation
        ),
        (
            "Structural Violation Detection", test_structural_violation_detection
        ),
        (
            "Violation Grouping", test_violation_grouping
        ),
        (
            "Grounded Connectivity Classification", test_grounded_connectivity_classification
        ),
        (
            "Unsupported Distance and Repair Classification", test_unsupported_distance_analysis
        ),
        (
            "Structural Repairing", test_structural_repair_candidates
        ),
        (
            "Evaluation Statistics Correctness", test_evaluation_statistics_functioning
        )
    ]
    
    passed_tests = 0
    
    print("\nVALIDATION TEST RESULTS") 
    print("=========================")
    
    for test_name, test_function in tests:
        try:
            test_function()
            
            passed_tests += 1
            print("[PASSED] " + test_name)
        
        except AssertionError:
            
            print("[FAILED] " + test_name)
            raise
    
    print("\n" + str(passed_tests) + " / " + str(len(tests)) + " validate tests passed")


if __name__ == "__main__":
    main()

