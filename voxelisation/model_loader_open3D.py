from pathlib import Path
import open3d as o3d

def view_model(model_class, model_number, model_dataset) -> None:
    """ Method to visualise models in a dedicated window.
    
    Args
        model_class -- the class of the model (i.e. chair).
        model_number - the number of the model.
        model_dataset - the dataset to which the model belongs.

    Returns:
        None.
    """
    if model_dataset == "model_net":
        model_path = Path("model_data/model_net_10/" + model_class.lower() + "/" + model_class.lower() + "_" + str(model_number).zfill(4) + ".off")
    elif model_dataset == "shapenet":
        model_path = Path("model_data/shape_net_core/" + model_class + "/" + str(model_number).zfill(4) + "/model_normalized.obj")
    else:
        raise ValueError(f"Invalid model dataset: {model_dataset}. Must be 'model_net' or 'shapenet'.")
    mesh = o3d.io.read_triangle_mesh(str(model_path))
    mesh.compute_vertex_normals()

    o3d.visualization.draw_geometries([mesh])

#view_model("bathtub", 1, "model_net")

if __name__ == "__name__":
    view_model("bottle", 1, "shapenet")
