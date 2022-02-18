import OpenGL.GL as gl
import numpy as np
import sys


def DEBUG():
    import inspect
    print(f"line {inspect.getframeinfo(inspect.stack()[1][0]).lineno:3}, error: {gl.glGetError()}")


class Texture:
    def __init__(self, size):
        self.size = size

        # создание текстуры
        self.id = gl.glGenTextures(1)
        DEBUG()
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        DEBUG()

        # режим наложения
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        DEBUG()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        DEBUG()

        # фильтрация
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        DEBUG()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        DEBUG()

        # создание графических данных
        data = np.zeros((self.size, self.size, 4), dtype=np.float32)
        DEBUG()
        # генерация текстуры
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F, self.size, self.size, 0,
                     gl.GL_RGBA, gl.GL_FLOAT, data)
        DEBUG()

        # # Кадровый буфер
        self.FBO = gl.glGenFramebuffers(1)  # Frame Buffer Objects
        DEBUG()
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
        DEBUG()

        # Прикрепление текстуры к буферу кадра
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                               gl.GL_TEXTURE_2D, self.id, 0)
        DEBUG()
        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        DEBUG()
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            DEBUG()
            print("Framebuffer is not complete!", file=sys.stderr)
            print(status)
            exit(-1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        DEBUG()

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

    # def __del__(self):
    #     if hasattr(self, 'EBO'):
    #         glDeleteBuffers(1, [self.EBO])
