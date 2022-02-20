import numpy as np


        # # cоздание объекта вершинного массива
        # VAO = gl.glGenVertexArrays(1)
        # gl.glBindVertexArray(VAO)

        # # копирование массива вершин в вершинный буфер
        # VBO = gl.glGenBuffers(1)
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
        # gl.glBufferData(gl.GL_ARRAY_BUFFER, self.model.vertices, gl.GL_STATIC_DRAW)

        # # копирование индексного массива в элементный буфер
        # EBO = gl.glGenBuffers(1)
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
        # gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.model.indices, gl.GL_STATIC_DRAW)

        # # установка указателей вершинных атрибутов
        # gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        # gl.glEnableVertexAttribArray(0)

        # # установка шейдеров
        # shaders = Shader("shader.vs", "shader.fs")
        # shaders.use()

        # # преобразование
        # shaders.setMat4("perspective", self.camera.getProjMatrix())
        # shaders.setMat4("view", self.camera.getVeiwMatrix())
        # shaders.setMat4("model", self.object.getModelMatrix())

        # # рисовка
        # gl.glBindVertexArray(VAO)
        # gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)
        # gl.glBindVertexArray(0)
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        
def create_grid(n_points: int):
    # gris_size = n_points x n_points
    vertices = np.empty((n_points, n_points, 3), dtype=np.float32)
    elements = list()
    for z, t in enumerate(np.linspace(-1.0, 1.0, n_points)):
        for x, s in enumerate(np.linspace(-1.0, 1.0, n_points)):
            print(z, t, x, s)
            vertices[x][z] = [s, 0, t]
            if x < n_points - 1 and z < n_points - 1:
                i = x + z * n_points
                print(i)
                elements.append([i, i + 1, i + n_points])
                elements.append([i + n_points, i + 1, i + n_points + 1])

    elements = np.array(elements, dtype=np.uint32)
    return vertices, elements


if __name__ == "__main__":
    for i in range (10):
        print(np.random.random(size=3))