import numpy as np


class Mesh():
    def __init__(self):
        self.vertices = np.empty(0)
        self.indices = np.empty(0)


class Cylinder(Mesh):
    def __init__(self, segments, height, radius):
        super().__init__()
        self.segments = segments
        self.height = height
        self.radius = radius
        self.generate()

    def generate(self):
        self.vertices = np.empty((self.segments * 4 + 2, 3), dtype=np.float64)
        #print(self.vertices)
        top_center = np.shape(self.vertices)[0] - 1
        bot_center = np.shape(self.vertices)[1] - 2
        self.vertices[top_center] = [0, self.height / 2, 0]
        self.vertices[bot_center] = [0, -self.height / 2, 0]

        step = 2 * np.pi / self.segments

        for i in range(0, self.segments):
            self.vertices[i] = [np.sin(step * i) * self.radius, -self.height / 2, np.cos(step * i) * self.radius]
        for i in range(0, self.segments):
            self.vertices[i + self.segments] = [np.sin(step * i) * self.radius, self.height / 2, np.cos(step * i) * self.radius]
        topCapBasePos = self.segments * 2
        botCapBasePos = self.segments * 3

        for i in range(self.segments):
            self.vertices[i + topCapBasePos] = [np.sin(step * i) * self.radius, self.height / 2, np.cos(step * i) * self.radius]
        for i in range(self.segments):
            self.vertices[i + botCapBasePos] = [np.sin(step * i) * self.radius, self.height / 2, np.cos(step * i) * self.radius]

        self.indices = np.empty((self.segments * 4, 3), dtype = np.int8)
        c = 0
        for i in range(self.segments):
            self.indices[c] = [i, (i + 1) % self.segments, i + self.segments]
            self.indices[c + 1] = [(i + 1) % self.segments, (i + 1) % self.segments + self.segments, i + self.segments]
            c += 2
        for i in range(self.segments):
            self.indices[c] = [bot_center, botCapBasePos + (i + 1) % self.segments, botCapBasePos + i]
            c += 1
        for i in range(self.segments):
            self.indices[c] = [top_center, topCapBasePos + i, topCapBasePos + (i + 1) % self.segments]
            c += 1

    def __repr__(self):
        return "Vertices: " + np.array2string(self.vertices) + "\nIndices: " + np.array2string(self.indices)