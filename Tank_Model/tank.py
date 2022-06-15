import math

G = 9.81


class Hole:
    def __init__(self, diameter):
        self.d: float = diameter


class Tank:
    def __init__(self, holes: list[Hole](), q: float, max_depth=1):
        self.holes: list[Hole]() = holes
        self.q: float = q

    def add_hole(self, hole: Hole):
        self.holes.append(hole)

    def rem_hole(self, i: int):
        self.holes.remove(i)

    def rem_hole_elem(self, hole: Hole):
        self.holes.remove(self.holes.__index__(hole))

    def check_holes(self):
        d = self.holes[0]
        return len([h for h in self.holes if h.d != d]) == 0

    def get_depth(self):
        if not self.check_holes():
            return -1
        d_holes = self.holes[0].d / 100
        n_holes = len(self.holes)

        return (1 / (2 * G)) * (((4 * self.q) / (n_holes * math.pi * (d_holes ** 2))) ** 2)


def create_holes(n: int, d: float):
    return [Hole(d) for i in range(n)]


if __name__ == '__main__':
    t = Tank(create_holes(25, 2), 0.06)
    print(t.get_depth())
