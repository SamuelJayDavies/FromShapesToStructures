import numpy as np
import open3d as o3d

from .MeshVoxeliser import MeshVoxeliser
from .MeshVoxeliser import create_path

# Add more method checking to this code

class ResultGrid:
    """ Class that creates a 3D numpy array from a voxel grid representing what the final model should look like 
    
    Args:
        None
    """
    def __init__(self) -> None:
        self.result_grid: np.ndarray | None = None
        self.grid_offset: np.ndarray | None = None
    
    def validate_result_grid(self) -> bool:
        """ Validates the result grid to ensure the model is grounded to the y-axis
        
        Returns: 
            Boolean that validates if the model is connected to the y-axis (via a supporting voxel on the bottom of the y-plane)
        """
        if self.result_grid is None:
            print("Result grid is empty, please populate grid first.")
            return False

        if self.result_grid.ndim != 3:
            print("Result grid is not 3D.")
            return False
        else:
            if not np.any(self.result_grid[0]):
                print("Result grid is not grounded.")
                return False
        
        return True

    def create_result_grid(self, voxel_grid: o3d.geometry.VoxelGrid) -> None:
        """ 
        Creates the result grid in numpy from the inputted voxel grid from the MeshVoxeliser class

        Args:
            voxel_grid: a voxelised 3D data structure that represents the object to be built (o3d.geometry.VoxelGrid)

        Returns:
            None
        """
        if voxel_grid is None:
            raise ValueError("Voxel grid is empty, please populate grid first.")
        
        # We want to get the collection of occupied Voxel objects with each of these being a grid_index
        voxels = voxel_grid.get_voxels()
        # Set voxel_grid as integers as partial voxel converage will equal full voxel coverage
        voxel_indices = np.array([voxel.grid_index for voxel in voxels], dtype=np.int32)

        # This whole secftion below is an attempt at local optimisation by removing array positions that can
        # never occur. In an instance such as [4,4,3] if these are the minimum indicies for each respective dimension
        # then by subtracting that minimum the same coordinates are represented and the sparsity is largely reduced.

        # Mention here that this was done to
        # - Reduce unncessary empty space, reduce array size, and to stop negative coordinate behaviour
        # But again include this as a later implementation, not as if you have done it now

        # If this wasn't normalised we are assuming every Open3D voxel index begins at zero, when it may not
        minimum_indicies = np.min(voxel_indices, axis=0)
        reduced_indices = voxel_indices - minimum_indicies
        self.grid_offset = minimum_indicies

        # Array indicies start at 0 so we need to shift
        size_of_indices = reduced_indices.max(axis=0) + 1

        # We also want to shift the indicies so that the depth is the first dimension for understanability
        # This reverses it from [x,y,z] to [y,z,x] better to understand, the ground plane starts at y=0
        ordered_indices = size_of_indices[::-1]

        size_z = ordered_indices[0]
        size_y = ordered_indices[1]
        size_x = ordered_indices[2]

        shape = (size_y, size_z, size_x)
        self.result_grid = np.zeros(shape, dtype=bool)

        x_indices = reduced_indices[:, 0]
        y_indices = reduced_indices[:, 1]
        z_indices = reduced_indices[:, 2]

        self.result_grid[y_indices, z_indices, x_indices] = True

        if self.validate_result_grid():
            print("------------------------ Result Grid Validation ------------------------")
            print("Result grid created successfully.")
        else:
            self.result_grid = None
            raise ValueError("Result grid validation failed after creation.")
        

    def visualise_result_grid(self) -> None:
        """ Visualises the numpy grid through outputting key characteristics of its dimensions and layers
        
        Returns:
            None
        """
        if self.result_grid is None:
            raise ValueError("Result grid is empty, please populate grid first.")

        print("Result Grid Shape:", self.result_grid.shape)
        print("Occupied Voxels: ", np.count_nonzero(self.result_grid))
        print("Ground-Layer voxels: ", np.count_nonzero(self.result_grid[0]))
        for layer in range(1, self.result_grid.shape[0]):
            print("Layer ", layer, " voxels: ", np.count_nonzero(self.result_grid[layer]))
                

if __name__ == "__main__":
    model_path = create_path("bottle", 1, "shapenet")

    mesh_voxeliser = MeshVoxeliser(
        model_path=model_path,
        resolution=16
    )

    voxel_grid = mesh_voxeliser.start()
    print("Mesh extent [x, y, z]:", mesh_voxeliser.mesh.get_axis_aligned_bounding_box().get_extent())
    result_grid = ResultGrid()
    result_grid.create_result_grid(voxel_grid)
    result_grid.visualise_result_grid()
    