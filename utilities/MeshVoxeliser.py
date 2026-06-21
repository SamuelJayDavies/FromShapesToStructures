from pathlib import Path
import open3d as o3d
import numpy as np

from MeshValidator import MeshValidator

def create_path(model_class, model_number) -> Path:
    return Path("../model_data/model_net_10/" + model_class + "/" + model_class + "_" + str(model_number).zfill(4) + ".off")

class MeshVoxeliser:
    """ Class to voxelise the mesh and create a voxel grid.

    Args:
        model_path -- the path to the model.
        resolution -- the resolution of the voxel grid.

    Returns:
        None.
    """
    def __init__(
            self,
            model_path: Path,
            resolution: int = 16,
    ) -> None:
        
        self.model_path = Path(model_path)
        self.resolution = resolution

        self.mesh: o3d.geometry.TriangleMesh | None = None
        self.voxel_size: float | None = None
        self.voxel_grid: o3d.geometry.VoxelGrid | None = None

    def load_mesh(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        
        mesh = o3d.io.read_triangle_mesh(str(self.model_path))

        # Need to make sure the mesh has the valid properties
        validator = MeshValidator(mesh, resolution=self.resolution)
        if not validator.validate_baseline():
            print("\n This mesh is not watertight and hence its interior cannot be filled")
        
        mesh.compute_vertex_normals()
        self.mesh = mesh
    
    def calculate_voxel_size(self) -> float:
        
        bounding_box = self.mesh.get_axis_aligned_bounding_box()
        largest_dimension = max(bounding_box.get_extent())
        voxel_size = largest_dimension / self.resolution
        return voxel_size
    
    def create_voxel_grid(self) -> None:

        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_triangle_mesh(self.mesh, voxel_size=self.voxel_size)
    
    # Can come back and make the features 

    def visualise(self, number_of_points: int =100000, colour: tuple[float, float, float] = [0, 0, 0]) -> None:
        point_cloud = self.mesh.sample_points_uniformly(number_of_points=number_of_points)
        point_cloud.paint_uniform_color(colour)

        visualised_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=self.voxel_size)
        o3d.visualization.draw_geometries([visualised_voxel_grid])

    def start(self) -> o3d.geometry.VoxelGrid:
        
        self.load_mesh()
        self.voxel_size = self.calculate_voxel_size()
        self.create_voxel_grid()
        return self.voxel_grid

# voxel size is an equation that can be converted to resolution if need be

# The voxel grid here should be used going ahead, because we don't care about lighting
# But for visualisation purposes

model_path = create_path("chair", 1)

mesh_voxeliser = MeshVoxeliser(
    model_path=model_path,
    resolution=16
)

voxel_grid = mesh_voxeliser.start()
mesh_voxeliser.visualise()