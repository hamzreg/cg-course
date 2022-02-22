import OpenGL.GL as gl
import glm
import math
import numpy as np

N_SECTOR = 25
N_STACK = 25
SPHERE_RADIUS = 0.3
TEX_PATH = "./data/sphereColor.jpg"
LIGHT_POSITION = glm.vec3(-3.0, 3.0, 3.0)
START_SPHERE_CENTER = glm.vec3(0, 0, 0)


def createSphere(nStack, nSector, radius):
    """
        Создание сферы.
    """

    vertices, textures, normals = list(), list(), list()
    
    sectorStep = 2.0 * math.pi / nSector
    stackStep = math.pi / nStack
        
    for i in range(nStack + 1):
        stackAngle = math.pi / 2.0 - i * stackStep
        xy = radius * math.cos(stackAngle)
        z = radius * math.sin(stackAngle)
        
        for j in range(nSector + 1):
            sectorAngle = j * sectorStep
            x = xy * math.cos(sectorAngle)
            y = xy * math.sin(sectorAngle)
            vertices.append([x, y, z])
            textures.append([j / nSector, i / nStack])
            normals.append([x / radius, y / radius, z / radius])

    vertices = np.array(vertices, dtype=np.float32).reshape((nStack + 1, nSector + 1, 3))
    textures = np.array(textures, dtype=np.float32).reshape((nStack + 1, nSector + 1, 2))
    normals = np.array(normals, dtype=np.float32).reshape((nStack + 1, nSector + 1, 3))

    return vertices, textures, normals


def sphereTriangulation(nStack, nSector):
    """
        Индексы для сферы.
    """

    indices = list()

    for i in range(nStack):
        k1 = i * (nSector + 1)
        k2 = k1 + nSector + 1

        for _ in range(nSector):
            if i != 0:
                indices.append([k1, k2, k1 + 1])
            if i != nStack - 1:
                indices.append([k1 + 1, k2, k2 + 1])
            k1 += 1
            k2 += 1

    return np.array(indices, dtype=np.uint32)
