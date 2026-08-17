import colorsys

import numpy as np
import open3d as o3d

class BrickConstructionVisualiser:
    
    EMPTY_VOXEL_VALUE: int = -1
    GOLDEN_RATIO_VALUE: float = 0.618033988749895
    
    PARTIALLY_SUPPORTED: str = "partially_supported"
    FLOATING: str = "floating"
    
    PARTIALLY_SUPPORTED_COLOUR: tuple[float, float, float] = (1.0, 0.8, 0.0)
    FLOATING_COLOUR: tuple[float, float, float] = (1.0, 0.0, 0.0)
    
    def __init__(self, finished_grid: np.ndarray, brick_statuses: dict[int, str] | None = None) -> None:
        
        if np.any(finished_grid < self.EMPTY_VOXEL_VALUE):
            raise ValueError("Finished grid cannot contain values below -1")
        
        self.finished_grid = finished_grid.copy()
        
        unique_bricks = np.unique(self.finished_grid)
        
        self.brick_ids = []
        
        for brick_id in unique_bricks:
            if brick_id != self.EMPTY_VOXEL_VALUE:
                self.brick_ids.append(brick_id)
                
        if brick_statuses is None:
            brick_statuses = {}
        
        valid_statuses = {self.PARTIALLY_SUPPORTED, self.FLOATING}
        
        for brick_id, status in brick_statuses.items():
            if brick_id not in self.brick_ids:
                raise ValueError("Brick Id not found in finished grid")
            
            if status not in valid_statuses:
                raise ValueError("Status is not partially supported or floating")
        
        self.brick_statuses = brick_statuses.copy()
        
    def _get_unqiue_brick_colour(self, brick_id: int) -> tuple[float, float, float]:
        
        # https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/ got the idea from this source
        hue = (brick_id * self.GOLDEN_RATIO_VALUE) % 1.0
        
        return colorsys.hsv_to_rgb(hue, 0.6, 0.9)
    
    def _get_brick_colour(self, brick_id: int) -> tuple[float, float, float]:
        brick_status = self.brick_statuses.get(brick_id)
        
        if brick_status == self.FLOATING:
            return self.FLOATING_COLOUR
        elif brick_status == self.PARTIALLY_SUPPORTED:
            return self.PARTIALLY_SUPPORTED_COLOUR
        else:
            return self._get_unqiue_brick_colour(brick_id)
    
    def _create_brick_mesh(self, brick_id: int) -> o3d.geometry.TriangleMesh:
        
        brick_coordinates = np.argwhere(self.finished_grid == brick_id)
        
        if brick_coordinates.size == 0:
            raise ValueError("This brick with the ID " + str(brick_id) + " does not exist in the finished grid")
        
        lowest_y, lowest_z, lowest_x = brick_coordinates.min(axis=0)
        
        highest_y, highest_z, highest_x = brick_coordinates.max(axis=0)
        
        # GET A SOURCE FOR HOW ALL THIS IS FOUND
        brick_width = highest_x - lowest_x + 1
        brick_height = highest_y - lowest_y + 1
        brick_depth = highest_z - lowest_z + 1
        
        brick_triangle_mesh = o3d.geometry.TriangleMesh.create_box(width=float(brick_width), height=float(brick_height), depth=float(brick_depth))
        
        brick_triangle_mesh.translate((float(lowest_x), float(lowest_y), float(lowest_z)))
        
        brick_triangle_mesh.paint_uniform_color(self._get_brick_colour(brick_id))
        
        brick_triangle_mesh.compute_vertex_normals()
        
        return brick_triangle_mesh
        
    def visualise_complete_model(self) -> None:
        
        if not self.brick_ids:
            raise ValueError("The finished grid does not contain any placed bricks WHAT!!")
        
        brick_meshes = [self._create_brick_mesh(brick_id) for brick_id in self.brick_ids]
        
        coordinate_frame_size = float(max(self.finished_grid.shape))
        
        coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=coordinate_frame_size * 0.20, origin=(0.0, 0.0, 0.0))
        
        o3d.visualization.draw_geometries(brick_meshes + [coordinate_frame], width=1280, height=720)