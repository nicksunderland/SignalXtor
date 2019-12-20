from vispy import scene
from vispy.io import read_mesh
import numpy as np


class MeshWindow:

    def __init__(self):
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600))
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.TurntableCamera()
        self.view.camera.set_range((-20, 20), (-20, 20), (-20, 20))

    def update_plot(self):
        verts, faces, normals, nothin = read_mesh(
             "/Users/nicholassunderland/Desktop/SignalXtor/example_data/GAM003_LAGeom_trimmed.obj")
        v_colors = np.random.rand(verts.shape[0], 3)
        mesh = scene.visuals.Mesh(vertices=verts, vertex_colors=v_colors, shading='smooth', faces=faces)
        self.view.add(mesh)


