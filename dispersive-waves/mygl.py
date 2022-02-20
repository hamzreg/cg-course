from distutils.util import change_root
from turtle import position
from PyQt5 import QtGui, QtOpenGL
from PyQt5.QtGui import QMatrix4x4, QCursor, QColor
from PyQt5.QtCore import Qt, QPoint

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo

import glm
import glfw
import numpy as np
import math
from random import random, uniform

from shader import Shader

from PIL import Image

from object import Object
from camera import Camera
from model import Model

from texture import Texture

N_SECTOR = 25
N_STACK = 25

POINTS = 256

LIGHT_POSITION = glm.vec3(-3.0, 3.0, 3.0)

POSITIVE = True
NEGATIVE = False

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

        self.camMode = False
        self.setMouseTracking(self.camMode)
        self.cursor = QCursor()
        self.cursorShapes = [Qt.ArrowCursor, Qt.BlankCursor]

        self.color = (255, 255, 255, 1.0)
        self.angle = 0
        self.object = Object()
        self.camera = Camera()


        # self.model = Model()
        # self.model.load("./data/water_cube.obj")

        self.randomDrop = False
        self.moveSphere = False

        self.oldCenter = [0, 0, 0]
        self.center = [0, 0, 0]
        self.change = 0
        self.time = 0.005
        self.route = POSITIVE
        self.load = False


    def initializeGL(self):
        print("INIT")
        self.qglClearColor(QtGui.QColor(50, 50, 50))
        gl.glEnable(gl.GL_DEPTH_TEST)


        # WATER
        self.prevTex = Texture(POINTS)
        self.currTex = Texture(POINTS)
        self.nextTex = Texture(POINTS)

        # создаем сетку
        self.vertices, self.indices = self.createGrid(POINTS)
        print(self.vertices)

        # cоздание объекта вершинного массива
        self.waterVAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.waterVAO)

        # копирование массива вершин в вершинный буфер
        self.waterVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.waterVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices, gl.GL_STATIC_DRAW)

        # копирование индексного массива в элементный буфер
        self.waterEBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER,self.waterEBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices, gl.GL_STATIC_DRAW)

        # установка указателей вершинных атрибутов
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
        gl.glEnableVertexAttribArray(0)

        # для поверхности
        self.overlay = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.overlay)

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


        self.sphereTexture = self.create_texture()
        self.sphereCenter = glm.vec3(0, 0, 0)
        self.nowCenter = glm.vec3(0, 0, 0)
        self.oldCenter = glm.vec3(0, 0, 0)
        self.velocity = 0.5


    def resizeGL(self, width, height):
        print("RESIZE")
        gl.glViewport(0, 0, width, height)
        self.camera.changePerspective(ratio = width / height)
        self.camera.setPosition([-1.8, 1, 1.8])
        self.camera.rotateY(45)
        self.camera.rotateX(-20)


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
        shaders.setInt("moveSphere", self.moveSphere)
        
        shaders.set2f("center", *np.random.random(size=2))

        print(self.nowCenter, self.oldCenter)
        print(self.moveSphere)

        y1 = uniform(0, 0.2)
        y2 = uniform(0, 0.2)
        print(y1, y2)
        print(y1, y2)

        shaders.set3f("nowCenter", self.nowCenter.x, y1, self.nowCenter.z)
        shaders.set3f("oldCenter", self.oldCenter.x, y2, self.oldCenter.z)
        # shaders.set3f("nowCenter", abs(self.nowCenter.x), abs(self.nowCenter.y), abs(self.nowCenter.z))
        # shaders.set3f("oldCenter", abs(self.oldCenter.x), abs(self.oldCenter.y), abs(self.oldCenter.z))
        shaders.set1f("step", 1.0 / self.nextTex.size)
        
        self.prevTex.bind()
        shaders.setInt("prevTexture", self.prevTex.id)

        self.currTex.bind()
        shaders.setInt("currTexture", self.currTex.id)

        gl.glBindVertexArray(self.waterVAO)
        gl.glDrawElements(gl.GL_TRIANGLES, self.indices.size, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))
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

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.overlay)

        gl.glBindVertexArray(self.waterVAO)
        gl.glDrawElements(gl.GL_TRIANGLES, self.indices.size, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))
        gl.glBindVertexArray(0)
    
        self.currTex.unbind()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        print("WATER: draw   --- end")  

        print("WATER: paint   --- end")


    def loadSphere(self):
        # SPHERE
        vertices, textures, normals = self.create_sphere(N_STACK, N_SECTOR)
        self.sphereVertices = np.dstack((vertices, textures, normals))
        self.sphereElements = self.sphere_triangulation(N_STACK, N_SECTOR)

        # Vertex Array Objects (VAO)
        self.sphereVAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.sphereVAO)

        # Vertex Buffer Object (VBO)
        self.sphereVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sphereVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                     self.sizeof(self.sphereVertices),
                     self.sphereVertices.ravel(),
                     gl.GL_STATIC_DRAW)

        # Element Buffer Object (EBO)
        self.sphereEBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.sphereEBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                     self.sizeof(self.sphereElements),
                     self.sphereElements.ravel(),
                     gl.GL_STATIC_DRAW)

        #      'position' ----v
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(0))
        gl.glEnableVertexAttribArray(0)
        #       'texture' ----v
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(12))
        gl.glEnableVertexAttribArray(1)
        #        'normal' ----v
        gl.glVertexAttribPointer(2, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(20))
        gl.glEnableVertexAttribArray(2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)  # Unbind VBO
        gl.glBindVertexArray(0)  # Unbind VAO


    # latitude and longitude ~ sector and stacks
    def create_sphere(self,nStack: int,
                    nSector: int,
                    radius: float = 0.3) -> np.array:
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


    def sphere_triangulation(self,nStack: int,
                            nSector: int) -> np.array:
        """
        k1 <- k1+1
        |  / / ^
        v / /  |
        k2 -> k2+1
        """
        elements = list()
        for i in range(nStack):
            k1 = i * (nSector + 1)
            k2 = k1 + nSector + 1
            for j in range(nSector):
                if i != 0:
                    elements.append([k1, k2, k1 + 1])
                if i != nStack - 1:
                    elements.append([k1 + 1, k2, k2 + 1])
                k1 += 1
                k2 += 1

        return np.array(elements, dtype=np.uint32)


    def sizeof(self,x: np.array) -> int:
        return x.size * x.itemsize


    def create_texture(self):
        texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        tex = Image.open("./data/color.jpg", mode='r')
        img_data = np.array(list(tex.getdata()), np.uint8)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB8, tex.width, tex.height, 0,
                    gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        return texture


    def paintSphere(self):
        print("SPHERE: draw   --- start")

        shaders = Shader("sphere_shader.vs", "sphere_shader.fs")
        shaders.use()

        # Texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.sphereTexture)

        # Uniform
        self.oldCenter = self.nowCenter
        self.nowCenter.x = self.change
        self.nowCenter.z = self.change
        shaders.set1f("change", self.change)
        shaders.setMat4("perspective", self.camera.getProjMatrix())
        shaders.setMat4("view", self.camera.getVeiwMatrix())
        shaders.setMat4("model", self.object.getModelMatrix())
        TrInvModel = glm.mat3(glm.transpose(glm.inverse(self.object.getModelMatrix())))
        shaders.setMat3("TrInvModel", TrInvModel)
        shaders.set3f("lightPos", LIGHT_POSITION.x, LIGHT_POSITION.y, LIGHT_POSITION.z)


        # Draw
        gl.glBindVertexArray(self.sphereVAO)
        gl.glDrawElements(gl.GL_TRIANGLES, self.sphereElements.size, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)  # Unbind VAO
        
        if self.route == POSITIVE and self.moveSphere:
            self.change += self.time * self.velocity
        
        if self.route == NEGATIVE and self.moveSphere:
            self.change -= self.time * self.velocity

        if self.sphereCenter.x + self.change + 0.2 >= 1.0:
            self.route = NEGATIVE
        elif self.sphereCenter.x + self.change - 0.2 <= -1.0:
            self.route = POSITIVE

        # Unbind texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        print("SPHERE: draw   --- end")

    def paintGL(self):

        # очищаем экран
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if self.load:
            self.paintSphere()
        self.paintWater()


    def changeVelocity(self, value):
        self.velocity = value / 10

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
