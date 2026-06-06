from pathlib import Path
import open3d as o3d
import numpy as np

MODEL_CLASS = "chair"
MODEL_NUMBER = "0001"

MODEL_PATH = Path("../model_data/model_net_10/" + MODEL_CLASS + "/train/" + MODEL_CLASS + "_" + MODEL_NUMBER + ".off")

mesh = o3d.io.read_triangle_mesh(str(MODEL_PATH))
mesh.compute_vertex_normals()


# Resolution to voxel_size conversion
resolution = 16
bounding_box = mesh.get_axis_aligned_bounding_box()
largest_dimension = max(bounding_box.get_extent())

voxel_size = largest_dimension/resolution

voxel_grid = o3d.geometry.VoxelGrid.create_from_triangle_mesh(mesh, voxel_size=voxel_size)
# voxel size is an equation that can be converted to resolution if need be

# The voxel grid here should be used going ahead, because we don't care about lighting
# But for visualisation purposes

point_cloud = mesh.sample_points_uniformly(number_of_points=1000000)
point_cloud.paint_uniform_color([0.2, 1, 0.2])

visualised_voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=voxel_size)

o3d.visualization.draw_geometries([visualised_voxel_grid])