from OpenGL.GL import *
from shader import Shader
from PIL import Image
import numpy as np
import camera
import utils
import glm

skybox: dict = {
    GL_TEXTURE_CUBE_MAP_POSITIVE_X: "./cubemap/env/right.jpg",
    GL_TEXTURE_CUBE_MAP_NEGATIVE_X: "./cubemap/env/left.jpg",
    GL_TEXTURE_CUBE_MAP_POSITIVE_Y: "./cubemap/env/top.jpg",
    GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: "./cubemap/env/bottom.jpg",
    GL_TEXTURE_CUBE_MAP_POSITIVE_Z: "./cubemap/env/back.jpg",
    GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: "./cubemap/env/front.jpg"
}


def create_buffers():
    vertices = np.array([
        -1.0, +1.0, -1.0,
        -1.0, -1.0, -1.0,
        +1.0, -1.0, -1.0,
        +1.0, -1.0, -1.0,
        +1.0, +1.0, -1.0,
        -1.0, +1.0, -1.0,

        -1.0, -1.0, +1.0,
        -1.0, -1.0, -1.0,
        -1.0, +1.0, -1.0,
        -1.0, +1.0, -1.0,
        -1.0, +1.0, +1.0,
        -1.0, -1.0, +1.0,

        +1.0, -1.0, -1.0,
        +1.0, -1.0, +1.0,
        +1.0, +1.0, +1.0,
        +1.0, +1.0, +1.0,
        +1.0, +1.0, -1.0,
        +1.0, -1.0, -1.0,

        -1.0, -1.0, +1.0,
        -1.0, +1.0, +1.0,
        +1.0, +1.0, +1.0,
        +1.0, +1.0, +1.0,
        +1.0, -1.0, +1.0,
        -1.0, -1.0, +1.0,

        -1.0, +1.0, -1.0,
        +1.0, +1.0, -1.0,
        +1.0, +1.0, +1.0,
        +1.0, +1.0, +1.0,
        -1.0, +1.0, +1.0,
        -1.0, +1.0, -1.0,

        -1.0, -1.0, -1.0,
        -1.0, -1.0, +1.0,
        +1.0, -1.0, -1.0,
        +1.0, -1.0, -1.0,
        -1.0, -1.0, +1.0,
        +1.0, -1.0, +1.0
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER,
                 utils.sizeof(vertices),
                 vertices,
                 GL_STATIC_DRAW)

    #      'position' ----v
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, GLvoidp(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)  # Unbind VBO
    glBindVertexArray(0)  # Unbind VAO

    return VAO, VBO


class Cubemap:
    def __init__(self):
        self.shader = Shader(vertexShaderPath="./cubemap/vertex.glsl",
                             fragmentShaderPath="./cubemap/fragment.glsl",
                             shaderName="CubemapShader")

        self.VAO, self.VBO = create_buffers()

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)

        for mode, imgPath in skybox.items():
            img = Image.open(imgPath, mode='r').resize((512, 512))
            img_data = np.array(list(img.getdata()), np.uint8)
            glTexImage2D(mode, 0, GL_RGB8, img.width, img.height,
                         0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

        # Uniform location
        self.MVPLoc = self.shader.getUniformLocation("MVP")

    def draw(self):
        self.shader.use()
        # Options:
        # glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        # Uniform
        # Remove any translation component of the view matrix:
        view = glm.mat4(glm.mat3(camera.get_view_matrix()))
        mvp = camera.get_projection_matrix() * view  # no model
        glUniformMatrix4fv(self.MVPLoc, 1, GL_FALSE, glm.value_ptr(mvp))
        # Draw:
        glBindVertexArray(self.VAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glBindVertexArray(0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        glDepthFunc(GL_LESS)
        # glDepthMask(GL_TRUE)

    def __del__(self):
        if hasattr(self, 'VAO'):
            glDeleteVertexArrays(1, [self.VAO])
        if hasattr(self, 'VBO'):
            glDeleteBuffers(1, [self.VBO])
        if hasattr(self, 'shader'):
            del self.shader
