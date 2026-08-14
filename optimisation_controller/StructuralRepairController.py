from optimisation_controller.ViolationCluster import ViolationCluster
from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolationDetector import StructuralViolationDetector
from optimisation_controller.ViolationGrouper import ViolationGrouper
from optimisation_controller.StructuralRepairEvaluator import StructuralRepairEvaluator
from optimisation_controller.StructuralRepairSelector import StructuralRepairSelector
from optimisation_controller.ReplacementCandidateGenerator import ReplacementCandidateGenerator
from optimisation_controller.ReplacementCandidateEvaluator import ReplacementCandidateEvaluator

from optimisation_controller.OptimisationStatistics import OptimisationStatistics

from brick.Brick import Brick

class StructuralRepairController:
    
    def __init__(self, construction_grid: ConstructionGrid, violation_detector: StructuralViolationDetector, violation_grouper: ViolationGrouper, structural_repair_evaluator: StructuralRepairEvaluator, repair_selector: StructuralRepairSelector, 
                 replacement_candidate_generator: ReplacementCandidateGenerator, replacement_candidate_evaluator: ReplacementCandidateEvaluator, optimisation_statistics: OptimisationStatistics):
        
        self.construction_grid = construction_grid
        self.violation_detector = violation_detector
        self.violation_grouper = violation_grouper
        self.repair_evaluator = structural_repair_evaluator
        self.repair_selector = repair_selector
        self.replacement_candidate_generator = replacement_candidate_generator
        self.replacement_candidate_evaluator = replacement_candidate_evaluator
        self.optimisation_statistics = optimisation_statistics
        
    def get_required_repair_clusters(self) -> list[ViolationCluster]:
        
        violations = self.violation_detector.detect_violations(self.construction_grid)
        
        if not violations:
            return []
        else:
            clusters = self.violation_grouper.group_violations(violations)
            
            required_repair_clusters: list[ViolationCluster] = []
            
            for cluster in clusters:
                if self.repair_evaluator.requires_repair(cluster):
                    required_repair_clusters.append(cluster)
                    
            return required_repair_clusters
        
    def attempt_replacement_repair(self, cluster: ViolationCluster) -> bool:
        """ Attempts to structural repair a violation weak cluster with a single-brick replacement

        Args:
            cluster (ViolationCluster): The violation cluster being repaired

        Returns:
            bool: True if the replacement was successful, False if not valid structural repair could be found
        """
        
        target_violation = self.repair_selector.get_repair_target(cluster)
        replacement_candidates = self.replacement_candidate_generator.generate_replacement_candidates(target_violation)
        
        candidate_evaluations: list[tuple[Brick, float, int, int]] = []
        
        for candidate in replacement_candidates:
            
            candidate_is_valid = self.replacement_candidate_evaluator.validate_candidate_does_not_conflict(candidate, target_violation)
            
            if candidate_is_valid:
                
                support_improvement = self.replacement_candidate_evaluator.get_support_ratio_improvement(candidate, target_violation)
                attachment_count = self.replacement_candidate_evaluator.get_independent_grounded_attachment_count(candidate, cluster)
                outside_target_count = self.replacement_candidate_evaluator.get_outside_target_coordinate_count(candidate)
                
                candidate_evaluations.append((candidate, support_improvement, attachment_count, outside_target_count))
        
        best_candidate = self.replacement_candidate_evaluator.select_best_candidate(candidate_evaluations)
        
        if best_candidate is None:
            return False
        else:
            self.construction_grid.replace_brick(target_brick_id=target_violation.brick_id, replacement_brick=best_candidate)
            
            return True
        
    def repair_with_replacement(self, maximum_iterations: int = 100) -> bool:
        
        self.record_initial_structural_statistics()
        self.optimisation_statistics.print_initial_audit_summary()
        
        repair_iteration = 0
        
        while repair_iteration < maximum_iterations:
            
            required_repair_clusters = self.get_required_repair_clusters()
            
            if not required_repair_clusters:
                return True
            else:
                
                current_cluster = required_repair_clusters[0]
                
                sucessful_placement = self.attempt_replacement_repair(current_cluster)
                
                if not sucessful_placement:
                    return False
                
                repair_iteration += 1
        
        raise RuntimeError("Exceeded maximum repair iterations")
    
    def record_initial_structural_statistics(self) -> None:
        
        initial_violations = self.violation_detector.detect_violations(self.construction_grid)
        self.optimisation_statistics.record_initial_basic_audit(total_brick_count=len(self.construction_grid.placed_bricks), violations=initial_violations)
        
        if not initial_violations:
            self.optimisation_statistics.record_initial_cluster_audit([])
            return
        else:
            initial_clusters = self.violation_grouper.group_violations(initial_violations)
            
            cluster_audit_result: list[tuple[ViolationCluster, str, bool]] = []
            
            for cluster in initial_clusters:
                
                grounded_classificaiton = self.repair_evaluator.grounded_checker.classify_cluster_support(cluster)
                
                required_repair = self.repair_evaluator.requires_repair(cluster)
                
                cluster_audit_result.append((cluster, grounded_classificaiton, required_repair))
            
            self.optimisation_statistics.record_initial_cluster_audit(cluster_audit_result)