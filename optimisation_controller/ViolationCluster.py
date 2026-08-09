from optimisation_controller.StructuralViolation import StructuralViolation

class ViolationCluster:
    
    def __init__(self, cluster_id: int, violations: list[StructuralViolation]) -> None:
        
        if len(violations) == 0:
            raise ValueError("Cannot have violation cluster with no violations")
        
        ordered_violations = sorted(violations, key=lambda violation: (violation.layer, violation.brick.z, violation.brick.x, violation.brick_id))
        
        violation_brick_ids = [violation.brick_id for violation in ordered_violations]
        
        if len(violation_brick_ids) != len(set(violation_brick_ids)):
            raise ValueError("Violations cannot appear more than once!")
        
        self.cluster_id = cluster_id
        self.violations = tuple(ordered_violations)
        self.violation_brick_ids = tuple(violation_brick_ids)
        self.violation_count = len(ordered_violations)
        
        self.footprint_coordinates = self._get_footprint_coordinates()
        
        self.y_bounds, self.z_bounds, self.x_bounds = self._calculate_cluster_bounds()
        
        self.total_support_deficit = sum(violation.support_diff for violation in self.violations)
        
        self.floating_violation_count = sum(1 for violation in self.violations if violation.actual_support_ratio == 0.0)
        
    def _get_footprint_coordinates(self) -> tuple[tuple[int, int, int]]:
        
        coordinates_set: set[tuple[int, int, int]] = set()
        
        for violation in self.violations:
            for coordinate in violation.footprint_coordinates:
                coordinates_set.add(coordinate)
                
                
        return tuple(sorted(coordinates_set, key=lambda coordinates: (coordinate[0], coordinate[1], coordinate[2])))
    
    def _calculate_cluster_bounds(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        
        if len(self.footprint_coordinates) == 0:
            raise ValueError("Cannot calcluate bounds on an empty cluster")
        
        y_coordinates = [coordinate[0] for coordinate in self.footprint_coordinates]
        z_coordinates = [coordinate[1] for coordinate in self.footprint_coordinates]
        x_coordinates = [coordinate[2] for coordinate in self.footprint_coordinates]
        
        y_bounds = min(y_coordinates)
        z_bounds = (min(z_coordinates), max(z_coordinates))
        x_bounds = (min(x_coordinates), max(x_coordinates))
        
        return (y_bounds, z_bounds, x_bounds)
    
    def get_violation_ids(self):
        return self.violation_brick_ids
    
    def __repr__(self) -> str:
        return "Violation Cluster (cluster_id + " + str(self.cluster_id) + ") violation brick ids " + str(self.violation_brick_ids) + " violation count " + str(self.violation_count) + " y_bounds " + str(self.y_bounds) + " z_bounds " + str(self.z_bounds) + " x_bounds " + str(self.x_bounds) + " total support deficit " + str(self.total_support_deficit) + " floating violation count" + str(self.floating_violation_count)
        