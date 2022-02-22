import OpenGL.GL as gl
import numpy as np

POINTS = 256
POSITIVE_BORDER = 1.0
NEGATIVE_BORDER = -1.0


skybox: dict = {
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: "./data/right.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: "./data/left.jpg",
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: "./data/top.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: "./data/bottom.jpg",
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: "./data/back.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: "./data/front.jpg"
}


def createGrid(countPoints):
    """
        Создание сетки - волновой поверхности.
    """

    vertices = np.empty((countPoints, countPoints, 3), dtype = np.float32)
    indices = list()

    for z, t in enumerate(np.linspace(NEGATIVE_BORDER, POSITIVE_BORDER, countPoints)):
        for x, s in enumerate(np.linspace(NEGATIVE_BORDER, POSITIVE_BORDER, countPoints)):
            vertices[x][z] = [s, 1, t]

            if x < countPoints - 1 and z < countPoints - 1:
                i = x + z * countPoints
                indices.append([i, i + 1, i + countPoints])
                indices.append([i + countPoints, i + 1, i + countPoints + 1])

    indices = np.array(indices, dtype = np.uint32)

    return vertices, indices
