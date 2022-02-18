import numpy as np

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
    create_grid(6)