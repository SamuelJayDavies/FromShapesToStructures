from optimisation_controller.ViolationCluster import ViolationCluster
from optimisation_controller.UnsupportedDistanceEvaluator import UnsupportedDistanceEvaluator

class StructuralRepairSelector:
    
    def __init__(self, distance_eval: UnsupportedDistanceEvaluator):
        self.unsupported_distance_evaluator = distance_eval
        
    
    def get_violation_containing_coordinate(self, cluster: ViolationCluster, coordinate: tuple[int, int, int]) -> ViolationCluster:
        
        matching_violations = []
        
        for violation in cluster.violations:
            if coordinate in violation.unsupported_footprint_coordinates:
                matching_violations.append(violation)
        
        if len(matching_violations) == 0:
            raise ValueError("The cluster provided does not contain the supplied unsupported coordinate")
        elif len(matching_violations) > 1:
            raise ValueError("Multiple violations contain the same coordinate")
        else:
            return matching_violations[0]
        
    def get_second_repair_target_violation_choice(self, cluster: ViolationCluster) -> ViolationCluster:
        
        if not cluster.violations:
            raise ValueError("Cannot select a repair target from a non-existent violation cluster")
        else:
            return min(cluster.violations, key=lambda violation: (violation.layer, violation.brick_id))
        
    def get_reapir_target_violation(self, cluster: ViolationCluster) -> ViolationCluster:
        
        if not cluster.violations:
            raise ValueError("Cannot select a repair target from an empty violation cluster")
        else:
            furthest_coordinate = (self.unsupported_distance_evaluator.get_furthest_unsupported_coordinate(cluster))
            
            if furthest_coordinate is None:
                return self.get_second_repair_target_violation_choice(cluster)
            else:
                return self.get_violation_containing_coordinate(cluster, furthest_coordinate)
            