import numpy as np
import glm

class Model(object):
    """
        Класс модели.
    """

    def __init__(self):
        pass
        # self.vertices = vertices
        # self.indices = indices


    def load(self, path):
        vrtcs = []
        indcs = []

        f = open(path)

        for line in f:
            values = line.split()

            if values[0] == "v":
                vertex = []

                vertex.append(float(values[1]))
                vertex.append(float(values[2]))
                vertex.append(float(values[3]))

                vrtcs.append(vertex)
            
            if values[0] == "f":

                facet = values[1].split("/")
                indcs.append(int(facet[0]))

                facet = values[2].split("/")
                indcs.append(int(facet[0]))

                facet = values[3].split("/")
                indcs.append(int(facet[0]))

        f.close()

        print(vrtcs)
        print(indcs)

        self.vertices = np.array(vrtcs, dtype = 'float32')
        self.indices = np.array(indcs, dtype='int32')
