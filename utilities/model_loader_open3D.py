from pathlib import Path
import open3d as o3d

MODEL_CLASS = "bathtub"
MODEL_NUMBER = "0001"

MODEL_PATH = Path("../model_data/model_net_10/" + MODEL_CLASS + "/train/" + MODEL_CLASS + "_" + MODEL_NUMBER + ".off")

mesh = o3d.io.read_triangle_mesh(str(MODEL_PATH))
mesh.compute_vertex_normals()

o3d.visualization.draw_geometries([mesh])
