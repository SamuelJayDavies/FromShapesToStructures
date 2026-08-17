from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker

class OptimisationStatistics:
    
    NO_GENERATED_CANDIDATES = "NO_GENERATED_CANDIDATES"
    NO_VALID_CANDIDATE = "NO_VALID_CANDIDATE"
    NO_BENEFICIAL_CANDIDATE = "NO_BENEFICIAL_CANDIDATE"
    
    def __init__(self) -> None:
        
        # Construction
        self.total_brick_count = 0
        
        # First Structural Audit (basic audit)
        self.initial_violation_count = 0
        self.initial_floating_brick_count = 0
        self.initial_partially_supported_violation_count = 0
        
        self.initial_violation_brick_ids: set[int] = set()
        self.initial_floating_brick_ids: set[int] = set()
        self.initial_partially_supported_violation_brick_ids: set[int] = set()
        
        # Cluster Audit
        self.initial_cluster_count = 0
        self.initial_disconnected_cluster_count = 0
        self.initial_single_anchored_cluster_count = 0
        self.initial_multi_anchored_cluster_count = 0
        
        self.initial_required_repair_cluster_count = 0
        
        self.structurally_sound_weak_brick_count = 0
        self.structurally_sound_weak_brick_ids: set[int] = set()
        
        # Replacement Repair Stage
        self.replacement_attempt_count = 0
        self.successful_replacement_count = 0
        self.failed_replacement_count = 0
        
        # Post Results
        self.generated_replacement_candidate_count = 0
        self.valid_replacement_candidate_count = 0
        
        self.no_generated_replacement_candidate_count = 0
        self.no_valid_replacement_candidate_count = 0
        self.no_beneficial_replacement_candidate_count = 0
        
        self.support_improving_replacement_count = 0
        self.grounded_attachment_replacement_count = 0
        
        # Final Results
        self.final_violaiton_brick_ids: set[int] = set()
        
        self.final_violation_count = 0
        self.final_floating_brick_count = 0
        self.final_required_repair_cluster_count = 0
        
        self.resolved_violation_count = 0
        self.new_violation_count = 0
        self.unresolved_cluster_count = 0
        
    def record_initial_basic_audit(self, total_brick_count: int, violations: list) -> None:
        
        self.total_brick_count = total_brick_count
        
        self.initial_violation_brick_ids = {violation.brick_id for violation in violations}
        
        self.initial_floating_brick_ids = {violation.brick_id for violation in violations if violation.supported_footprint_coordinates_count == 0}
        
        self.initial_partially_supported_violation_brick_ids = {violation.brick_id for violation in violations if violation.supported_footprint_coordinates_count > 0}
        
        self.initial_violation_count = len(self.initial_violation_brick_ids)
        self.initial_floating_brick_count = len(self.initial_floating_brick_ids)
        self.initial_partially_supported_violation_count = len(self.initial_partially_supported_violation_brick_ids)
        
    def record_initial_cluster_audit(self, cluster_audit_results: list[tuple]) -> None:
        
        self.initial_cluster_count = len(cluster_audit_results)
        
        self.initial_disconnected_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_DISCONNECTED)
        self.initial_single_anchored_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_SINGLE_ANCHORED)
        self.initial_multi_anchored_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_MULTI_ANCHORED)
        
        self.initial_required_repair_cluster_count = sum(1 for _, _, required_repair in cluster_audit_results if required_repair)
        self.structurally_sound_weak_brick_ids = (self._get_structurally_sound_weak_brick_ids(cluster_audit_results))
        self.structurally_sound_weak_brick_count = len(self.structurally_sound_weak_brick_ids)
        
    def record_final_basic_audit(self, violations: list) -> None:
        self.final_violation_brick_ids = {violation.brick_id for violation in violations if violation.brick_id}
        
        self.final_violation_count = len(self.final_violation_brick_ids)
        
        self.final_floating_brick_count = len({violation.brick_id for violation in violations if violation.supported_footprint_coordinates_count == 0 and violation.brick_id not in self.structurally_sound_weak_brick_ids})
        
        self.resolved_violation_count = len(self.get_resolved_initial_violation_brick_ids())
        
        self.new_violation_count = len(self.get_new_violation_brick_ids())
        
    def record_final_cluster_audit(self, cluster_repair_results: list[tuple]) -> None:
        self.final_required_repair_cluster_count = sum(1 for _, required_repair in cluster_repair_results if required_repair)
        self.unresolved_cluster_count = self.final_required_repair_cluster_count
    
    def _get_structurally_sound_weak_brick_ids(self, cluster_audit_result: list[tuple]) -> set[int]:
        
        results: set[int] = set()
        
        for cluster, classification, required_repair in cluster_audit_result:
            
            if not required_repair and classification in {StructuralGroundedChecker.CLASSIFICATION_SINGLE_ANCHORED, StructuralGroundedChecker.CLASSIFICATION_MULTI_ANCHORED}:
                
                for violation in cluster.violations:
                    results.add(violation.brick_id)
        
        return results
    
    def get_structurally_accepted_floating_brick_ids(self) -> set[int]:
        return self.initial_floating_brick_ids & self.structurally_sound_weak_brick_ids
    
    def get_structurally_accepted_partially_supported_brick_ids(self) -> set[int]:
        return self.initial_partially_supported_violation_brick_ids & self.structurally_sound_weak_brick_ids
    
    def get_structurally_accepted_weak_brick_ids(self) -> set[int]:
        return self.initial_violation_brick_ids & self.structurally_sound_weak_brick_ids
    
    def get_resolved_initial_violation_brick_ids(self) -> set[int]:
        return self.initial_violation_brick_ids - self.final_violation_brick_ids
    
    def get_new_violation_brick_ids(self) -> set[int]:
        return self.final_violation_brick_ids - self.initial_violation_brick_ids
    
    def get_structurally_accounted_for_initial_violation_brick_ids(self) -> set[int]:
        return self.get_structurally_accepted_weak_brick_ids() | self.get_resolved_initial_violation_brick_ids()
    
    def get_structurally_unaccounted_for_initial_violation_brick_ids(self) -> set[int]:
        return self.initial_violation_brick_ids - self.get_structurally_accounted_for_initial_violation_brick_ids()
    
    def get_final_actual_violating_brick_count(self) -> int:
        return len(self.final_violation_brick_ids - self.structurally_sound_weak_brick_ids)
        
    def get_structural_accounting_ratio(self) -> float:
        if self.initial_violation_count == 0:
            return 1.0
        else:
            account_for_num = len(self.get_structurally_accounted_for_initial_violation_brick_ids())
            
            return account_for_num / self.initial_violation_count
    
    def record_replacement_attempt(self) -> None:
        self.replacement_attempt_count += 1
        
    def record_failed_replacement(self, failure_reason: str) -> None:
        
        self.failed_replacement_count += 1
        
        if failure_reason == self.NO_GENERATED_CANDIDATES:
            self.no_generated_replacement_candidate_count += 1
        elif failure_reason == self.NO_VALID_CANDIDATE:
            self.no_valid_replacement_candidate_count += 1
        elif failure_reason == self.NO_BENEFICIAL_CANDIDATE:
            self.no_beneficial_replacement_candidate_count += 1
        else:
            raise ValueError("Structural Repair failed for an unknown reason: " + failure_reason)
        
    def record_successful_replacement(self, support_improvement: float, grounded_attachment_count: int) -> None:
        self.successful_replacement_count += 1
        
        if support_improvement > 0:
            self.support_improving_replacement_count += 1
        if grounded_attachment_count > 0:
            self.grounded_attachment_replacement_count += 1
            
    def record_generated_replacement_candidates(self, candidate_count: int) -> None:
        self.generated_replacement_candidate_count += candidate_count
        
    def record_valid_replacement_candidates(self, candidate_count: int) -> None:
        self.valid_replacement_candidate_count += candidate_count
    
    def print_initial_audit_summary(self) -> None:
        
        print("\n INITIAL OPTIMISATION STRUCTURAL AUDIT")
        print("----------------------------------------")
        
        print("Total Brick Count: " + str(self.total_brick_count))
        
        print("Initial Violating Brick Count: " + str(self.initial_violation_count))
        print("Initial Floating Brick Count: " + str(self.initial_floating_brick_count))
        print("Initial Partially-Supported Violation Count: " + str(self.initial_partially_supported_violation_count))
        print("")
        
        print("Initial Violation Cluster Count: " + str(self.initial_cluster_count))
        print("")
        
        print("Disconnected Clusters: " + str(self.initial_disconnected_cluster_count))
        print("Single-anchored Clusters: " + str(self.initial_single_anchored_cluster_count))
        print("Multi-anchored Clusters: " + str(self.initial_multi_anchored_cluster_count))
        print("")
        
        print("Required Repair Clusters: " + str(self.initial_required_repair_cluster_count))
        
        print("Structurally sound weak bricks (total): " + str(self.structurally_sound_weak_brick_count))
        print("Weak Bricks - Locally Floating but Structurally Accepted: " + str(len(self.get_structurally_accepted_floating_brick_ids())))
        print("Weak Bricks - Partially Supported but Structurally Accepted: " + str(len(self.get_structurally_accepted_partially_supported_brick_ids())))
        
    def print_replacement_repair_summary(self) -> None:
        
        print("\nREPLACEMENT REPAIR RESULTS")
        print("----------------------------")
        
        print("Replacement Attempts: " + str(self.replacement_attempt_count))
        print("Generated Replacement Candidates: " + str(self.generated_replacement_candidate_count))
        print("Valid Replacement Candidates: " + str(self.valid_replacement_candidate_count))
        print("Successful Replacements: " + str(self.successful_replacement_count))
        print("")
        print("Failed Replacements: " + str(self.failed_replacement_count))
        print("Failures - No Generated Candidates: " + str(self.no_generated_replacement_candidate_count))
        print("Failures - No Valid Candidates: " + str(self.no_valid_replacement_candidate_count))
        print("Failures - No Beneficial Candidate: " + str(self.no_beneficial_replacement_candidate_count))
        print("")
        print("Replacments - That Improved Support: " + str(self.support_improving_replacement_count))
        print("Replacements - That Improved Grounded-Attachment: " + str(self.grounded_attachment_replacement_count))
        print("Unresolved Repair-Required Clusters: " + str(self.unresolved_cluster_count))
        
    def print_final_audit_summary(self) -> None:
        
        structurally_accepted_floating_ids = self.get_structurally_accepted_floating_brick_ids()
        
        structurally_accepted_partially_supported_ids = self.get_structurally_accepted_partially_supported_brick_ids()
        
        resolved_initial_violation_ids = self.get_resolved_initial_violation_brick_ids()
        
        accounted_for_ids = self.get_structurally_accounted_for_initial_violation_brick_ids()
        
        unaccounted_for_ids = self.get_structurally_unaccounted_for_initial_violation_brick_ids()
        
        print("\nFINAL OPTIMISATION STRUCTURAL AUDIT")
        print("-------------------------------------")
        
        print("Initial Violating Brick Count: " + str(self.initial_violation_count))
        print("Final Violating Brick Count: " + str(self.get_final_actual_violating_brick_count()))
        print("")
        
        print("Initial Locally Floating Brick Count: " + str(self.initial_floating_brick_count))
        print("Final Locally Floating but Structurally Accepted Brick Count: " + str(len(structurally_accepted_floating_ids)))
        print("")
        
        print("Initial Partially-Supported Brick Count: " + str(self.initial_partially_supported_violation_count))
        print("Final Partially-Supported but Structurally Accepted Brick Count: " + str(len(structurally_accepted_partially_supported_ids)))
        print("")
        
        print("Initial Violations Resolved Through Modification: " + str(len(resolved_initial_violation_ids)))
        print("Initial Violations Structurally Accounted For: " + str(len(accounted_for_ids)))
        print("Initial Violations Structurally Unaccounted For: " + str(len(unaccounted_for_ids)))
        print("")
        
        print("Structural Accounting Ratio: " + str(round(self.get_structural_accounting_ratio(), 4)))
        print("")
        
        print("New Local Violations Introduced: " + str(self.new_violation_count))
        print("Final Locally Floating Brick Count: " + str(self.final_floating_brick_count))
        print("")
        
        print("Initial Required Repair Clusters: " + str(self.initial_required_repair_cluster_count))
        print("Final Required Repair Clusters: " + str(self.final_required_repair_cluster_count))
        print("Unresolved Clusters: " + str(self.unresolved_cluster_count))