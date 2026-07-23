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

MODEL_CLASS: str = "sofa"
MODEL_NUMBER: int = 1
MODEL_DATASET: str = "shapenet"

RESOLUTION: int = 16

MINIMUM_SUPPORT_RATIO = 0.5
# Sofas need a support ratio of 0.25

# Stage 1
def create_model_result_grid() -> np.ndarray:
    
    model_path = create_path(MODEL_CLASS, MODEL_NUMBER, MODEL_DATASET)
    
    mesh_voxeliser = MeshVoxeliser(model_path, resolution=RESOLUTION)
    
    voxel_grid = mesh_voxeliser.start()
    
    result_grid = ResultGrid()
    
    result_grid.create_result_grid(voxel_grid)
    
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
    
    pipeline = HeuristicPipeline(result_grid, brick_vocabulary, strategy, minimum_support_ratio)
    
    finished_structure = pipeline.create_structure()
    
    return finished_structure

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
    brick_vocabulary = BASIC_BRICK_VOCABULARY
    
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
    compare_final_to_result(informed_finished_structure, CandidateGenerationStrategy.INFORMED)
    
    if (basic_finished_structure.final_status == PlacementResult.STATUS_NO_VALID_CANDIDATES and informed_finished_structure.final_status == PlacementResult.STATUS_NO_VALID_CANDIDATES):
        minimum_support_ratio -= 0.05
        if (minimum_support_ratio >= 0):
            main(minimum_support_ratio)
        else:
            print("Runtime Has Concluded!")
    
if __name__ == "__main__":
    main(MINIMUM_SUPPORT_RATIO)