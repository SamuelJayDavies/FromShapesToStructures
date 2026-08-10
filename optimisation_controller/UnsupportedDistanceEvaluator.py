from optimisation_controller import StructuralGroundedChecker
from optimisation_controller import ViolationCluster
from brick_placement import ConstructionGrid

from collections import deque


class UnsupportedDistanceEvaluator:
    
    def __init__(self, construction_grid: ConstructionGrid, grounded_checker: StructuralGroundedChecker) -> None:
        self.construction_grid = construction_grid
        self.grounded_checker = grounded_checker
        
    def get_cluster_coordinates(self, cluster: ViolationCluster) -> tuple[tuple[int, int, int], ...]:
        """ Returns the footprint coordinates belonging to the weak cluster in y-z-x order

        Args:
            cluster (ViolationCluster): The cluster that provides the footprint coordinates

        Returns:
            tuple[tuple[int, int, int], ...]: Footprint coordinates in y, z x order
        """
        cluster_coordiantes: set[tuple[int, int, int]] = set()
        
        for violation in cluster.violations:
            cluster_coordiantes.update(violation.footprint_coordinates)
            
        return tuple(sorted(cluster_coordiantes))
    
    def get_unsupported_coordinates(self, cluster: ViolationCluster) -> tuple[tuple[int, int, int], ...]:
        unsupported_coordinates: set[tuple[int, int, int]] = set()
        
        for violation in cluster.violations:
            unsupported_coordinates.update(violation.unsupported_footprint_coordinates)
            
        return tuple(sorted(unsupported_coordinates))
    
    def get_grounded_regions(self, cluster: ViolationCluster) -> tuple[tuple[int, ...], ...]:
        regions = self.grounded_checker.get_grounded_regions(cluster)
        
        ordered_regions = [tuple(sorted(region)) for region in regions]
        
        return tuple(sorted(ordered_regions))
    
    # This method is for single anchored
    def get_grounded_contact_coordinates(self, cluster: ViolationCluster, grounded_region: tuple[int, ...]) -> tuple[tuple[int, int, int], ...]:
        """ Returns coordinates from a violation cluster that vertically contact any brick belonging to a grounded region. This can be above or below.

        Args:
            cluster (ViolationCluster): The violation cluster the coordinates are coming from
            grounded_region (tuple[int, ...]): The grounded region that bricks are being compared against

        Returns:
            tuple[tuple[int, int, int], ...]: A tuple of coordinates that are both part of the violation cluster and contact a grounded brick
        """
        grounded_brick_ids = set(grounded_region)
        
        cluster_coordinates = self.get_cluster_coordinates(cluster)
        
        contact_coordinates: set[tuple[int, int, int]] = set()
        
        y_size = self.construction_grid.current_grid.shape[0]
        
        for y, z, x in cluster_coordinates:
            
            if y > 0:
                below_brick_id = self.construction_grid.current_grid[y-1, z, x]
                
                if below_brick_id in grounded_brick_ids:
                    contact_coordinates.add((y, z, x))
            
            if y + 1 < y_size:
                above_brick_id = self.construction_grid.current_grid[y+1, z, x]
                if above_brick_id in grounded_brick_ids:
                    contact_coordinates.add((y, z, x))
                    
        return tuple(sorted(contact_coordinates))
    
    # This method is for multi-anchored
    def get_grounded_contact_regions(self, cluster: ViolationCluster) -> tuple[tuple[tuple[int, int, int], ...], ...]:
        """ Returns cluster contact coordinates from a violation cluster for multiple independantly grounded regions. For example, in a multi_anchored cluster, there will be more than one grounded region.

        Args:
            cluster (ViolationCluster): The violation cluster the coordinates are coming from

        Returns:
            tuple[tuple[tuple[int, int, int], ...], ...]: A tuple of tuples that contain coordinates for bricks that vertically contact a brick from a supported region, while separating each tuple by their different grounded regions.
        """
        grounded_regions = self.get_grounded_regions(cluster)
        
        contact_regions: list[tuple[tuple[int, int, int], ...]] = []
        
        for grounded_region in grounded_regions:
            contact_coordinates = self.get_grounded_contact_coordinates(cluster, grounded_region)
            
            contact_regions.append(contact_coordinates)
            
        return tuple(contact_regions)
    
    def get_cluster_neighbour_coordinates(self, coordinate: tuple[int, int, int], cluster_coordinates: set[tuple[int, int, int]]) -> tuple[tuple[int, int, int], ...]:
        """ Returns with 6-connectivity (up/down/left/right/forward/backward), coordinates that also belong to the violation cluster.

        Args:
            coordinate (tuple[int, int, int]): The coordinate that is started with
            cluster_coordinates (set[tuple[int, int, int]]): The cluster coordinates from a violation cluster

        Returns:
            tuple[tuple[int, int, int]]: Neighbour coordinates that also belong to a cluster
        """
        y, z, x = coordinate
        
        neighbour_candidates = (
            (y-1, z, x),
            (y+1, z, x),
            (y, z-1, x),
            (y, z+1, x),
            (y, z, x-1),
            (y, z, x+1)
        )
        
        # BFS can only travel through the violation cluster because we are finding how far the unsupported coordinates go away from a grounded structure
        return tuple(neighbour for neighbour in neighbour_candidates if neighbour in cluster_coordinates)
    
    def get_grounded_distance_map(self, cluster: ViolationCluster) -> dict[tuple[int, int, int], int]:
        """ Calcuates the shortest six-connected cluster distance from every reachable cluster coordinate to its nearest grounded contact coordinate

        Args:
            cluster (ViolationCluster): The violation cluster the BFS will have to traverse through

        Returns:
            dict[tuple[int, int, int], int]: A dictionary of the coordinate and its distance to the nearest grounded contact coordinate
        """
        cluster_coordinates = set(self.get_cluster_coordinates(cluster))
        
        grounded_contact_regions = self.get_grounded_contact_regions(cluster)
        
        grounded_contact_coordinates: set[tuple[int, int, int]] = set()
        
        for contact_region in grounded_contact_regions:
            grounded_contact_coordinates.update(contact_region)
        
        distance_by_coordinate: dict[tuple[int, int, int], int] = {}
        
        search_queue = deque()
        
        for contact_coordinate in grounded_contact_coordinates:
            if contact_coordinate in cluster_coordinates and contact_coordinate not in distance_by_coordinate:
                
                distance_by_coordinate[contact_coordinate] = 0
                search_queue.append(contact_coordinate)
                
        while search_queue:
            current_coordinate = search_queue.popleft()
            
            current_distance = distance_by_coordinate[current_coordinate]
            
            neighbour_coordinates = self.get_cluster_neighbour_coordinates(current_coordinate, cluster_coordinates)
            
            for neighbour_coordinate in neighbour_coordinates:
                if neighbour_coordinate not in distance_by_coordinate:
                    
                    distance_by_coordinate[neighbour_coordinate] = current_distance + 1
                    
                    search_queue.append(neighbour_coordinate)
        
        return dict(sorted(distance_by_coordinate.items()))
    
    def get_unsupported_distance_map(self, cluster: ViolationCluster) -> dict[tuple[int, int, int], int]:
        """ Returns the grounded-contact distance of every unsupported cordinate in the cluster. EVERY UNSUPPORTED COORDINATE

        Args:
            cluster (ViolationCluster): The violation cluster being used

        Returns:
            dict[tuple[int, int, int], int]: The distance from every point in the cluster, to the nearest grounded-contact point
        """
        unsupported_coordinates = self.get_unsupported_coordinates(cluster)
        
        grounded_distance_map = self.get_grounded_distance_map(cluster)
        
        if not grounded_distance_map:
            return {}
        else:
            unsupported_distance_map: dict[tuple[int, int, int], int] = {}
            
            for unsupported_coordinate in unsupported_coordinates:
                if unsupported_coordinate not in grounded_distance_map:
                    raise ValueError("Unsupported cluster coordinate cannot be reached from grounded contact coordinates")
                else:
                    unsupported_distance_map[unsupported_coordinate] = grounded_distance_map[unsupported_coordinate]
                    
            return dict(sorted(unsupported_distance_map.items()))
        
    def get_furthest_unsupported_coordinate(self, cluster: ViolationCluster) -> tuple[tuple[int, int, int], int] | None:
        """ Returns the furthest unsupported coordinate from a grounded structure to a unsupported coordinate

        Args:
            cluster (ViolationCluster): The cluster the unssupported coordinate is from

        Returns:
            tuple[tuple[int, int, int], int] | None: Returns a coordinate and its distance or none, if there is no unsupported coordinate
        """
        unsupported_distance_map = self.get_unsupported_distance_map(cluster)
        
        if not unsupported_distance_map:
            return None
        
        max_dist = max(unsupported_distance_map.values())
        
        furthest_coordinate = min(coordinate for coordinate, distance in unsupported_distance_map.items() if distance == max_dist)
        
        return furthest_coordinate, max_dist
    
    def get_unsupported_coordinate_count(self, cluster: ViolationCluster) -> int:
        """ Returns how many coordinates are unsupoorted in a cluster for later stability analysis

        Args:
            cluster (ViolationCluster): The cluster that is being counted

        Returns:
            int: How many coordinates are unsupported in the cluster
        """
        unsupported_coordinates = self.get_unsupported_coordinates(cluster)
        
        return len(unsupported_coordinates)
    
    def get_unsupported_horizontal_distance(self, cluster: ViolationCluster) -> tuple[int, int]:
        
        unsupported_coordinates = self.get_unsupported_coordinates(cluster)
        
        if not unsupported_coordinates:
            return (0, 0)
        else:
            z_coordinates = [coordinate[1] for coordinate in unsupported_coordinates]
            x_coordinates = [coordinate[2] for coordinate in unsupported_coordinates]
            
            z_dist = max(z_coordinates) - min(z_coordinates)
            x_dist = max(x_coordinates) - min(x_coordinates)
            
            return z_dist, x_dist
        
    def get_maximum_unsupported_horizontal_distance(self, cluster: ViolationCluster) -> int:
        
        z_dist, x_dist = self.get_unsupported_horizontal_distance(cluster)
        
        return max(z_dist, x_dist)
    
    def get_maximum_unsupported_distance(self, cluster: ViolationCluster) -> int | None:
        
        max_result = self.get_furthest_unsupported_coordinate(cluster)
        
        if max_result is None:
            return None
        else:
            _, max_dist = max_result
            
            return max_dist
        