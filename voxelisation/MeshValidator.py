import open3d
import numpy as np

class MeshValidator:
    """ Class to validate the mesh and its properties.
    
    Args:
        mesh -- the mesh to validate.
        resolution -- the resolution of the voxel grid.

    Returns:
        None.
    """
    def __init__(self, mesh: open3d.geometry.TriangleMesh, resolution: int = 16) -> None:
        self.mesh = mesh
        self.resolution = resolution

    def has_geometry(self) -> bool:
        """ 1. The mesh must contain geometry, containing vertices, triangles, and be non-empty.
        
        Args:
            mesh -- the mesh to check.
        
        Returns:
            True if the mesh has geometry, False otherwise.
        """
        return not self.mesh.is_empty() and self.mesh.has_triangles() and self.mesh.has_vertices()
    
    def has_finite_vertices(self) -> bool:
        """ 2. Every vertex coordinate must be a finite number (i.e. not NaN or infinite).
        
        Args:
            mesh -- the mesh to check.
            
        Returns:
            True if all vertex coordinates are finite, False otherwise.
        """
        return np.isfinite(np.asarray(self.mesh.vertices)).all()

    def has_valid_dimensions(self) -> bool:
        """ 3. The model must have valid width, height, and depth dimensions (non-zero and non-negative).
        
        Args:
            mesh -- the mesh to check.
        
        Returns:
            True if the model has valid dimensions, False otherwise.
        """
        bounding_box = self.mesh.get_axis_aligned_bounding_box()
        dimensions = bounding_box.get_extent()
        return np.all(dimensions > 0)
    
    def is_watertight(self) -> bool:
        """ 4. The mesh must be watertight, a completely closed surface separating the inside from the outside.

        Args:
            mesh -- the mesh to check.

        Returns:
            True if the mesh is watertight, False otherwise.
        
        """
        return self.mesh.is_watertight()

    def is_manifold(self) -> bool:
        """ 5. The mesh must be manifold, meaning that each edge is shared by exactly two triangles.

        Args:
            mesh -- the mesh to check.

        Returns:
            True if the mesh is manifold, False otherwise.
        """
        edge_manifold = self.mesh.is_edge_manifold(allow_boundary_edges=False)
        vertex_manifold = self.mesh.is_vertex_manifold()
        return edge_manifold and vertex_manifold

    def has_no_self_intersections(self) -> bool:
        """ 6. The mesh must not have self-intersections, meaning that no two triangles intersect each other.

        Args:
            mesh -- the mesh to check.
        
        Returns:
            True if the mesh has no self-intersections, False otherwise.
        """
        return not self.mesh.is_self_intersecting()

    def validate_baseline(self) -> bool:
        """ Method to validate the mesh against the baseline checks (1-3).
        
        Args:
            mesh -- the mesh to check.
        
        Returns:
            True if the mesh passes all baseline checks, False otherwise.
        """
        results = {
            "has_geometry": self.has_geometry(),
            "has_finite_vertices": self.has_finite_vertices(),
            "has_valid_dimensions": self.has_valid_dimensions(),
            "is_watertight": self.is_watertight(),
            "is_manifold": self.is_manifold(),
            "has_no_self_intersections": self.has_no_self_intersections()
        }

        print("------------------- Mesh Validation Results-------------------")
        for check, result in results.items():
            print(check + ": " + ("Passed" if result else "Failed"))
        
        print("------------------------")
        print("Overall Validation: " + ("Passed" if all(results.values()) else "Failed"))
        print("Baseline Validation: " + ("Passed" if all(results[check] for check in ["has_geometry", "has_finite_vertices", "has_valid_dimensions"]) else "Failed"))
        return all(results[check] for check in ["has_geometry", "has_finite_vertices", "has_valid_dimensions"])
        
    
    def validate_advanced(self) -> bool:
        """ Method to validate the mesh against the advanced checks (4-6).
        
        Args:
            mesh -- the mesh to check.
        
        Returns:
            True if the mesh passes all advanced checks, False otherwise.
        """
        results = {
            "has_geometry": self.has_geometry(),
            "has_finite_vertices": self.has_finite_vertices(),
            "has_valid_dimensions": self.has_valid_dimensions(),
            "is_watertight": self.is_watertight(),
            "is_manifold": self.is_manifold(),
            "has_no_self_intersections": self.has_no_self_intersections()
        }

        print("------------------- Mesh Validation Results-------------------")
        for check, result in results.items():
            print(check + ": " + ("Passed" if result else "Failed"))
        
        print("------------------------")
        print("Overall Validation: " + ("Passed" if all(results.values()) else "Failed"))
        print("Advanced Validation: " + ("Passed" if all(results[check] for check in ["is_watertight", "is_manifold", "has_no_self_intersections"]) else "Failed"))
        return all(results.values())