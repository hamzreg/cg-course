import OpenGL.GL as gl
import numpy as np
from PIL import Image
import sys

class Texture:
    """
        Класс для работы с текстурами
        и FBO.
    """

    def __init__(self, size):
        self.size = size

        # создание текстуры
        self.id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)

        # режим наложения
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        # фильтрация
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # создание графических данных
        data = np.zeros((self.size, self.size, 4), dtype=np.float32)
        # генерация текстуры
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F, self.size, self.size, 0,
                     gl.GL_RGBA, gl.GL_FLOAT, data)

        # Кадровый буфер
        self.FBO = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)

        # Прикрепление текстуры к буферу кадра
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                               gl.GL_TEXTURE_2D, self.id, 0)
        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)

        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer is not complete!", file=sys.stderr)
            exit(-1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)


    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.id)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)


    def unbind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.id)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def bindFBO(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                               gl.GL_TEXTURE_2D, self.id, 0)


    def unbindFBO(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)


    def setViewport(self):
        gl.glViewport(0, 0, self.size, self.size)
