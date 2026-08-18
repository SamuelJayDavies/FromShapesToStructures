import numpy as np

# Stage 1 imports to get the model data -> Open3D voxel grid -> numpy result grid
from voxelisation import MeshVoxeliser
from voxelisation.MeshVoxeliser import create_path
from voxelisation.ResultGrid import ResultGrid

# Stage 2 imports to define bricks, the generation strategy and the Heuristic Pipeline
from brick.BrickType import BrickType
from brick.Brick_vocabulary import Brick_vocabulary
from brick.Brick_vocabulary import BASIC_BRICK_VOCABULARY, ADVANCED_BRICK_VOCABULARY

from brick_generation.CandidateGenerationStrategy import CandidateGenerationStrategy

from heuristic_controller.HeuristicPipeline import HeuristicPipeline
from heuristic_controller.HeuristicResult import HeuristicResult

# Stage 3 comparing original to result
from brick_placement.PlacementResult import PlacementResult

# Stage 4 Visualising the final result
from visualisation.BrickConstructionVisualiser import BrickConstructionVisualiser

# Stage 1A - Introducing Structural Violation Detector
from optimisation_controller.StructuralViolationDetector import StructuralViolationDetector
from optimisation_controller.StructuralViolation import StructuralViolation
from optimisation_controller.ViolationCluster import ViolationCluster
from optimisation_controller.ViolationGrouper import ViolationGrouper

# Stage 2A - The Structural Repair and Evaluator Thing
from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker
from optimisation_controller.UnsupportedDistanceEvaluator import UnsupportedDistanceEvaluator
from optimisation_controller.StructuralRepairEvaluator import StructuralRepairEvaluator
from optimisation_controller.StructuralRepairSelector import StructuralRepairSelector

from optimisation_controller.ReplacementCandidateGenerator import ReplacementCandidateGenerator
from optimisation_controller.ReplacementCandidateEvaluator import ReplacementCandidateEvaluator

from optimisation_controller.StructuralRepairController import StructuralRepairController
from optimisation_controller.OptimisationStatistics import OptimisationStatistics

# Stage 3A - Improving Visualisations
from visualisation.BrickConstructionVisualiser import BrickConstructionVisualiser

MODEL_CLASS: str = "chair"
MODEL_NUMBER: int = 1
MODEL_DATASET: str = "shapenet"

RESOLUTION: int = 16

MINIMUM_SUPPORT_RATIO = 0.5
FINAL_SUPPORT_RATIO = MINIMUM_SUPPORT_RATIO # Change if you want sofa example

IS_MODEL_UPSIDE_DOWN: bool = False
VISUALISE_VIOLATIONS: bool = True

MAXIMUM_UNSUPPORTED_DISTANCE_ACCEPTED: int = max(1, RESOLUTION/16)
BUILDING_BRICK_VOCAB = BASIC_BRICK_VOCABULARY
REPLACEMENT_BRICK_VOCAB = ADVANCED_BRICK_VOCABULARY
# Sofas need a support ratio of 0.25

# Stage 1
def create_model_result_grid() -> np.ndarray:
    
    model_path = create_path(MODEL_CLASS, MODEL_NUMBER, MODEL_DATASET)
    
    mesh_voxeliser = MeshVoxeliser(model_path, resolution=RESOLUTION)
    
    voxel_grid = mesh_voxeliser.start()
    
    result_grid = ResultGrid()
    
    result_grid.create_result_grid(voxel_grid)
    
    # Temporary Testing Thing
    if IS_MODEL_UPSIDE_DOWN:    
        result_grid.result_grid = np.flip(result_grid.result_grid, axis=0)
    
    return result_grid.result_grid

def visualise_result_grid(result_grid: np.ndarray) -> None:
    
    result_voxel_count = int(np.count_nonzero(result_grid))
    ground_layer_voxel_count = int(np.count_nonzero(result_grid[0]))
    
    print("\nResults for actual model voxel grid")
    print("=====================================")
    print("Model Class: " + MODEL_CLASS)
    print("Model Number: " + str(MODEL_NUMBER))
    print("Model Dataset: " + MODEL_DATASET)
    print("Resolution: " + str(RESOLUTION))
    print("Result grid shape: ")
    print(result_grid.shape)
    print("Result grid voxel count: ")
    print(result_voxel_count)
    print("Ground-Layer voxel count: ")
    print(ground_layer_voxel_count)
    
    
# Stage 2
def run_heuristic(result_grid: np.ndarray, brick_vocabulary: Brick_vocabulary, strategy: CandidateGenerationStrategy, minimum_support_ratio: float) -> HeuristicResult:
    
    pipeline = HeuristicPipeline(result_grid, brick_vocabulary, strategy, minimum_support_ratio, True, force_support=False)
    
    finished_structure = pipeline.create_structure()
    
    return finished_structure

