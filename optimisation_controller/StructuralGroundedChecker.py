from brick_placement import ConstructionGrid
from ViolationCluster import ViolationCluster

class StructuralGroundedChecker:
    
    CLASSIFICATION_DISCONNECTED = "DISCONNECTED"
    CLASSIFICATION_SINGLE_ANCHORED = "SINGLE_ANCHORED"
    CLASSIFICATION_MULTI_ANCHORED = "MULTI_ANCHORED"
    
    def __init__(self, construction_grid: ConstructionGrid) -> None:
        self.construction_grid = construction_grid
        
    def get_cluster_boundary_brick_ids(self, cluster: ViolationCluster) -> tuple[int, ...]:
        """ Returns brick ids on the boundary of clusters either above or below them

        Args:
            cluster (ViolationCluster): The core cluster that is being used to find neighbours

        Raises:
            ValueError: If a brick_id is invalid i.e. less than zero, or more than the amount of placed bricks

        Returns:
            tuple[int, ...]: A tuple of brick ids that are boundary to the cluster
        """
        cluster_brick_ids = set(cluster.get_violation_ids())
        
        boundary_brick_ids = set[int] = set()
        
        for cluster_brick_id in sorted(cluster_brick_ids):
            
            if (cluster_brick_id < 0 or cluster_brick_id >= len(self.construction_grid.placed_bricks)):
                raise ValueError("Brick id cannot possibly exist")
            else:
                
                cluster_brick = self.construction_grid.placed_bricks[cluster_brick_id]
                
                boundary_brick_ids.update(self.construction_grid.get_support_bricks(cluster_brick))
                boundary_brick_ids.update(self.construction_grid.get_bricks_above(cluster_brick))
                
        boundary_brick_ids.difference_update(cluster_brick_ids)
        return tuple(sorted(boundary_brick_ids))
        
    def get_grounded_boundary_brick_ids(self, cluster: ViolationCluster) -> tuple[int, ...]:
        """ Returns brick ids that are grounded using BFS that are neighbouring the violation cluster. Every brick returned is connected to the ground, excluding any bricks that require a cluster brick to be connected.

        Args:
            cluster (ViolationCluster): The violation cluster in the middle of the neighbours.

        Returns:
            tuple[int, ...]: Brick ids that are grounded regardless of cluster brick involvement.
        """
        cluster_brick_ids = cluster.get_violation_ids()
        
        boundary_brick_ids = set(self.get_cluster_boundary_brick_ids(cluster))
        
        grounded_brick_ids = set(self.construction_grid.get_grounded_brick_ids(excluded_brick_ids=cluster_brick_ids))
        
        grounded_brick_ids = boundary_brick_ids.intersection(grounded_brick_ids)
        
        return tuple(sorted(grounded_brick_ids))
    
    def get_grounded_regions(self, cluster: ViolationCluster) -> tuple[tuple[int, ...], ...]:
        """ Groups 

        Args:
            cluster (ViolationCluster): _description_

        Returns:
            tuple[tuple[int, ...], ...]: _description_
        """
        cluster_brick_ids = set(cluster.get_violation_ids())
        
        grounded_boundary_brick_ids = set(self.get_grounded_boundary_brick_ids(cluster))
        
        assigned_boundary_brick_ids: set[int] = set()
        
        grounded_regions: list[tuple[int, ...]] = []
        
        for boundary_brick_id in sorted(grounded_boundary_brick_ids):
            
            if boundary_brick_id not in assigned_boundary_brick_ids:
                
                connected_brick_ids = set(self.construction_grid.get_vertically_connected_brick_ids({boundary_brick_id}, cluster_brick_ids))
                
                region_boundary_brick_ids = connected_brick_ids.intersection(grounded_boundary_brick_ids)
                
                grounded_regions.append(tuple(sorted(region_boundary_brick_ids)))
                
                assigned_boundary_brick_ids.update(region_boundary_brick_ids)
                
        return tuple(grounded_regions)
    
    def classify_cluster_support(self, cluster: ViolationCluster) -> str:
        
        grounded_regions = self.get_grounded_regions(cluster)
        
        grounded_region_count = len(grounded_regions)
        
        if grounded_region_count == 0:
            return self.CLASSIFICATION_DISCONNECTED
        elif grounded_region_count == 1:
            return self.CLASSIFICATION_SINGLE_ANCHORED
        else:
            return self.CLASSIFICATION_MULTI_ANCHORED
        
    