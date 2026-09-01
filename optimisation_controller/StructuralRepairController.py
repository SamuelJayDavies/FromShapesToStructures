from optimisation_controller.ViolationCluster import ViolationCluster
from brick_placement.ConstructionGrid import ConstructionGrid
from optimisation_controller.StructuralViolationDetector import StructuralViolationDetector
from optimisation_controller.ViolationGrouper import ViolationGrouper
from optimisation_controller.StructuralRepairEvaluator import StructuralRepairEvaluator
from optimisation_controller.StructuralRepairSelector import StructuralRepairSelector
from optimisation_controller.ReplacementCandidateGenerator import ReplacementCandidateGenerator
from optimisation_controller.ReplacementCandidateEvaluator import ReplacementCandidateEvaluator

from optimisation_controller.OptimisationStatistics import OptimisationStatistics

import numpy as np

import copy

from brick.Brick import Brick

class StructuralRepairController:
    
    NO_GENERATED_CANDIDATES = "NO_GENERATED_CANDIDATES"
    NO_VALID_CANDIDATE = "NO_VALID_CANDIDATE"
    NO_BENEFICIAL_CANDIDATE = "NO_BENEFICIAL_CANDIDATE"
    
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
        self.optimisation_statistics.record_replacement_attempt()
        
        target_violation = self.repair_selector.get_repair_target(cluster)
                    
        replacement_candidates = self.replacement_candidate_generator.generate_replacement_candidates(target_violation)
        
        self.optimisation_statistics.record_generated_replacement_candidates(len(replacement_candidates))
        
        if not replacement_candidates:
            self.optimisation_statistics.record_failed_replacement(StructuralRepairController.NO_GENERATED_CANDIDATES)
            return False
        
        candidate_evaluations: list[tuple[Brick, float, int, int]] = []
        
        for candidate in replacement_candidates:
            
            candidate_is_valid = self.replacement_candidate_evaluator.validate_candidate_does_not_conflict(candidate, target_violation)
            
            if candidate_is_valid:
                
                support_improvement = self.replacement_candidate_evaluator.get_support_ratio_improvement(candidate, target_violation)
                attachment_count = self.replacement_candidate_evaluator.get_independent_grounded_attachment_count(candidate, cluster)
                outside_target_count = self.replacement_candidate_evaluator.get_outside_target_coordinate_count(candidate)
                
                candidate_evaluations.append((candidate, support_improvement, attachment_count, outside_target_count))
                
        self.optimisation_statistics.record_valid_replacement_candidates(len(candidate_evaluations))
        
        if not candidate_evaluations:
            self.optimisation_statistics.record_failed_replacement(self.NO_VALID_CANDIDATE)
            return False
        
        best_candidate = self.replacement_candidate_evaluator.select_best_candidate(candidate_evaluations)
        
        if best_candidate is None:
            self.optimisation_statistics.record_failed_replacement(self.NO_BENEFICIAL_CANDIDATE)
            return False
        else:
            selected_evaluation = next(evaluation for evaluation in candidate_evaluations if evaluation[0] is best_candidate)
            
            if selected_evaluation is None:
                raise ValueError("Selected replacement candidate is missings its evaluation")
            else:
                _, support_improvement, attachment_count, outside_target_count = selected_evaluation
                self.construction_grid.replace_brick(target_brick_id=target_violation.brick_id, replacement_brick=best_candidate)
                self.optimisation_statistics.record_successful_replacement(support_improvement, attachment_count)
                return True
        
    def repair_with_replacement(self, maximum_iterations: int = 100) -> bool:
        
        self.record_initial_structural_statistics()
        self.optimisation_statistics.print_initial_audit_summary()
        
        repair_iteration = 0
        
        unresolved_cluster_ids: set[tuple[int, ...]] = set()
        
        while repair_iteration < maximum_iterations:
            
            required_repair_clusters = self.get_required_repair_clusters()
            
            if not required_repair_clusters:
                self.optimisation_statistics.unresolved_cluster_count = 0
                
                self.record_final_structural_statistics()
                return True
            else:
                current_required_cluster_ids = {self._get_cluster_unique_id(cluster) for cluster in required_repair_clusters}
                unresolved_cluster_ids.intersection_update(current_required_cluster_ids)
                repairable_clusters = [cluster for cluster in required_repair_clusters if self._get_cluster_unique_id(cluster) not in unresolved_cluster_ids]
                
                if not repairable_clusters:
                    self.optimisation_statistics.unresolved_cluster_count = len(required_repair_clusters)
                    
                    self.record_final_structural_statistics()
                    return False
                
                current_cluster = repairable_clusters[0]
                current_cluster_id = self._get_cluster_unique_id(current_cluster)
                
                sucessful_placement = self.attempt_replacement_repair(current_cluster)
                
                repair_iteration += 1
                
                if not sucessful_placement:
                    unresolved_cluster_ids.add(current_cluster_id)
                

        raise RuntimeError("Exceeded maximum repair iterations")
    
    def _get_cluster_unique_id(self, cluster: ViolationCluster) -> tuple[int, ...]:
        return tuple(sorted(violation.brick_id for violation in cluster.violations))
    
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
            
    def record_final_structural_statistics(self) -> None:
        final_violations = self.violation_detector.detect_violations(self.construction_grid)
        
        self.optimisation_statistics.record_final_basic_audit(final_violations)
        
        if not final_violations:
            self.optimisation_statistics.record_final_cluster_audit([])
        else:
            final_clusters = self.violation_grouper.group_violations(final_violations)
            
            cluster_repair_results: list[tuple[ViolationCluster, bool]] = []
            
            for cluster in final_clusters:
                
                required_repair = self.repair_evaluator.requires_repair(cluster)
                
                cluster_repair_results.append((cluster, required_repair))
                
            self.optimisation_statistics.record_final_cluster_audit(cluster_repair_results)
            
    def attempt_merge_repair(self, cluster: ViolationCluster) -> bool:
        
        priority_target = self.repair_selector.get_repair_target(cluster)
        
        ordered_target_violations = [priority_target]
        
        for violation in cluster.violations:
            if violation.brick_id != priority_target.brick_id:
                ordered_target_violations.append(violation)
                
        merge_evaluations: list[tuple[Brick, int, int, float, float, int]] = []
        
        for target_violation in ordered_target_violations:
            
            merge_candidates = (self.replacement_candidate_generator.generate_merge_candidates(self.construction_grid, target_violation))
            
            if not merge_candidates:
                continue
            
            target_evaluations = (self.replacement_candidate_evaluator.evaluate_all_merge_candidates(merge_candidates, target_violation, cluster))
            
            merge_evaluations.extend(target_evaluations)
        
        if not merge_evaluations:
            return False
        
        best_merge = self.replacement_candidate_evaluator.select_best_merge_candidate(merge_evaluations)
        
        if best_merge is None:
            return False
        
        merged_brick, target_brick_id, neighbour_brick_id, _, _, _ = best_merge
        
        self.construction_grid.merge_bricks(target_brick_id, neighbour_brick_id, merged_brick)
        
        return True
    
    def repair_with_merging(self, maximum_iterations: int = 100) -> bool:
        
        merge_iteration = 0
        
        unresolved_cluster_ids: set[tuple[int, ...]] = set()
        
        while merge_iteration < maximum_iterations:
            
            required_repair_clusters = self.get_required_repair_clusters()
            
            if not required_repair_clusters:
                self.record_final_structural_statistics()
                return True
            
            current_required_cluster_ids = {self._get_cluster_unique_id(cluster) for cluster in required_repair_clusters}
            
            unresolved_cluster_ids.intersection_update(current_required_cluster_ids)
            
            repairable_clusters = [cluster for cluster in required_repair_clusters if self._get_cluster_unique_id(cluster) not in unresolved_cluster_ids]
            
            if not repairable_clusters:
                self.record_final_structural_statistics()
                return False
            
            current_cluster = repairable_clusters[0]
            
            current_cluster_id = self._get_cluster_unique_id(current_cluster)
            
            successful_merge = self.attempt_merge_repair(current_cluster)
            
            merge_iteration += 1
            
            if not successful_merge:
                unresolved_cluster_ids.add(current_cluster_id)
                
        raise RuntimeError("Maximum merge repair iterations exceeded")