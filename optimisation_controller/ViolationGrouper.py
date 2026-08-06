from optimisation_controller.StructuralViolation import StructuralViolation
from optimisation_controller.ViolationCluster import ViolationCluster

class ViolationGrouper:
    
    def __init__(self) -> None:
        print("Violation Grouper Created!")
        
    def are_violations_adjacent(self, violation1: StructuralViolation, violation2: StructuralViolation) -> bool:
        """Checks if two violations should be grouped together

        Args:
            violation1 (StructuralViolation): The first violation to check
            violation2 (StructuralViolation): The second violation to check

        Returns:
            bool: True if they should be groupd, False otherwise
        """
        for first_coordinate in violation1.footprint_coordinates:
            
            y_1, z_1, x_1 = first_coordinate
            
            for second_coordinate in violation2.footprint_coordinates:
                
                y_2, z_2, x_2 = second_coordinate
                
                layer_difference = abs(y_1 - y_2)
                
                z_diff = abs(z_1 - z_2)
                x_diff = abs(x_1 - x_2)
                
                horizontal_diff = z_diff + x_diff
                
                if layer_difference == 0 and horizontal_diff == 1:
                    return True
                elif layer_difference == 1 and horizontal_diff == 0:
                    return True
        
        return False
    
    def _get_group(self, start_index: int, ordered_violations: list[StructuralViolation], unvisited_indexes: set[int]) -> list[StructuralViolation]:
        """ Uses BFS to find every violation 

        Args:
            start_index (int): _description_
            ordered_violations (list[StructuralViolation]): _description_
            unvisited_indexes (set[int]): _description_

        Returns:
            list[StructuralViolation]: _description_
        """
        cluster: list[StructuralViolation] = []
        
        next_indices: list[int] = [start_index]
        
        unvisited_indexes.remove(start_index)
        
        while next_indices:
            current_index = next_indices.pop(0)
            
            current_violation = ordered_violations[current_index]
            
            cluster.append(current_violation)
            
            neighbouring_indices: list[int] = []
            
            for neighbour_index in sorted(unvisited_indexes):
                
                neighbour_violation = (ordered_violations[neighbour_index])
                
                if self.are_violations_adjacent(current_violation, neighbour_violation):
                    neighbouring_indices.append(neighbour_index)
                    
            for neighbouring_index in neighbouring_indices:
                unvisited_indexes.remove(neighbouring_index)
                
                next_indices.append(neighbouring_index)
        
        return cluster
    
    def group_violations(self, violations: list[StructuralViolation]) -> list[ViolationCluster]:
        """ Groups violations into 

        Args:
            violations (list[StructuralViolation]): _description_

        Returns:
            list[list[StructuralViolation]]: _description_
        """
        
        ordered_violations = sorted(violations, key=lambda violation: (violation.layer, violation.brick.z, violation.brick.x, violation.brick_id))
        
        unvisited_indices = set(range(len(ordered_violations)))
        
        clusters: list[ViolationCluster] = []
        
        while unvisited_indices:
            starting_index = min(unvisited_indices)
            
            clustered_violations = self._get_group(starting_index, ordered_violations, unvisited_indices)
            
            cluster = ViolationCluster(cluster_id=len(clusters), violations=clustered_violations)
            
            clusters.append(cluster)
            
        return clusters