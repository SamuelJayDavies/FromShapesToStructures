from brick.Brick_vocabulary import Brick_vocabulary
from brick.BrickType import BrickType
from optimisation_controller.StructuralViolation import StructuralViolation
from brick.Brick import Brick

from brick_placement.ConstructionGrid import ConstructionGrid

class ReplacementCandidateGenerator:
    
    def __init__(self, brick_vocabulary: Brick_vocabulary) -> None:
        
        if not isinstance(brick_vocabulary, Brick_vocabulary):
            raise TypeError("Brick vocab needs to be of type Brick_vocabulary")
        
        self.brick_vocabulary = brick_vocabulary
        
    def get_target_footprint_bounds(self, target_violation: StructuralViolation) -> tuple[int, int, int, int]:
        """ Returns the footprint of the violation brick 

        Args:
            target_violation (StructuralViolation): The target violation of the brick

        Returns:
            tuple[int, int, int, int]: 
        """
        footprint_coordinates = target_violation.footprint_coordinates
        
        if not footprint_coordinates:
            raise ValueError("Footprint is empty")
        
        y_coordinates = {coordinate[0] for coordinate in footprint_coordinates}
        
        if len(y_coordinates) != 1:
            raise ValueError("A brick cannot extend more than one y-layer")
        
        z_coordinates = [coordinate[1] for coordinate in footprint_coordinates]
        x_coordinates = [coordinate[2] for coordinate in footprint_coordinates]
        
        return (min(z_coordinates), max(z_coordinates), min(x_coordinates), max(x_coordinates))
    
    def get_candidate_brick_orientations(self, target_violation: StructuralViolation) -> list[tuple[BrickType, tuple[int, int]]]:
        """ Returns larger vocabulary bricks and orientations that can cover teh full target footprint

        Args:
            target_violation (StructuralViolation): The violation that is being covered

        Returns:
            list[tuple[BrickType, tuple[int, int]]]: A list of valid brick types and their orientation to cover the footprint of the target violation
        """
        min_z, max_z, min_x, max_x = self.get_target_footprint_bounds(target_violation)
        
        target_size_z = max_z - min_z + 1
        target_size_x = max_x - min_x + 1
        target_area = target_violation.total_footprint_coordinates_count
        
        candidate_orientations: list[tuple[BrickType, tuple[int, int]]] = []
        
        for brick_type in self.brick_vocabulary:
            
            seen_orientations: set[tuple[int, int]] = set()
            
            for orientation in brick_type.orientations():
                
                if orientation not in seen_orientations:
                    
                    seen_orientations.add(orientation)
                    
                    # Remember they are the other way round
                    candidate_size_z = orientation[1]
                    candidate_size_x = orientation[0]
                    
                    candidate_area = candidate_size_z * candidate_size_x
                    
                    if candidate_area > target_area and candidate_size_z >= target_size_z and candidate_size_x >= target_size_x:
                        
                        candidate_orientations.append((brick_type, orientation))
            
        candidate_orientations.sort(key=lambda candidate: (candidate[1][0] * candidate[1][1], candidate[1][0], candidate[1][1], candidate[0].name))
            
        return candidate_orientations
        
    def get_candidate_origins(self, target_violation: StructuralViolation, candidate_orientation: tuple[int, int]) -> list[tuple[int, int, int]]:
        """ Return every same-layer candidate origin where the candidate orientation can completely contain the target footprint

        Args:
            target_violation (StructuralViolation): The target violation 
            candidate_orientation (tuple[int, int]): the candidate origins being compared

        Returns:
            list[tuple[int, int, int]]: A list of y-z-x origins
        """
        min_z, max_z, min_x, max_x = self.get_target_footprint_bounds(target_violation)
        
        # And they are the other way round here, just remember i dont know why I did it like this
        candidate_size_z = candidate_orientation[1]
        candidate_size_x = candidate_orientation[0]
        
        target_size_z = max_z - min_z + 1
        target_size_x = max_x - min_x + 1
        
        if candidate_size_z < target_size_z or candidate_size_x < target_size_x:
            return []
        
        minimum_origins_z = max_z - candidate_size_z + 1
        maximum_origin_z = min_z
        
        minimum_origins_x = max_x - candidate_size_x + 1
        maximum_origin_x = min_x
        
        candidate_origins: list[tuple[int, int, int]] = []
        
        for origin_z in range(minimum_origins_z, maximum_origin_z + 1):
            
            for origin_x in range(minimum_origins_x, maximum_origin_x + 1):
                
                candidate_origins.append((target_violation.layer, origin_z, origin_x))
        
        return candidate_origins
    
    def create_replacement_candidate(self, brick_type: BrickType, candidate_orientation: tuple[int, int], candidate_origin: tuple[int, int, int]) -> Brick:
        """ Creates an unplaced brick that represents a possible candidate

        Args:
            brick_type (BrickType): The brick type of the proposed brick
            candidate_orietation (tuple[int, int]): The candidate orientation in (x, z) order
            candidate_origin (tuple[int, int, int]): The origin of the candidate

        Returns:
            Brick: An unplaced placement brick candidate
        """
        candidate_y, candidate_z, candidate_x = candidate_origin
        
        return Brick(brick_type, candidate_y, candidate_z, candidate_x, candidate_orientation)
    
    def generate_replacement_candidates(self, target_violation: StructuralViolation) -> list[Brick]:
        
        replacement_candidates: list[Brick] = []
        
        candidate_brick_orientations = self.get_candidate_brick_orientations(target_violation)
        
        for brick_type, candidate_orientation in candidate_brick_orientations:
            
            candidate_origins = self.get_candidate_origins(target_violation, candidate_orientation)
            
            for candidate_origin in candidate_origins:
                
                if any(coordinate < 0 for coordinate in candidate_origin):
                    continue
                
                candidate = self.create_replacement_candidate(brick_type, candidate_orientation, candidate_origin)
                
                replacement_candidates.append(candidate)
        
        return replacement_candidates
    
    def get_target_brick(self, construction_grid: ConstructionGrid, target_violation: StructuralViolation) -> Brick:
        
        target_brick_id = target_violation.brick_id
        
        if (target_brick_id < 0 or target_brick_id >= len(construction_grid.placed_bricks)):
            raise ValueError("Target violation has an non-existent brick Id")
        else:
            return construction_grid.placed_bricks[target_brick_id]
        
    def get_directly_adjacent_brick_ids(self, construction_grid: ConstructionGrid, target_violation: StructuralViolation) -> list[int]:
        
        target_brick = self.get_target_brick(construction_grid, target_violation)
        
        target_brick_id = target_violation.brick_id
        
        target_coordinates = construction_grid.get_brick_footprint_coordinates(target_brick)
        
        neighbour_shifts = ( (-1, 0), (1, 0), (0, -1), (0, 1))
        
        adjacent_brick_ids: set[int] = set()
        
        _, size_z, size_x = construction_grid.result_shape
        
        for y, z, x in target_coordinates:
            
            for z_shift, x_shift in neighbour_shifts:
                
                neighbour_z = z + z_shift
                neighbour_x = x + x_shift
                
                if not (0 <= neighbour_z < size_z and 0 <= neighbour_x < size_x):
                    continue
                
                neighbour_brick_id = int(construction_grid.current_grid[y, neighbour_z, neighbour_x])
                
                if (neighbour_brick_id != -1 and neighbour_brick_id != target_brick_id):
                    adjacent_brick_ids.add(neighbour_brick_id)
                    
        return sorted(adjacent_brick_ids)
    
    def get_combined_merge_footprint(self, construction_grid: ConstructionGrid, target_violation: StructuralViolation, neighbour_brick_id: int) -> set[tuple[int, int, int]]:
        
        target_brick = self.get_target_brick(construction_grid, target_violation)
        
        neighbour_brick = construction_grid.placed_bricks[neighbour_brick_id]
        
        if neighbour_brick.y != target_brick.y:
            raise ValueError("Merge neighbour must be on teh same y-layer")
        else:
            target_coordinates = set(construction_grid.get_brick_footprint_coordinates(target_brick))
            neighbour_coordinates = set(construction_grid.get_brick_footprint_coordinates(neighbour_brick))
            
            return target_coordinates | neighbour_coordinates
        
    def get_rectangular_merge_bounds(self, combined_coordinates: set[tuple[int, int, int]]) -> tuple[int, int, int, int, int] | None:
        
        if not combined_coordinates:
            return None
        else:
            y_coordinates = {coordinate[0] for coordinate in combined_coordinates}
            
            if len(y_coordinates) != 1:
                return None
            
            y = next(iter(y_coordinates))
            
            z_coordinates = [coordinate[1] for coordinate in combined_coordinates]
            x_coordinates = [coordinate[2] for coordinate in combined_coordinates]
            
            min_z = min(z_coordinates)
            max_z = max(z_coordinates)
            
            min_x = min(x_coordinates)
            max_x = max(x_coordinates)
            
            expected_coordinates: set[tuple[int, int, int]] = set()
            
            for z in range(min_z, max_z + 1):
                for x in range(min_x, max_x + 1):
                    expected_coordinates.add((y, z, x))
            
            if combined_coordinates != expected_coordinates:
                return None
            else:
                return (y, min_z, max_z, min_x, max_x)
            
    def get_merge_brick_options(self, combined_coordinates: set[tuple[int, int, int]]) -> list[tuple[BrickType, tuple[int, int], tuple[int, int, int]]]:
        
        merge_bounds = self.get_rectangular_merge_bounds(combined_coordinates)
        
        if merge_bounds is None:
            return []
        
        y, min_z, max_z, min_x, max_x = merge_bounds
        
        required_size_z = max_z - min_z + 1
        required_size_x = max_x - min_x + 1
        
        merge_origins = (y, min_z, min_x)
        
        merge_options: list[tuple[BrickType, tuple[int, int], tuple[int, int, int]]] = []
        
        for brick_type in self.brick_vocabulary:
            
            seen_orientations: set[tuple[int, int]] = set()
            
            for orientation in brick_type.orientations():
                
                if orientation not in seen_orientations:
                    seen_orientations.add(orientation)
                    
                    candidate_size_z = orientation[1]
                    candidate_size_x = orientation[0]
                    
                    if (candidate_size_z == required_size_z and candidate_size_x == required_size_x):
                        merge_options.append((brick_type, orientation, merge_origins))
        
        merge_options.sort(key=lambda option: (option[1][0] * option[1][1], option[1][0], option[1][1], option[0].name))
        
        return merge_options
    
    def generate_merge_candidates(self, construction_grid: ConstructionGrid, target_violation: StructuralViolation) -> list[tuple[Brick, int, int]]:
        
        merge_candidates: list[tuple[Brick, int, int]] = []
        
        target_brick_id = target_violation.brick_id
        
        adjacent_brick_ids = self.get_directly_adjacent_brick_ids(construction_grid, target_violation)
        
        for neighbour_brick_id in adjacent_brick_ids:
            
            combined_coordinates = self.get_combined_merge_footprint(construction_grid, target_violation, neighbour_brick_id) 
            
            merge_options = self.get_merge_brick_options(combined_coordinates)
            
            for brick_type, orientation, origin in merge_options:
                
                candidate = self.create_replacement_candidate(brick_type, orientation, origin)
                
                merge_candidates.append((candidate, target_brick_id, neighbour_brick_id))
                
        return merge_candidates
    
    