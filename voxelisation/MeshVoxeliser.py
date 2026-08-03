from pathlib import Path
import open3d as o3d
import numpy as np

from .MeshValidator import MeshValidator

def create_path(model_class, model_number, model_dataset) -> Path:
    """
    Create the path to the model based on the model class, model number, and dataset.
    """
    if model_dataset == "model_net":
        return Path("model_data/model_net_10/" + model_class + "/" + model_class + "_" + str(model_number).zfill(4) + ".off")
    elif model_dataset == "shapenet":
        return Path("model_data/shape_net_core/" + model_class + "/" + str(model_number).zfill(4) + "/model_normalized.obj")
    else:
        raise ValueError(f"Invalid model dataset: {model_dataset}. Must be 'model_net' or 'shapenet'.")

# An important point for later on is that SHAPE_NET and MODEL_NET have different x, y, z axes. So going ahead
# only shape_net models will be compatible with the y-axis translation step

class MeshVoxeliser:
    """ Class to voxelise the mesh and create a voxel grid.

    Args:
        model_path: the path to the model.
        resolution: the resolution of the voxel grid.

    Depreciated:
        This class now no longer supports ModelNet models, as they have different x, y, z axes. Only ShapeNet models are supported.

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
        """
        Loades the mesh into the class and checks if it as all the required properties. If not, an error will be raised
        """
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
        """
        Calculate the voxel size based on the bounding box of the mesh and the resolution.
        """
        bounding_box = self.mesh.get_axis_aligned_bounding_box()
        largest_dimension = max(bounding_box.get_extent())
        voxel_size = largest_dimension / self.resolution
        return voxel_size

    # This is done before voxelisation as it is better to have the source mesh aligned rather than later voxel grid
    def ground_align_model(self) -> None:
        """
        Ground align the mesh by translating it along the y-axis so that the lowest point of the mesh is at y=0.
        """
        if self.mesh is None:
            raise ValueError("Mesh not loaded. Please load the mesh before ground aligning.")

        min_bound = self.mesh.get_min_bound()
        y_offset = -min_bound[1]
        self.mesh.translate((0, y_offset, 0))
    
    def create_voxel_grid(self) -> None:
        """
        Create a voxel grid from the loaded mesh.
        """
        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_triangle_mesh(self.mesh, voxel_size=self.voxel_size)
    
    # Can come back and make the features 

    def visualise(self, number_of_points: int =100000, colour: tuple[float, float, float] = [0.5, 0.5, 0.5]) -> None:
        """
        Visualise the voxel grid by sampling points from the mesh and creating a voxel grid from those points.
        """
        #point_cloud = self.mesh.sample_points_uniformly(number_of_points=number_of_points)
        #point_cloud.paint_uniform_color(colour)

        #visualised_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=self.voxel_size)
        o3d.visualization.draw_geometries([self.voxel_grid])

    def start(self) -> o3d.geometry.VoxelGrid:
        """
        Start the voxelisation process by loading the mesh, calculating the voxel size, and creating the voxel grid.
        """
        self.load_mesh()
        self.voxel_size = self.calculate_voxel_size()
        self.ground_align_model()
        self.create_voxel_grid()
        return self.voxel_grid

# voxel size is an equation that can be converted to resolution if need be

# The voxel grid here should be used going ahead, because we don't care about lighting
# But for visualisation purposes

#model_path = create_path("chair", 1, "model_net")

if __name__ == "__main__":
    model_path = create_path("chair", 1, "shapenet")

    mesh_voxeliser = MeshVoxeliser(
        model_path=model_path,
        resolution=16
    )

    voxel_grid = mesh_voxeliser.start()
    mesh_voxeliser.visualise()