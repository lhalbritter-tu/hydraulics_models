import math

G = 9.81
M_TO_PIXELS = 100


class Hole:
    def __init__(self, diameter):
        self.d: float = diameter


class Tank:
    def __init__(self, holes, q: float, max_depth=1, max_holes=50, width=200):
        self.holes = holes
        self.hole_callback = self.holes + create_holes(max_holes - len(self.holes), self.holes[0].d)
        self.q: float = q
        self.depth: float = max_depth
        self.width = width

    def add_hole(self, hole: Hole):
        self.holes.append(self.hole_callback[0])

    def pop_hole(self):
        self.holes.pop()

    def rem_hole(self, i: int):
        self.holes.remove(i)

    def rem_hole_elem(self, hole: Hole):
        self.holes.remove(self.holes.__index__(hole))

    def check_holes(self):
        d = self.holes[0].d
        ch = [h for h in self.holes if h.d != d]
        return len(ch) == 0

    def set_diameter(self, d):
        for hole in self.holes:
            hole.d = d

    def get_depth(self):
        if not self.check_holes():
            return -1
        d_holes = self.holes[0].d / 100
        n_holes = len(self.holes)

        return (1 / (2 * G)) * (((4 * self.q) / (n_holes * math.pi * (d_holes ** 2))) ** 2)

    def get_dimensions(self, x, y):
        return [x, y, self.width, self.depth * M_TO_PIXELS]

    def draw_holes(self, sx, x, y, ly):
        m = len(self.holes) // sx
        offs = self.width // m
        rects = []
        for i in range(0, m):
            rects.append([(offs + self.holes[i].d) * i + x, y, self.holes[i].d, ly])
        return rects

    def alt_draw_holes(self, x_off, x_0, y, ly):
        container = len(self.holes)
        fx = self.width / 2 + x_0
        rects = [[fx, y, self.holes[0].d, ly]]
        container -= 1

        for i in range(1, len(self.holes)):
            if container <= 0:
                return rects
            if (fx - x_off * i) < 0 or (fx + x_off * i) >= self.width + x_0:
                return rects
            rects.append([fx - x_off * i, y, self.holes[i].d, ly])
            container -= 1
            rects.append([fx + x_off * i, y, self.holes[i].d, ly])
            container -= 1
        return rects


def create_holes(n: int, d: float):
    return [Hole(d) for i in range(n)]


if __name__ == '__main__':
    t = Tank(create_holes(25, 2), 0.06)
    print(t.check_holes())