def run_optimisation(finished_structure: HeuristicResult, brick_vocab: Brick_vocabulary, minimum_support_ratio: float, maximum_unsupported_distance_accepted: int) -> OptimisationStatistics:
    
    construction_grid = finished_structure.construction_grid
    
    violation_detector = StructuralViolationDetector(minimum_support_ratio)
    violation_grouper = ViolationGrouper()
    
    grounded_checker = StructuralGroundedChecker(construction_grid)
    distance_evaluator = UnsupportedDistanceEvaluator(construction_grid, grounded_checker)
    
    repair_evaluator = StructuralRepairEvaluator(grounded_checker, distance_evaluator, maximum_unsupported_distance_accepted)
    
    repair_selector = StructuralRepairSelector(distance_evaluator)
    
    replacement_candidate_generator = ReplacementCandidateGenerator(REPLACEMENT_BRICK_VOCAB)
    replacement_candidate_evaluator = ReplacementCandidateEvaluator(construction_grid)
    
    optimisation_statistics = OptimisationStatistics()
    
    repair_controller = StructuralRepairController(construction_grid, violation_detector, violation_grouper, repair_evaluator, repair_selector, replacement_candidate_generator, replacement_candidate_evaluator, optimisation_statistics)
    
    successful_replacement_repair = repair_controller.repair_with_replacement()
    
    successful_merge_repair = (
    repair_controller.repair_with_merging()
)

    print(
        "Replacement phase successful:",
        successful_replacement_repair
    )

    print(
        "Merge phase successful:",
        successful_merge_repair
    )

    print(
        "Active bricks after merging:",
        construction_grid.get_active_brick_count()
    )

    remaining_repair_clusters = (
        repair_controller.get_required_repair_clusters()
    )

    print(
        "Repair-required clusters after merging:",
        len(remaining_repair_clusters)
    )

    print(
        "Retired brick IDs:",
        construction_grid.retired_brick_ids
    )
    
    return optimisation_statistics
    

# Stage 3 - Comparing final grid to result_grid
def compare_final_to_result(finished_structure: HeuristicResult, strategy: CandidateGenerationStrategy) -> None:
    
    result_grid = finished_structure.result_grid
    #finished_grid_in_result_grid_format = finished_structure.finished_grid.astype(bool) #Change this when you need it for report
    finished_grid_in_result_grid_format = finished_structure.finished_grid != -1 
    
    correctly_covered = result_grid & finished_grid_in_result_grid_format
    missed_coverage = result_grid & ~finished_grid_in_result_grid_format
    outside_coverage = ~result_grid & finished_grid_in_result_grid_format
    
    correctly_covered_voxels = int(np.count_nonzero(correctly_covered))
    missed_coverage_voxels = int(np.count_nonzero(missed_coverage))
    outside_coverage_voxels = int(np.count_nonzero(outside_coverage))
    
    num_of_placed_bricks = len(finished_structure.placed_bricks)
    placement_history_count = len(finished_structure.placement_history)
    
    print("\nResults for comparision between result and final grid using strategy: " + strategy.name)
    print("================================================")
    print("Final status :" + finished_structure.final_status)
    print("Placed bricks: " + str(num_of_placed_bricks))
    print("Number of entries in placement history :" + str(placement_history_count))
    print("Correctly covered voxel count: " + str(correctly_covered_voxels))
    print("Missed voxel count: " + str(missed_coverage_voxels))
    print("Overextended or outside coverage voxels: " + str(outside_coverage_voxels))
    
    if (finished_structure.final_status != PlacementResult.STATUS_COMPLETE and finished_structure.placement_history):
        last_crucial_point = finished_structure.placement_history[-1].crucial_point
        
        print("Last point left uncompleted :")
        print(last_crucial_point)
    
