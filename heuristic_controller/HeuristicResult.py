from brick_placement import ConstructionGrid
from brick_placement import PlacementResult

class HeuristicResult:
    
    STATUS_MAXIMUM_ITERATIONS_HIT: str = "maxiumum iterations have been hit"
    
    def __init__(self, construction_grid: ConstructionGrid, placement_history: list[PlacementResult], final_status: str):
        self.construciton_grid = construction_grid
        self.result_grid = construction_grid.result_grid.copy()
        self.finished_grid = construction_grid.current_grid.copy()
        self.placed_bricks = construction_grid.placed_bricks
        self.placement_history = placement_history
        self.final_status = final_status