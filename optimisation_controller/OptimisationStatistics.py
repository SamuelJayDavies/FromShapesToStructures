from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker

class OptimisationStatistics:
    
    def __init__(self) -> None:
        
        # Construction
        self.total_brick_count = 0
        
        # First Structural Audit (basic audit)
        self.initial_violation_count = 0
        self.initial_floating_brick_count = 0
        self.initial_partially_supported_violation_count = 0
        
        self.initial_violation_brick_ids: set[int] = set()
        
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
        
        self.support_improving_replacement_count = 0
        self.grounded_attachment_replacement_count = 0
        
        # Final Results
        self.final_violation_count = 0
        self.final_floating_brick_count = 0
        self.final_required_repair_cluster_count = 0
        
        self.resolved_violation_count = 0
        self.new_violation_count = 0
        self.unresolved_cluster_count = 0
        
    def record_initial_basic_audit(self, total_brick_count: int, violations: list) -> None:
        
        self.total_brick_count = total_brick_count
        
        self.initial_violation_brick_ids = {violation.brick_id for violation in violations}
        
        self.initial_violation_count = len(self.initial_violation_brick_ids)
        
        # Maybe change this later to unqiue bricks
        self.initial_floating_brick_count = sum(1 for violation in violations if violation.supported_footprint_coordinates_count == 0)
        
        self.initial_partially_supported_violation_count = sum(1 for violation in violations if violation.supported_footprint_coordinates_count > 0)
        
    def record_initial_cluster_audit(self, cluster_audit_results: list[tuple]) -> None:
        
        self.initial_cluster_count = len(cluster_audit_results)
        
        self.initial_disconnected_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_DISCONNECTED)
        self.initial_single_anchored_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_SINGLE_ANCHORED)
        self.initial_multi_anchored_cluster_count = sum(1 for _, classification, _ in cluster_audit_results if classification == StructuralGroundedChecker.CLASSIFICATION_MULTI_ANCHORED)
        
        self.initial_required_repair_cluster_count = sum(1 for _, _, required_repair in cluster_audit_results if required_repair)
        self.structurally_sound_weak_brick_ids = (self._get_structurally_sound_weak_brick_ids(cluster_audit_results))
        self.structurally_sound_weak_brick_count = len(self.structurally_sound_weak_brick_ids)
    
    def _get_structurally_sound_weak_brick_ids(self, cluster_audit_result: list[tuple]) -> set[int]:
        
        results: set[int] = set()
        
        for cluster, classification, required_repair in cluster_audit_result:
            
            if not required_repair and classification in {StructuralGroundedChecker.CLASSIFICATION_SINGLE_ANCHORED, StructuralGroundedChecker.CLASSIFICATION_MULTI_ANCHORED}:
                
                for violation in cluster.violations:
                    results.add(violation.brick_id)
        
        return results
    
    def print_initial_audit_summary(self) -> None:
        
        print("\n INITIAL OPTIMISATION STRUCTURAL AUDIT")
        print("----------------------------------------")
        
        print("Total Brick Count: " + str(self.total_brick_count))
        
        print("Initial Violating Brick Count: " + str(self.initial_violation_count))
        print("Initial Floating Brick Count: " + str(self.initial_floating_brick_count))
        print("Initial Partially-Supported Violation Count: " + str(self.initial_partially_supported_violation_count))
        
        print("Initial Violation Cluster Count: " + str(self.initial_cluster_count))
        
        print("Disconnected Clusters: " + str(self.initial_disconnected_cluster_count))
        print("Single-anchored Clusters: " + str(self.initial_single_anchored_cluster_count))
        print("Multi-anchored Clusters: " + str(self.initial_multi_anchored_cluster_count))
        
        print("Required Repair Clusters: " + str(self.initial_required_repair_cluster_count))
        
        print("Structurally sound weak bricks: " + str(self.structurally_sound_weak_brick_count))