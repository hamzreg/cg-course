from PyQt5 import QtGui, QtOpenGL
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QPoint

import OpenGL.GL as gl
import glm

import numpy as np
from random import uniform
from PIL import Image
from time import time

from shader import Shader
from object import Object
from camera import Camera
from texture import Texture

from water import *
from sphere import *
from constants import *


class myGL(QtOpenGL.QGLWidget):
    """
        Класс myGL для отрисовки.
    """

    def __init__(self, parent = None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        # эксперимент
        self.frames = 0
        self.timeStart = time()
        self.fps = 0

        self.camMode = False
        self.setMouseTracking(self.camMode)
        self.cursor = QCursor()
        self.cursorShapes = [Qt.ArrowCursor, Qt.BlankCursor]

        self.color = (255, 255, 255, 1.0)
        self.angle = 0
        self.object = Object()
        self.camera = Camera()

        # капли
        self.randomDrop = False

        # движение сферы
        self.load = False
        self.moveSphere = False
        self.nowCenter = glm.vec3(0, 0, 0)
        self.oldCenter = glm.vec3(0, 0, 0)
        self.sphereRadius = 0.02
        self.velocity = MIN_VELOCITY
        self.change = 0
        self.time = TIME / MS_IN_S
        self.route = POSITIVE


    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(50, 50, 50))
        gl.glEnable(gl.GL_DEPTH_TEST)

        # создание волновой поверхности
        self.createWater()

        # создание текстуры сферы
        self.sphereTexture = self.createTexture(TEX_PATH)


    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.camera.changePerspective(ratio = width / height)
        self.camera.setPosition([-1.8, 1, 1.8])
        self.camera.rotateY(45)
        self.camera.rotateX(-20)


    def paintGL(self):

        # очищаем экран
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if self.load:
            self.paintSphere()
        self.paintWater()


    def update(self, color, transVec):
        self.camera.continousTranslate(transVec)
        self.color = color
        self.updateGL()

        # эксперимент
        self.frames += 1
        timeEnd = time()

        if timeEnd - self.timeStart > 0:
            self.fps = self.frames // (timeEnd - self.timeStart)
            self.frames = 0
            self.timeStart = timeEnd

        print(POINTS, self.fps)


    def createWater(self):
        """
            Создание волновой
            поверхности.
        """

        # создание текстур
        self.prevTex = Texture(POINTS)
        self.currTex = Texture(POINTS)
        self.nextTex = Texture(POINTS)

        # создание сетки
        self.vertices, self.indices = createGrid(POINTS)

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
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, gl.GLvoidp(0))
        gl.glEnableVertexAttribArray(0)

        # наложение отражения облаков
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


    def paintWater(self):
        """
            Отрисовка волновой
            поверхности.
        """

        VArgs = gl.glGetIntegerv(gl.GL_VIEWPORT)

        self.nextTex.bindFBO()
        self.nextTex.setViewport()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # установка шейдеров
        shaders = Shader("updateWaterShader.vs", "updateWaterShader.fs")
        shaders.use()

        # uniform-переменные
        shaders.setInt("dropWater", self.randomDrop)
        shaders.setInt("moveSphere", self.moveSphere)
        shaders.set2f("center", *np.random.random(size=2))

        y1 = uniform(0, 0.2)
        y2 = uniform(0, 0.2)

        shaders.set1f("sphereRadius", self.sphereRadius)
        shaders.set3f("nowCenter", self.nowCenter.x, y1, self.nowCenter.z)
        shaders.set3f("oldCenter", self.oldCenter.x, y2, self.oldCenter.z)
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

        # обмен текстур
        self.prevTex, self.currTex, self.nextTex = self.currTex, self.nextTex, self.prevTex

        # установка шейдеров
        shaders = Shader("drawWaterShader.vs", "drawWaterShader.fs")
        shaders.use()

        # uniform-переменые
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


    def loadSphere(self):
        """
            Загрузка сферы.
        """

        vertices, textures, normals = createSphere(N_STACK, N_SECTOR, SPHERE_RADIUS)
        self.sphereVertices = np.dstack((vertices, textures, normals))
        self.sphereElements = sphereTriangulation(N_STACK, N_SECTOR)

        # cоздание объекта вершинного массива
        self.sphereVAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.sphereVAO)

        # копирование массива вершин в вершинный буфер
        self.sphereVBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sphereVBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.sizeof(self.sphereVertices),
                        self.sphereVertices.ravel(), gl.GL_STATIC_DRAW)

        # копирование индексного массива в элементный буфер
        self.sphereEBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.sphereEBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.sizeof(self.sphereElements),
                        self.sphereElements.ravel(), gl.GL_STATIC_DRAW)

        # установка указателей вершинных атрибутов
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(0))
        gl.glEnableVertexAttribArray(0)
        # установка указателей для текстур
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(12))
        gl.glEnableVertexAttribArray(1)
        # установка указателей для нормалей
        gl.glVertexAttribPointer(2, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, gl.GLvoidp(20))
        gl.glEnableVertexAttribArray(2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)


    def moveObject(self):
        """
            Движение сферы.
        """

        if self.moveSphere:
            if self.route == POSITIVE:
                sign = 1
            else:
                sign = -1
            
            self.change += sign * self.time * self.velocity

        if START_SPHERE_CENTER.x + self.change + self.sphereRadius >= POSITIVE_BORDER:
            self.route = NEGATIVE
        elif START_SPHERE_CENTER.x + self.change - self.sphereRadius <= NEGATIVE_BORDER:
            self.route = POSITIVE


    def paintSphere(self):
        """
            Отрисовка сферы.
        """

        shaders = Shader("sphereShader.vs", "sphereShader.fs")
        shaders.use()

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.sphereTexture)

        # uniform-переменные
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


        gl.glBindVertexArray(self.sphereVAO)
        gl.glDrawElements(gl.GL_TRIANGLES, self.sphereElements.size, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))
        gl.glBindVertexArray(0)

        self.moveObject()

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def createTexture(self, path):
        """
            Создание текстуры без FBO.
        """

        texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        tex = Image.open(path, mode='r')
        img_data = np.array(list(tex.getdata()), np.uint8)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB8, tex.width, tex.height, 0,
                        gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        return texture


    def sizeof(self, array):
        """
            Определение размера массива.
        """

        return array.size * array.itemsize


    def changeVelocity(self, value):
        """
            Изменение скорости
            движения сферы по
            значению слайдера.
        """

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
