import OpenGL.GL as gl

import numpy as np

from shader import Shader

from object import Object
from camera import Camera
from model import Model
from texture import Texture

POINTS = 100



def createGrid(countPoints):
    vertices = np.empty((countPoints, countPoints, 3), dtype = np.float32)
    elements = list()

    for z, t in enumerate(np.linspace(-1.0, 1.0, countPoints)):
        for x, s in enumerate(np.linspace(-1.0, 1.0, countPoints)):
            vertices[x][z] = [s, 1, t]

            if x < countPoints - 1 and z < countPoints - 1:
                i = x + z * countPoints
                elements.append([i, i + 1, i + countPoints])
                elements.append([i + countPoints, i + 1, i + countPoints + 1])

    elements = np.array(elements, dtype = np.uint32)

    return vertices, elements


class Water(object):
    def __init__(self):
        print("Paint START : water")

        # self.camera = Camera()
        # self.object = Object()

        # создаем сетку
        self.vertices, self.indices = createGrid(POINTS)

        # cоздание объекта вершинного массива
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices, gl.GL_STATIC_DRAW)

        # копирование индексного массива в элементный буфер
        self.EBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices, gl.GL_STATIC_DRAW)

        # установка указателей вершинных атрибутов
        # gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
        # gl.glEnableVertexAttribArray(0)

        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)  # Unbind VBO
        # gl.glBindVertexArray(0)  # Unbind VAO

        # установка шейдеров
        shaders = Shader("water_shader.vs", "water_shader.fs")
        shaders.use()

        # # преобразование
        # shaders.setMat4("perspective", self.camera.getProjMatrix())
        # shaders.setMat4("view", self.camera.getVeiwMatrix())
        # shaders.setMat4("model", self.object.getModelMatrix())

    
    def draw(self):
        # рисовка
        gl.glBindVertexArray(self.VAO)
        gl.glDrawElements(gl.GL_TRIANGLES, self.indices.size, gl.GL_UNSIGNED_INT, None)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

        print("Paint END : water")