def main(minimum_support_ratio: float) -> None:
    # Stage 1
    result_grid = create_model_result_grid()
    visualise_result_grid(result_grid)
    
    # Stage 2
    brick_vocabulary = BUILDING_BRICK_VOCAB
    
    basic_finished_structure = run_heuristic(result_grid, brick_vocabulary, CandidateGenerationStrategy.BASIC, minimum_support_ratio)
    informed_finished_structure = run_heuristic(result_grid, brick_vocabulary, CandidateGenerationStrategy.INFORMED, minimum_support_ratio)

    print("\nResults for basic heuristic pipeline")
    print("=======================================")
    print("Final status " + basic_finished_structure.final_status)
    
    print("\nResults for informed heuristic pipeline")
    print("=======================================")
    print("Final status " + informed_finished_structure.final_status)
    print("Support Ratio: " + str(minimum_support_ratio))
    
    # Stage 3
    compare_final_to_result(basic_finished_structure, CandidateGenerationStrategy.BASIC)
    #compare_final_to_result(informed_finished_structure, CandidateGenerationStrategy.INFORMED)
    
    # Stage 1A
    basic_violations = check_structural_support_violations(basic_finished_structure, CandidateGenerationStrategy.BASIC, minimum_support_ratio)
    informed_violations = check_structural_support_violations(informed_finished_structure, CandidateGenerationStrategy.INFORMED, minimum_support_ratio)
    
    generate_violation_clusters(basic_violations)
    
    # Stage 2A - Optimisation FINALLE!!!
    basic_optimisation_statistics = run_optimisation(basic_finished_structure, brick_vocabulary, minimum_support_ratio, MAXIMUM_UNSUPPORTED_DISTANCE_ACCEPTED)
    basic_optimisation_statistics.print_replacement_repair_summary()
    basic_optimisation_statistics.print_final_audit_summary()
    
    # Stage 5 - specific checking for bottle at resolution 32
    if basic_finished_structure.final_status == PlacementResult.STATUS_NO_VALID_CANDIDATES:
        print_blocked_layer_diagnostics(finished_structure=basic_finished_structure)
                
    # Stage 4
    visualise_results(basic_finished_structure.finished_grid, basic_violations)
    
    #visualise_results(informed_finished_structure.finished_grid)

            
def visualise_results(finished_grid: np.ndarray, violations: list[StructuralViolation] | None) -> None:
    if VISUALISE_VIOLATIONS:
        brick_statuses = create_support_visualisation_statuses(violations)
        
    visualiser = BrickConstructionVisualiser(finished_grid, brick_statuses)
    
    visualiser.visualise_complete_model()

def create_support_visualisation_statuses(violations: list[StructuralViolation]) -> dict[int, str]:
    brick_statuses: dict[int, str] = {}
    
    for violation in violations:
        
        if violation.supported_footprint_coordinates_count == 0:
            brick_statuses[violation.brick_id] = BrickConstructionVisualiser.FLOATING
        else:
            brick_statuses[violation.brick_id] = BrickConstructionVisualiser.PARTIALLY_SUPPORTED
        
    return brick_statuses
    
# Stage 5 - checking why models failed
def print_blocked_layer_diagnostics(
    finished_structure: HeuristicResult
) -> None:

    blocked_y, _, _ = (finished_structure.placement_history[-1].crucial_point)

    target_layer = finished_structure.result_grid[blocked_y]

    occupied_layer = (finished_structure.finished_grid[blocked_y] != -1)

    support_layer = (finished_structure.finished_grid[blocked_y - 1] != -1)

    uncovered_layer = (target_layer & ~occupied_layer)

    print("\nTarget layer:")
    print(target_layer.astype(int))

    print("\nOccupied construction layer:")
    print(occupied_layer.astype(int))

    print("\nUncovered target cells:")
    print(uncovered_layer.astype(int))

    print("\nConstructed support layer:")
    print(support_layer.astype(int))
    
# Stage 1A - checking for structural violations
def check_structural_support_violations(finished_structure: HeuristicResult, strategy: CandidateGenerationStrategy, minimum_support_ratio: float, verbose: bool=False) -> list[StructuralViolation]:
    
    detector = StructuralViolationDetector(minimum_support_ratio)
    
    violations = detector.detect_violations(finished_structure.construction_grid)
    
    total_support_deficit = sum(violation.support_diff for violation in violations)
    floating_brick_count = sum(1 for violation in violations if violation.actual_support_ratio == 0.0)
    
    print("Structural Violation Support Check with " + strategy.name + " strategy and minimum support ratio of " + str(minimum_support_ratio))
    print ("================================================")
    print("Total Violations Found: " + str(len(violations)))
    print("Total Support Deficit: " + str(total_support_deficit))
    print("Floating Brick Count: " + str(floating_brick_count))
    
    if verbose:
        print("List of Violations:")
        print("------------------------------------------------")
        for violation in violations:
            print(violation)
        
    return violations
        
def generate_violation_clusters(violations: list[StructuralViolation], verbose: bool=False):
    
    cluster_creator = ViolationGrouper()
    
    clusters = cluster_creator.group_violations(violations)
    
    if verbose:
        print("Structural Violation Clusters")
        print ("=======================================")
    
        print("Amount of clusters " + str(len(clusters)))
    
        for cluster in clusters:
            print("\n" + str(cluster))
            
            print("Violations")
            
            for violation in cluster.violations:
                
                print("Brick ID " + str(violation.brick_id) + " at y:" + str(violation.brick.y) + " z: " + str(violation.brick.z) + " x: " + str(violation.brick.x))

if __name__ == "__main__":
    main(MINIMUM_SUPPORT_RATIO)
    