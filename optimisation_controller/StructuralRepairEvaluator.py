from optimisation_controller.StructuralGroundedChecker import StructuralGroundedChecker
from optimisation_controller.UnsupportedDistanceEvaluator import UnsupportedDistanceEvaluator

from optimisation_controller.ViolationCluster import ViolationCluster

class StructuralRepairEvaluator:
    
    REPAIR_DISCONNECTED = "DISCONNECTED"
    REPAIR_EXCESSIVE_DISTANCE = "EXCESSIVE_UNSUPPORTED_DISTANCE"
    
    def __init__(self, grounded_checker: StructuralGroundedChecker, distance_evaluator: UnsupportedDistanceEvaluator, maximum_unsupported_distance_accepted: int) -> None:
        
        if maximum_unsupported_distance_accepted < 0:
            raise ValueError("Maximum permitted distance cannot be less than zero")
        else:
            self.grounded_checker = grounded_checker
            self.distance_evaluator = distance_evaluator
            self.maximum_unsupported_distance_accepted = maximum_unsupported_distance_accepted
            
    def get_repair_classification(self, cluster: ViolationCluster) -> str | None:
        """ Returns why the violation cluster requires a repair either that the cluster is disconnected or because it has an excessive unsupported distance

        Args:
            cluster (ViolationCluster): The violation cluster being classified for repair

        Returns:
            str | None: The classification of DISCONNECTED or EXCESSIVE_DISTANCE or None (if the cluster does not need a repair)
        """
        grounded_classification = self.grounded_checker.classify_cluster_grounding(cluster)
        
        if grounded_classification == StructuralGroundedChecker.CLASSIFICATION_DISCONNECTED:
            return self.REPAIR_DISCONNECTED
        elif grounded_classification not in (StructuralGroundedChecker.CLASSIFICATION_SINGLE_ANCHORED, StructuralGroundedChecker.CLASSIFICATION_MULTI_ANCHORED):
            raise ValueError("Unknown structural grounding classification: " + grounded_classification)
        else:
            
            maximum_unsupported_distance = self.distance_evaluator.get_maximum_unsupported_distance(cluster)
            
            if maximum_unsupported_distance is None:
                raise ValueError("Anchored cluster is missing an unsupported distance")
            
            if maximum_unsupported_distance > self.maximum_unsupported_distance_accepted:
                return self.REPAIR_EXCESSIVE_DISTANCE
            else:
                return None
                
    def requires_repair(self, cluster: ViolationCluster) -> bool:
        """ Returns if the violation cluster requires a structural repair under the current grounding and distance policy.

        Args:
            cluster (ViolationCluster): The cluster that may need structural repairing

        Returns:
            bool: True if it fails grounding or distance policy, False otherwise
        """
        repair_reason = self.get_repair_classification(cluster)
        
        return repair_reason is not None
                    
                    