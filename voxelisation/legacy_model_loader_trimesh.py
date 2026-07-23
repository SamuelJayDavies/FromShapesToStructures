from pathlib import Path
import trimesh

MODEL_CLASS = "bathtub"
MODEL_NUMBER = "0001"

MODEL_PATH = Path("../model_data/model_net_10/" + MODEL_CLASS + "/train/" + MODEL_CLASS + "_" + MODEL_NUMBER + ".off")

mesh = trimesh.load(MODEL_PATH, force="mesh")

mesh.show()