import numpy as np
import open3d as o3d

from MeshVoxeliser import MeshVoxeliser
from MeshVoxeliser import create_path

# Add more method checking to this code

class OccupancyGrid:
    def __init__(self) -> None:
        self.occupancy_grid: np.ndarray | None = None
        #self.grid_offset: np.ndarray | None = None

    def create_occupancy_grid(self, voxel_grid: o3d.geometry.VoxelGrid) -> None:
        if voxel_grid is None:
            raise ValueError("Voxel grid is empty, please populate grid first.")
        
        voxels = voxel_grid.get_voxels()
        # Set voxel_grid as integers as partial voxel converage will equal full voxel coverage
        voxel_indices = np.array([voxel.grid_index for voxel in voxels], dtype=np.int32)

        # This whole secftion below is an attempt at local optimisation by removing array positions that can
        # never occur. In an instance such as [4,4,3] if these are the minimum indicies for each respective dimension
        # then by subtracting that minimum the same coordinates are represented and the sparsity is largely reduced.

        #minimum_indicies = np.min(voxel_indices, axis=0)
        #reduced_indices = voxel_indices - minimum_indicies
        #self.grid_offset = minimum_indicies

        # Array indicies start at 0 so we need to shift
        size_of_indices = voxel_indices.max(axis=0) + 1

        # We also want to shift the indicies so that the depth is the first dimension for understanability
        # This reverses it from [x,y,z] to [y,z,x] better to understand, the ground plane starts at y=0
        ordered_indices = size_of_indices[::-1]

        size_z = ordered_indices[0]
        size_y = ordered_indices[1]
        size_x = ordered_indices[2]

        shape = (size_y, size_z, size_x)
        self.occupancy_grid = np.zeros(shape, dtype=bool)

        x_indices = voxel_indices[:, 0]
        y_indices = voxel_indices[:, 1]
        z_indices = voxel_indices[:, 2]

        self.occupancy_grid[y_indices, z_indices, x_indices] = True

    def visualise_occupancy_grid(self) -> None:
        if self.occupancy_grid is None:
            raise ValueError("Occupancy grid is empty, please populate grid first.")

        print("Occupancy Grid Shape:", self.occupancy_grid.shape)
        print("Occupied Voxels: ", np.count_nonzero(self.occupancy_grid))
        print("Ground-Layer voxels: ", np.count_nonzero(self.occupancy_grid[0]))



model_path = create_path("bottle", 1, "shapenet")

mesh_voxeliser = MeshVoxeliser(
    model_path=model_path,
    resolution=16
)

voxel_grid = mesh_voxeliser.start()
print("Mesh extent [x, y, z]:", mesh_voxeliser.mesh.get_axis_aligned_bounding_box().get_extent())
occupancy_grid = OccupancyGrid()
occupancy_grid.create_occupancy_grid(voxel_grid)
occupancy_grid.visualise_occupancy_grid()