from PyQt5 import QtGui, QtOpenGL
from PyQt5.QtGui import QMatrix4x4, QCursor, QColor
from PyQt5.QtCore import Qt, QPoint

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo

import glm
import glfw
import numpy as np

from shader import Shader

from PIL import Image

from object import Object
from camera import Camera
from model import Model

from texture import Texture

POINTS = 100

skybox: dict = {
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: "./cubemap/env/right.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: "./cubemap/env/left.jpg",
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: "./cubemap/env/top.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: "./cubemap/env/bottom.jpg",
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: "./cubemap/env/back.jpg",
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: "./cubemap/env/front.jpg"
}


class myGL(QtOpenGL.QGLWidget):
    def __init__(self, parent = None):
        print("CREATE")
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.randomDrop = False
        self.camMode = False
        self.setMouseTracking(self.camMode)
        self.cursor = QCursor()
        self.cursorShapes = [Qt.ArrowCursor, Qt.BlankCursor]

        self.color = (255, 255, 255, 1.0)
        self.angle = 0
        self.object = Object()
        self.camera = Camera()

        self.model = Model()
        self.model.load("./data/water_cube.obj")


    def initializeGL(self):
        print("INIT")
        self.qglClearColor(QtGui.QColor(50, 50, 50))
        gl.glEnable(gl.GL_DEPTH_TEST)


        self.prevTex = Texture(POINTS)
        self.currTex = Texture(POINTS)
        self.nextTex = Texture(POINTS)


    def resizeGL(self, width, height):
        print("RESIZE")
        gl.glViewport(0, 0, width, height)
        self.camera.changePerspective(ratio = width / height)
        self.camera.setPosition([-1.8, 4, 1.8])
        self.camera.rotateY(45)
        self.camera.rotateX(-50)


    def createGrid(self, countPoints):
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


    def paintWater(self):
        print("WATER: paint  --- start")

        # создаем сетку
        vertices, indices = self.createGrid(POINTS)

        # cоздание объекта вершинного массива
        VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(VAO)

        # копирование массива вершин в вершинный буфер
        VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_STATIC_DRAW)

        # копирование индексного массива в элементный буфер
        EBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)

        # установка указателей вершинных атрибутов
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
        gl.glEnableVertexAttribArray(0)

        print("WATER: update --- start")

        # bind FBO
        VArgs = gl.glGetIntegerv(gl.GL_VIEWPORT)

        self.nextTex.bindFBO()
        self.nextTex.setViewport()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # установка шейдеров
        shaders = Shader("update_water_shader.vs", "update_water_shader.fs")
        shaders.use()

        # uniform
        shaders.setInt("dropWater", self.randomDrop)

        shaders.set2f("center", *np.random.random(size=2))

        shaders.set1f("step", 1.0 / self.nextTex.size)

        self.prevTex.bind()
        shaders.setInt("prevTexture", self.prevTex.id)

        self.currTex.bind()
        shaders.setInt("currTexture", self.currTex.id)

        gl.glBindVertexArray(VAO)
        gl.glDrawElements(gl.GL_TRIANGLES, indices.size, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))
        gl.glBindVertexArray(0)
        
        
        self.prevTex.unbind()
        self.currTex.unbind()
        self.nextTex.unbindFBO()
        gl.glViewport(*VArgs)
        # Rotate
        self.prevTex, self.currTex, self.nextTex = self.currTex, self.nextTex, self.prevTex

        print("WATER: update --- end")


        print("WATER: draw   --- start")

        # установка шейдеров
        shaders = Shader("draw_water_shader.vs", "draw_water_shader.fs")
        shaders.use()

        # uniform
        # преобразование
        shaders.setMat4("perspective", self.camera.getProjMatrix())
        shaders.setMat4("view", self.camera.getVeiwMatrix())
        shaders.setMat4("model", self.object.getModelMatrix())

        TrInvModel = glm.mat3(glm.transpose(glm.inverse(self.object.getModelMatrix())))
        shaders.setMat3("TrInvModel", TrInvModel)
        shaders.set3f("cameraPos", self.camera.position.x, self.camera.position.y, self.camera.position.z)


        self.currTex.bind()
        shaders.setInt("heightMap", self.currTex.id)
        shaders.set1f("step", 1.0 / self.currTex.size)


        overlay = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, overlay)

        for mode, imgPath in skybox.items():
            img = Image.open(imgPath, mode='r').resize((512, 512))
            img_data = np.array(list(img.getdata()), np.uint8)
            gl.glTexImage2D(mode, 0, gl.GL_RGB8, img.width, img.height,
                         0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, overlay)

        gl.glBindVertexArray(VAO)
        gl.glDrawElements(gl.GL_TRIANGLES, indices.size, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))
        gl.glBindVertexArray(0)
    
        self.currTex.unbind()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        print("WATER: draw   --- end")  

        print("WATER: paint   --- end")


    def paintGL(self):
        print("CUBE: paint    --- start")

        # очищаем экран
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # cоздание объекта вершинного массива
        VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(VAO)

        # копирование массива вершин в вершинный буфер
        VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.model.vertices, gl.GL_STATIC_DRAW)

        # копирование индексного массива в элементный буфер
        EBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.model.indices, gl.GL_STATIC_DRAW)

        # установка указателей вершинных атрибутов
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        gl.glEnableVertexAttribArray(0)

        # установка шейдеров
        shaders = Shader("shader.vs", "shader.fs")
        shaders.use()

        # преобразование
        shaders.setMat4("perspective", self.camera.getProjMatrix())
        shaders.setMat4("view", self.camera.getVeiwMatrix())
        shaders.setMat4("model", self.object.getModelMatrix())

        # рисовка
        # gl.glBindVertexArray(VAO)
        # gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)
        # gl.glBindVertexArray(0)
        # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        print("CUBE: paint    --- end")

        self.paintWater()


    def translate(self, vec):
        self.camera.translate(*vec)


    def scale(self, coef):
        self.camera.zoom(coef)


    def rotate(self, vec):
        self.camera.rotateX(vec[0])
        self.camera.rotateY(vec[1])
        self.camera.rotateZ(vec[2])

    
    def mousePressEvent(self, event):
        selfPos = self.pos()
        self.lastPos = QPoint(selfPos.x() + self.width() // 2,
                              selfPos.y() + self.height() // 2
                       )
        self.cursor.setPos(self.lastPos)

        if event.button() == Qt.LeftButton:
            self.camMode = not self.camMode
            self.cursor.setShape(self.cursorShapes[self.camMode])
            self.setCursor(self.cursor)
            self.setMouseTracking(self.camMode)

        if self.camMode:
            print("on")
        else:
            print("off")


    def mouseMoveEvent(self, event):
        curPos = event.globalPos()

        if self.lastPos == curPos:
            return

        deltaX = curPos.x() - self.lastPos.x()
        deltaY = self.lastPos.y() - curPos.y()
        self.lastPos = curPos

        self.camera.rotation(deltaX, deltaY)


    def leaveEvent(self, event):
        if self.camMode:
            selfPos = self.pos()
            self.lastPos = QPoint(selfPos.x() + self.width() // 2,
                                  selfPos.y() + self.height() // 2
                           )
            self.cursor.setPos(self.lastPos)


    def wheelEvent(self, event):
        zoomCoef = event.pixelDelta().y() / 100
        self.camera.zoom(zoomCoef)


    def update(self, color, transVec):
        print("UPDATE")
        self.camera.continousTranslate(transVec)
        self.color = color
        self.updateGL()
