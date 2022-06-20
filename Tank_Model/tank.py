import math

G = 9.81
M_TO_PIXELS = 100


class Hole:
    def __init__(self, diameter):
        self.d: float = diameter


class Tank:
    def __init__(self, holes: list[Hole](), q: float, max_depth=1, max_holes=50):
        self.holes: list[Hole]() = holes
        self.hole_callback = self.holes + create_holes(max_holes - len(self.holes), self.holes[0].d)
        self.q: float = q
        self.depth: float = max_depth

    def add_hole(self, hole: Hole):
        self.holes.append(self.hole_callback[0])

    def pop_hole(self):
        self.holes.pop()

    def rem_hole(self, i: int):
        self.holes.remove(i)

    def rem_hole_elem(self, hole: Hole):
        self.holes.remove(self.holes.__index__(hole))

    def check_holes(self):
        d = self.holes[0]
        return len([h for h in self.holes if h.d != d]) == 0

    def set_diameter(self, d):
        for hole in self.holes:
            hole.d = d

    def get_depth(self):
        d_holes = self.holes[0].d / 100
        n_holes = len(self.holes)

        return (1 / (2 * G)) * (((4 * self.q) / (n_holes * math.pi * (d_holes ** 2))) ** 2)

    def get_dimensions(self, x, y):
        return [x, y, len(self.holes) * self.holes[0].d, self.depth * M_TO_PIXELS]


def create_holes(n: int, d: float):
    return [Hole(d) for i in range(n)]


if __name__ == '__main__':
    t = Tank(create_holes(25, 2), 0.06)
    print(t.get_depth())
