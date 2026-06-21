from pathlib import Path
import open3d as o3d

def view_model(model_class, model_number) -> None:
    """ Method to visualise models in a dedicated window.
    
    Args
        model_class -- the class of the model (i.e. chair).
        model_number - the number of the model.

    Returns:
        None.
    """
    model_path = Path("../model_data/model_net_10/" + model_class.lower() + "/" + model_class.lower() + "_" + str(model_number).zfill(4) + ".off")
    mesh = o3d.io.read_triangle_mesh(str(model_path))
    mesh.compute_vertex_normals()

    o3d.visualization.draw_geometries([mesh])

view_model("bathtub", 1)
