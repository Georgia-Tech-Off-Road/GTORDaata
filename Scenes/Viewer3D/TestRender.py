import sys

import numpy as np
from PyQt5.QtWidgets import QApplication
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem
from stl import mesh

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GLViewWidget()
    # https://ozeki.hu/attachments/116/Eiffel_tower_sample.STL
    stl_mesh = mesh.Mesh.from_file('topBoxV2.STL')

    points = stl_mesh.points.reshape(-1, 3)
    faces = np.arange(points.shape[0]).reshape(-1, 3)

    mesh_data = MeshData(vertexes=points, faces=faces)
    mesh = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
    view.addItem(mesh)

    view.show()
    app.exec()