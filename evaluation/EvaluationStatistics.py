import numpy as np

from brick_placement.ConstructionGrid import ConstructionGrid

from brick.Brick import Brick
from optimisation_controller.StructuralViolationDetector import StructuralViolationDetector

class EvaluationStatistics:
    
    def __init__(self, construction_grid: ConstructionGrid, violation_detector: StructuralViolationDetector) -> None:
        
        self.construction_grid = construction_grid
        self.violation_detector = violation_detector
        
        # Visual Fidelity
        self.target_voxel_count = 0
        self.correctly_covered_voxel_count = 0
        self.missed_target_voxel_count = 0
        self.outside_target_voxel_count = 0
        
        self.coverage_ratio = 0.0
        self.reconstruction_completed = False
        
        # Brick Minimisation
        self.active_brick_count = 0
        self.covered_voxels_per_brick = 0.0
        
        # Structural Integrity
        self.local_support_violation_count = 0
        self.floating_brick_count = 0
        self.partially_supported_brick_count = 0
        
        self.total_support_deficit = 0.0
        self.mean_support_ratio = 0.0
        
        # Computational Effectiveness
        self.total_runtime_seconds = 0.0
        self.covered_voxels_per_second = 0.0
        
    def evaluate_geometry(self) -> None:
        
        target_grid = self.construction_grid.result_grid
        constructed_grid = self.construction_grid.convert_to_result_grid()
        
        self.target_voxel_count = int(np.count_nonzero(target_grid))
        
        self.correctly_covered_voxel_count = int(np.count_nonzero(target_grid & constructed_grid))
        
        self.missed_target_voxel_count = int(np.count_nonzero(target_grid & ~constructed_grid))
        
        self.outside_target_voxel_count = int(np.count_nonzero(~target_grid & constructed_grid))
        
        if self.target_voxel_count == 0:
            self.coverage_ratio = 1.0
        else:
            self.coverage_ratio = (self.correctly_covered_voxel_count / self.target_voxel_count)
            
        self.reconstruction_completed = self.missed_target_voxel_count == 0
        
    def evaluate_brick_minimisation(self) -> None:
        
        self.active_brick_count = self.construction_grid.get_active_brick_count()
        
        if self.active_brick_count == 0:
            self.covered_voxels_per_brick = 0.0
        else:
            self.covered_voxels_per_brick = self.correctly_covered_voxel_count / self.active_brick_count
            
    def _get_active_bricks(self) -> list[Brick]:
        
        return [self.construction_grid.placed_bricks[brick_id] for brick_id in self.construction_grid.get_active_brick_ids()]
    
    def evaluate_local_structural_integrity(self) -> None:
        
        violations = self.violation_detector.detect_violations(self.construction_grid)
        
        self.local_support_violation_count = len(violations)
        
        self.floating_brick_count = sum(1 for violation in violations if violation.supported_footprint_coordinates_count == 0)
        
        self.partially_supported_brick_count = sum(1 for violation in violations if violation.supported_footprint_coordinates_count > 0)
        
        self.total_support_deficit = sum(violation.support_diff for violation in violations)
        
        active_bricks = self._get_active_bricks()
        
        if not active_bricks:
            self.mean_support_ratio = 0.0
        else:
            total_support_ratio = sum(self.construction_grid.calculate_support_ratio(brick) for brick in active_bricks)
            
            self.mean_support_ratio = total_support_ratio / len(active_bricks)
            
    def evaluate_computational_effectiveness(self, total_runtime_seconds: float) -> None:
        
        if total_runtime_seconds < 0:
            raise ValueError("That cannot happen, runtime cannot be negative!")
        
        self.total_runtime_seconds = total_runtime_seconds
        
        if total_runtime_seconds == 0:
            self.covered_voxels_per_second = 0.0
        else:
            self.covered_voxels_per_second = self.correctly_covered_voxel_count / total_runtime_seconds
            
    def evaluate(self, total_runtime_seconds: float) -> None:
        
        self.evaluate_geometry()
        self.evaluate_brick_minimisation()
        self.evaluate_local_structural_integrity()
        self.evaluate_computational_effectiveness(total_runtime_seconds)
        
    def print_summary(self) -> None:
        
        print("\nEvaluation Framework Results")
        print("==============================")
        
        print("\nVISUAL SIMILARITY")
        print("-------------------")
        print("Target Voxels: " + str(self.target_voxel_count))
        print("Correctly Covered Voxels: " + str(self.correctly_covered_voxel_count))
        print("Missed Target Voxels: " + str(self.missed_target_voxel_count))
        print("Outside Target Voxels: " + str(self.outside_target_voxel_count))
        print("Coverage Ratio: " + str(round(self.coverage_ratio, 4)))
        print("Reconstruction Completed: " + str(self.reconstruction_completed))
        
        print("\nSTRUCTURAL INTEGRITY")
        print("----------------------")
        print("Local Support Violations: " + str(self.local_support_violation_count))
        print("Floating Brick Count: " + str(self.floating_brick_count))
        print("Partially Supported Brick Count " + str(self.partially_supported_brick_count))
        print("Total Support Deficit: " + str(round(self.total_support_deficit, 4)))
        print("Mean Support Ratio: " + str(round(self.mean_support_ratio, 4)))
        
        print("\nBRICK MINIMISATION")
        print("--------------------")
        print("Active Brick Count: " + str(self.active_brick_count))
        print("Covered Voxels Per Brick: " + str(round(self.covered_voxels_per_brick, 4)))
        
        print("\nCOMPUTATIONAL EFFECTIVENESS")
        print("-----------------------------")
        print("Total Runtime: " + str(round(self.total_runtime_seconds, 4)) + " seconds")
        print("Covered Voxels Per Second: " + str(round(self.covered_voxels_per_second, 4)))