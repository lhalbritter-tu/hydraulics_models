import math as pymath
import threading
import time

from ipycanvas import hold_canvas

from demo import *

G = 9.81
M_TO_PIXELS = 100


class Grid:
    def __init__(self, width, height, cell_width, cell_height):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.size = (width // cell_width, height // cell_height)
        self.grid = [[None] * (width // cell_width)] * (height // cell_height)

    def print2D(self):
        for line in self.grid:
            print('|', end=' ')
            for cell in line:
                print(cell, end=" | ")
            print()
            print('-' * self.size[0] * self.cell_width)

    def place(self, x, y, obj):
        if not self.inside(x, y):
            return False
        self.grid[x][y] = obj
        return True

    def inside(self, x, y):
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]


class Hole:
    def __init__(self, diameter):
        self.d: float = diameter


class Tank(Model):
    def lines(self):
        pass

    def calculate(self):
        return "Depth h = " + str(self.get_depth().rounded(cut=3))

    def update(self, args):
        if self.canvas is not None:
            t = threading.Thread(target=self.lerp_water, args=[0.01])  # self.canvas.on_client_ready(self.draw)
            t.start()

        self.tank_pivot.scale = [1, self.depth.real(), 1]
        #self.water_pivot.scale = [1, self.get_depth().real(), 1]


        super().update(args)

    def __init__(self, holes, q: float, max_depth=1, max_holes=50, width=200, c=None, height=150):
        self.holes = holes
        self.hole_callback = self.holes + create_holes(max_holes - len(self.holes), self.holes[0].d)
        self.canvas = c
        self.q = FloatChangeable(q, _min=0.01, _max=1.0, desc="Water flow Q = ", unit="m³s⁻¹", step=0.01)
        self.depth = FloatChangeable(max_depth, _min=0.5, _max=5.0, desc="Tank depth = ", unit="m")
        self.depth.observe(self.draw)
        self.nHoles = IntChangeable(len(holes), _min=5, _max=max_holes, desc="Nr of Holes: ")
        self.dHoles = FloatChangeable(holes[0].d, unit="cm", base=-2, _min=0.5, _max=10, desc="Diameter d = ")
        self.params = [
            ChangeableContainer([self.q, self.depth]),
            ChangeableContainer([self.nHoles, self.dHoles])
        ]
        self.width = width
        self.height = height

        self.tank_rendering = Mesh(
            BoxBufferGeometry(self.width / 100, 1, 1),
            MeshPhongMaterial(transparent=True, opacity=0.4, color='gray'),
            scale=[1, 1, 1],
            position=[0, -0.5, 0]
        )
        self.tank_pivot = Object3D()
        self.tank_pivot.add(self.tank_rendering)
        self.tank_pivot.scale = [1, self.depth.real(), 1]
        self.tank_pivot.position = [0, -1, 0]
        self.tank_pivot.rotation = [pymath.pi, 0, 0, 'XYZ']

        self.water_rendering = Mesh(
            BoxBufferGeometry(self.width / 100, 1, 1),
            MeshPhongMaterial(color='lightblue'),
            scale=[0.99, 1, 0.99],
            position=[0, -0.5, 0]
        )
        self.water_pivot = Object3D()
        self.water_pivot.add(self.water_rendering)
        self.water_pivot.position = [0, -1, 0]
        self.water_pivot.scale = [1, self.get_depth().real(), 1]
        self.water_pivot.rotation = [pymath.pi, 0, 0, 'XYZ']

        self.current_water_depth = self.get_depth()

        self.canvas.on_client_ready(self.do_draw)

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
        d_holes = self.dHoles.real()
        n_holes = self.nHoles.real()

        return Variable((1 / (2 * G)) * (((4 * self.q.real()) / (n_holes * pymath.pi * (d_holes ** 2))) ** 2), unit="m")

    def get_dimensions(self, x, y):
        return [x, y, self.width, self.height]

    def draw_holes(self, sx, x, y, ly):
        m = self.nHoles.real() // sx
        offs = self.width // m
        rects = []
        for i in range(0, m):
            rects.append([(offs + self.holes[i].d) * i + x, y, self.holes[i].d, ly])
        return rects

    def alt_draw_holes(self, x_off, x_0, y, ly):
        container = self.nHoles.real()
        fx = self.width / 2 + x_0
        rects = [[fx - self.dHoles.value / 2, y, self.dHoles.value, ly]]
        container -= 1

        for i in range(1, len(self.holes)):
            if container <= 0:
                return rects
            if (fx - x_off * i) < 0 or (fx + x_off * i) >= self.width + x_0:
                return rects
            rects.append([fx - x_off * i - self.dHoles.value / 2, y, self.dHoles.value, ly])
            container -= 1
            rects.append([fx + x_off * i - self.dHoles.value / 2, y, self.dHoles.value, ly])
            container -= 1
        return rects

    def draw_holes_3d(self):
        container = self.nHoles.real()

    def draw_hole_on_grid(self, grid, x, y, container):
        if container <= 0:
            return grid
        if not grid.place(x, y, self.holes[0]):
            return
        self.draw_hole_on_grid(grid, x + 1, y, container - 1)
        self.draw_hole_on_grid(grid, x - 1, y, container - 1)
        self.draw_hole_on_grid(grid, x, y + 1, container - 1)
        self.draw_hole_on_grid(grid, x, y - 1, container - 1)
        self.draw_hole_on_grid(grid, x + 1, y + 1, container - 1)
        self.draw_hole_on_grid(grid, x - 1, y + 1, container - 1)
        self.draw_hole_on_grid(grid, x + 1, y + 1, container - 1)
        self.draw_hole_on_grid(grid, x + 1, y - 1, container - 1)
        self.draw_hole_on_grid(grid, x - 1, y - 1, container - 1)

    def do_draw(self):
        self.draw(None)

    def draw(self, args):
        self.canvas.clear()
        self.canvas.fill_style = 'black'
        self.canvas.fill_rect(0, 0, 60, 20)
        rect = self.get_dimensions(50, 50)
        x_0 = rect[0]
        y_0 = rect[1]
        x_1 = x_0 + rect[2]
        y_1 = y_0 + rect[3]

        # self.canvas.height = y_1 + 50

        if self.get_depth().real() > self.depth.real():
            wy_0 = y_0 - 5
            self.canvas.stroke_style = 'red'
            self.canvas.stroke_text("OVERFLOW!", x_1 + 15, y_0 - 5)
            self.canvas.stroke_style = 'black'
        else:
            partial = self.get_depth().real() / self.depth.real()
            wy_0 = self.height * (1 - partial) + 50
        gradient = self.canvas.create_linear_gradient(
            x_0, wy_0, x_1, y_1,
            # List of color stops
            [
                (0, '#CAFAD4'),
                (1, '#90D3D6'),
            ],
        )
        self.canvas.fill_style = gradient
        self.canvas.global_alpha = 0.75
        self.canvas.fill_rect(x_0 + 1, wy_0, rect[2] - 1.5, y_1 - wy_0 - 1)

        """if 15 <= len(self.tank.holes) < 40:
            holes = self.tank.draw_holes(5, x_0, y_1, 20)
        elif len(self.tank.holes) >= 40:
            holes = self.tank.draw_holes(7, x_0, y_1, 20)
        elif len(self.tank.holes) < 15:
            holes = self.tank.draw_holes(1, x_0, y_1, 20)
        """
        self.canvas.global_alpha = 1

        line = [x_0 - 10, wy_0, x_0 - 10, y_1]
        self.canvas.stroke_line(*line)
        self.canvas.stroke_text("h", x_0 - 30, (wy_0 + y_1) // 2)

        #if self.current_water_depth.real() > 0.03:
        #    holes = self.alt_draw_holes(15, x_0, y_1, 20)
        #    for hole in holes:
        #        self.canvas.fill_rect(*hole)

        self.canvas.line_width = 3.0
        self.canvas.begin_path()
        self.canvas.move_to(x_0, y_0)
        self.canvas.line_to(x_0, y_1)
        self.canvas.line_to(x_1, y_1)
        self.canvas.line_to(x_1, y_0)
        self.canvas.stroke()
        self.canvas.line_width = 1.0
        # self.canvas.flush()

    def lerp_water(self, vstep):
        goal = self.get_depth()
        start_time = time.time()
        step = 0
        #print("Lerp Water, goal: " + str(goal) + ", cur: " + str(self.current_water_depth))
        with hold_canvas(self.canvas):
            while goal.real() - 0.001 > self.current_water_depth.real() or self.current_water_depth.real() > goal.real() + 0.001:
                ts = time.time()
                bf = self.current_water_depth
                self.current_water_depth = self.lerp(self.current_water_depth, goal, ts - start_time, 'm')

                #print("Lerp Water, goal: " + str(goal) + ", cur: " + str(self.current_water_depth))
                self.canvas.clear()
                self.canvas.fill_style = 'black'
                self.canvas.fill_rect(0, 0, 60, 20)
                rect = self.get_dimensions(50, 50)
                x_0 = rect[0]
                y_0 = rect[1]
                x_1 = x_0 + rect[2]
                y_1 = y_0 + rect[3]
                partial = self.current_water_depth.real() / self.depth.real()
                if partial > 1:
                    wy_0 = y_0 - 5
                    self.canvas.stroke_style = 'red'
                    self.canvas.stroke_text("OVERFLOW!", x_1 + 15, y_0 - 5)
                    self.canvas.stroke_style = 'black'
                else:
                    wy_0 = self.height * (1 - partial) + 50
                gradient = self.canvas.create_linear_gradient(
                    x_0, wy_0, x_1, y_1,
                    # List of color stops
                    [
                        (0, '#CAFAD4'),
                        (1, '#90D3D6'),
                    ],
                )
                self.canvas.fill_style = gradient
                self.canvas.global_alpha = 0.75
                if self.current_water_depth > bf:
                    self.draw_stream(wy_0)
                self.canvas.fill_rect(x_0 + 1, wy_0, rect[2] - 1.5, y_1 - wy_0 - 1)

                self.global_alpha = 1

                line = [x_0 - 10, wy_0, x_0 - 10, y_1]
                self.canvas.stroke_line(*line)
                self.canvas.stroke_text("h", x_0 - 30, (wy_0 + y_1) // 2)

                if self.current_water_depth < bf:
                    holes = self.alt_draw_holes(15, x_0, y_1, 20)
                    for hole in holes:
                        self.canvas.fill_rect(*hole)

                self.canvas.line_width = 3.0
                self.canvas.begin_path()
                self.canvas.move_to(x_0, y_0)
                self.canvas.line_to(x_0, y_1)
                self.canvas.line_to(x_1, y_1)
                self.canvas.line_to(x_1, y_0)
                self.canvas.stroke()
                self.canvas.line_width = 1.0

                self.water_pivot.scale = [1, self.current_water_depth.real(), 1]
                step += vstep
                self.canvas.sleep(20)
        self.draw(None)

    def lerp(self, v0, v1, t, unit=''):
        return Variable((1 - t) * v0.real() + t * v1.real(), unit=unit)

    def draw_stream(self, y):
        self.canvas.fill_rect(60, 10, 5, y)
        pass

    def draw_holes3D(self, scene):
        diameter = self.dHoles.real()
        ref_hole = CylinderBufferGeometry(diameter, diameter, 3, 8, 4)
        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'),
                    position=[0, -2.5, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)
        for i in range(1, self.nHoles.value // 4):
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * 4 * i * (-1), -2.5, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[0, -2.5, diameter * 4 * i * (-1)], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * 4 * i * (1), -2.5, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[0, -2.5, diameter * 4 * i * (1)], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)

        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'),
                    position=[diameter * self.nHoles.value * (-1), -2.5, diameter * self.nHoles.value * -1], rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)
        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'),
                    position=[diameter * self.nHoles.value, -2.5, diameter * self.nHoles.value * (-1)], rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)
        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * self.nHoles.value * (1), -2.5, diameter * self.nHoles.value],
                    rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)
        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * self.nHoles.value * (-1), -2.5, diameter * self.nHoles.value * (1)],
                    rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)

        # holes = InstancedBufferGeometry(attributes=hole.attributes, instanceCount=self.nHoles.real())
        # return Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[0, -2.5, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])


def create_holes(n: int, d: float):
    return [Hole(d) for i in range(n)]


if __name__ == '__main__':
    grid = Grid(16, 16, 2, 2)
    grid.place(0, 3, Variable(18, 0, 'cm'))
    grid.print2D()
