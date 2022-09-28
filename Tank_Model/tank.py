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
    """
    Concrete Implementation of demo::Model for simulating a tank with holes
    """
    def lines(self):
        pass

    def calculate(self):
        """
        Returns the current water depth in the tank as string

        :return: the string representation of this model
        """
        return f'<h1>Water Depth &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp</h1> <br />' \
               f'Depth ${{h = \\frac{{1}}{{2g}} \cdot \left( \\frac{{4 \cdot Q_{{in}}}}{{n_{{holes}} \cdot \pi \cdot d^2_{{holes}}}} \\right)^2 [m] }}$ <br />' \
               f'Depth ${{ h = \\frac{{1}}{{2 \cdot 9.81}} \cdot \left( \\frac{{4 \cdot {self.q.real()}}}{{{self.nHoles.real()} \cdot \pi \cdot {self.dHoles.real()}^2}}\\right)^2[m] }}$ <br />' \
               f'Depth ${{h = {self.get_depth().rounded_latex(cut=3)}}}$'

    def update(self, args):
        """
        Starts adding or draining water, by starting the lerp_water() thread
        :param args: not used
        :return: None
        """
        if self.canvas is not None:
            t = threading.Thread(target=self.lerp_water, args=[0.01])  # self.canvas.on_client_ready(self.draw)
            t.start()

        # self.tank_pivot.scale = [1, self.depth.real(), 1]
        if self.threejs_scene is not None:
            self.draw_holes3D(self.threejs_scene)
        #self.water_pivot.scale = [1, self.get_depth().real(), 1]

        super().update(args)

    def set_threejs_scene(self, scene):
        self.threejs_scene = scene

    def __init__(self, holes, q: float, max_depth=1, max_holes=50, width=200, c=None, height=150):
        self.holes = holes
        self.hole_callback = self.holes + create_holes(max_holes - len(self.holes), self.holes[0].d)
        self.canvas = c
        self.q = FloatChangeable(q, _min=0.01, _max=1.0, desc="Discharge Q = ", unit="m³s⁻¹", step=0.01)
        self.depth = FloatChangeable(max_depth, _min=0.5, _max=5.0, desc="Tank depth = ", unit="m")
        #self.depth.observe(self.draw)
        self.nHoles = IntChangeable(len(holes), _min=5, _max=max_holes, desc="Nr of Holes: ")
        self.dHoles = FloatChangeable(holes[0].d * 10**(-2), unit="m", base=0, _min=0.005, _max=0.1, desc="Diameter d = ", step=0.001)

        self.plot_selection = ToggleGroup(["Discharge", "Number of Holes", "Diameter of Holes"], tooltips=["Shows the plot in dependence of Discharge Q",
                                                                                                            "Shows the plot in dependence of Number of Holes N",
                                                                                                            "Shows the plot in dependence of Diameter of Holes D"])
        self.plot_selection.observe(self.select_plot)
        self.nHoles.observe(self.update_plots)
        self.dHoles.observe(self.update_plots)
        self.q.observe(self.update_plots)

        self.params = [
            ChangeableContainer([self.q, self.depth]),
            ChangeableContainer([HorizontalSpace(50)]),
            ChangeableContainer([self.nHoles, self.dHoles]),
            ChangeableContainer([HorizontalSpace(50)]),
            ChangeableContainer([self.plot_selection]),
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
        self.water_pivot.scale = [1, min(1.05, self.get_depth().real()), 1]
        self.water_pivot.rotation = [pymath.pi, 0, 0, 'XYZ']

        self.current_water_depth = self.get_depth()

        self.hole_meshes = []

        self.plot = MultiPlot(width=5, height=5)
        self.q_vars = np.linspace(0, 1, 100)
        self.d_vars = np.linspace(0.5 * 10 ** (-2), 10 * 10 ** (-2), 100)
        self.n_vars = np.linspace(5, 50, 100)

        self.in_flow_plot = self.plot.add_ax(self.q_vars, (1 / (2 * G)) * ((4 * self.q_vars) / (self.nHoles.real() * pymath.pi * self.dHoles.real() ** 2)) ** 2,
                                            xlim=[0, 1], xlabel="Q [m^3s^(-1)]", ylabel="h [m]", title="Discharge Q")
        self.d_plot = self.plot.add_ax(self.d_vars, (1 / (2 * G)) * ((4 * self.q.real()) / (self.nHoles.real() * pymath.pi * self.d_vars ** 2)) ** 2, color='green',
                                       xlim=[0.5 * 10 ** (-2), 10 * 10 ** (-2)], xlabel="d [m]", ylabel="h [m]", title="Diameter d")
        self.n_plot = self.plot.add_ax(self.n_vars, (1 / (2 * G)) * ((4 * self.q.real()) / (self.n_vars * pymath.pi * self.dHoles.real() ** 2)) ** 2, color='orange',
                                       xlim=[5, 50], xlabel="n [#]", ylabel="h [m]", title="Number of Holes N")
        self.plot.set_visible(self.in_flow_plot)

        self.plot.grid(self.in_flow_plot)
        self.plot.grid(self.d_plot)
        self.plot.grid(self.n_plot)
        self.canvas.on_client_ready(self.do_draw)
        self.scale = self.canvas.width / self.canvas.height * 1.5

    def select_plot(self, args):
        if self.plot_selection.value == "Discharge":
            self.plot.set_visible(self.in_flow_plot)
        elif self.plot_selection.value == "Number of Holes":
            self.plot.set_visible(self.n_plot)
        elif self.plot_selection.value == "Diameter of Holes":
            self.plot.set_visible(self.d_plot)

    def update_plots(self, args):
        self.plot.set_data(self.in_flow_plot, self.q_vars, (1 / (2 * G)) * ((4 * self.q_vars) / (self.nHoles.real() * pymath.pi * self.dHoles.real() ** 2)) ** 2)
        self.plot.set_data(self.d_plot, self.d_vars, (1 / (2 * G)) * ((4 * self.q.real()) / (self.nHoles.real() * pymath.pi * self.d_vars ** 2)) ** 2)
        self.plot.set_data(self.n_plot, self.n_vars, (1 / (2 * G)) * ((4 * self.q.real()) / (self.n_vars * pymath.pi * self.dHoles.real() ** 2)) ** 2)
        self.plot.grid(self.in_flow_plot)
        self.plot.grid(self.d_plot)
        self.plot.grid(self.n_plot)
        self.plot.mark(self.d_plot, self.dHoles.real(), self.get_depth().real())
        self.plot.mark(self.n_plot, self.nHoles.real(), self.get_depth().real())
        self.plot.mark(self.in_flow_plot, self.q.real(), self.get_depth().real())

    def add_hole(self):
        """
        Adds a hole to the tank, increases number of holes in tank

        :return: None
        """
        self.holes.append(self.hole_callback[0])

    def pop_hole(self):
        """
        Pops the first Hole in the tank
        :return: None
        """
        self.holes.pop()

    def rem_hole(self, i: int):
        """
        Removes Hole at index i

        :param i: index
        :return: None
        """
        self.holes.remove(i)

    def rem_hole_elem(self, hole: Hole):
        """
        Removes a specific Hole from the tank
        :param hole: Hole Object to remove
        :return: None
        """
        self.holes.remove(self.holes.__index__(hole))

    def check_holes(self):
        """
        Checks if all the Holes are valid (= have equal diameter)
        :return: True, if diameter is equal for all holes, else False
        """
        d = self.holes[0].d
        ch = [h for h in self.holes if h.d != d]
        return len(ch) == 0

    def set_diameter(self, d):
        """
        Sets the diameter for all holes

        :param d: new diameter
        :return: None
        """
        for hole in self.holes:
            hole.d = d

    def get_depth(self):
        """
        Calculates current water depth and returns it

        :return: Variable Object with value=calculated water depth, unit='m'
        """
        if not self.check_holes():
            return -1
        d_holes = self.dHoles.real()
        n_holes = self.nHoles.real()

        return Variable((1 / (2 * G)) * (((4 * self.q.real()) / (n_holes * pymath.pi * (d_holes ** 2))) ** 2), unit="m")

    def get_dimensions(self, x, y):
        """
        Returns the dimensions of this tank for visualization with x-offset x and y-offset y

        :param x: the x-offset
        :param y: the y-offset
        :return: params for drawing a rect with x=x, y=y, width=self.width, height=self.height
        """
        return [x, y, self.width, self.height]

    def draw_holes(self, x_off, x_0, y, ly):
        """
        Returns a list of params for drawing holes in 2D, starting from the middle of the tank

        :param x_off: the distance between each hole
        :param x_0: the x-offset of the tank itself
        :param y: the y-position of the holes (bottom of tank)
        :param ly: the length of the holes in y-direction
        :return: list of params for hole rects
        """
        container = self.nHoles.real()
        fx = self.width / 2 + x_0
        rects = [[fx - self.dHoles.value * 100 / 2, y, self.dHoles.value * 100, ly]]
        container -= 1

        for i in range(1, len(self.holes)):
            if container - 2 < 0:
                return rects
            if (fx - x_off * i) < 0 or (fx + x_off * i) >= self.width + x_0:
                return rects
            rects.append([fx - x_off * i - self.dHoles.value * 100 / 2, y, self.dHoles.value * 100, ly])
            container -= 1
            rects.append([fx + x_off * i - self.dHoles.value * 100 / 2, y, self.dHoles.value * 100, ly])
            container -= 1
        return rects

    def do_draw(self):
        """
        Helper method to call the draw() method without arguments

        :return: None
        """
        self.draw(None)

    def draw(self, args):
        """
        Draws the 2D-Visualization of the tank

        :param args: catcher variable for ipywidgets observe method
        :return: None
        """
        self.canvas.clear()
        self.canvas.reset_transform()
        self.canvas.scale(self.scale, self.scale)
        self.canvas.fill_style = 'black'
        self.canvas.fill_rect(0, 0, 60, 20)
        rect = self.get_dimensions(50, 50)
        x_0 = rect[0]
        y_0 = rect[1]
        x_1 = x_0 + rect[2]
        y_1 = y_0 + rect[3]

        # self.canvas.height = y_1 + 50

        partial = self.get_depth().real() / self.depth.real()
        overflow = partial > 1
        if overflow:
            wy_0 = y_0 - 5
            self.canvas.stroke_style = 'red'
            self.canvas.stroke_text("OVERFLOW!", x_1 + 15, y_0 - 5)
            self.canvas.stroke_style = hexcode((20, 20, 20))
            self.canvas.font = '8px sans-serif'
            self.canvas.stroke_text("Equation invalidated", x_1 + 10, y_0 + 5)
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

        self.draw_stream(wy_0 - 10)
        self.canvas.fill_rect(x_0 + 1, wy_0, rect[2] - 1.5, y_1 - wy_0 - 1)

        if overflow:
            self.canvas.fill_rect(x_0 - 5, y_0 - 5, 5, y_1 - y_0 + 15)
            self.canvas.fill_rect(x_0, y_0 - 5, 5, 5)
            self.canvas.fill_rect(x_1, y_0 - 5, 5, y_1 - y_0 + 15)
            self.canvas.fill_rect(x_1 - 5, y_0 - 5, 5, 5)

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
        holes = self.draw_holes(15, x_0, y_1, 20)
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

        self.water_pivot.scale = [1, min(partial, 1.05), 1]
        # self.canvas.flush()

    def lerp_water(self, vstep):
        """
        Animates the 2D-Visualization by lerping the water depth from previous to current depth.
        Draws holes only when depth decreases, draws stream only when depth increases

        :param vstep: increase velocity of step variable for lerp method
        :return: None
        """
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
                overflow = partial > 1
                if overflow:
                    wy_0 = y_0 - 5
                    self.canvas.stroke_style = 'red'
                    self.canvas.stroke_text("OVERFLOW!", x_1 + 15, y_0 - 5)
                    self.canvas.stroke_style = hexcode((20, 20, 20))
                    self.canvas.font = '8px sans-serif'
                    self.canvas.stroke_text("Equation invalidated", x_1 + 10, y_0 + 5)
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
                #if self.current_water_depth > bf:
                self.draw_stream(wy_0 - 10)
                self.canvas.fill_rect(x_0 + 1, wy_0, rect[2] - 1.5, y_1 - wy_0 - 1)

                if overflow:
                    self.canvas.fill_rect(x_0 - 5, y_0 - 5, 5, y_1 - y_0 + 15)
                    self.canvas.fill_rect(x_0, y_0 - 5, 5, 5)
                    self.canvas.fill_rect(x_1, y_0 - 5, 5, y_1 - y_0 + 15)
                    self.canvas.fill_rect(x_1 - 5, y_0 - 5, 5, 5)

                self.global_alpha = 1

                line = [x_0 - 10, wy_0, x_0 - 10, y_1]
                self.canvas.stroke_line(*line)
                self.canvas.stroke_text("h", x_0 - 30, (wy_0 + y_1) // 2)

                #if self.current_water_depth < bf:
                holes = self.draw_holes(15, x_0, y_1, 20)
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

                self.water_pivot.scale = [1, min(partial, 1.05), 1]
                step += vstep
                self.canvas.sleep(20)
        self.draw(None)

    def lerp(self, v0, v1, t, unit=''):
        """
        Returns a linear interpolation between values v0 and v1 at t

        :param v0: start value
        :param v1: goal value
        :param t: step of the lerp
        :param unit: Unit of the Variable to return, default: ''
        :return: A variable of the lerped value
        """
        return Variable((1 - t) * v0.real() + t * v1.real(), unit=unit)

    def draw_stream(self, y):
        """
        Draws the water in-flow with y length

        :param y: length of the stream
        :return: None
        """
        self.canvas.fill_rect(60, 10, 5 + self.q.real() * 2, y)

    def draw_holes3D(self, scene):
        """
        Draws the Holes of the tank in 3D-Visualization

        :param scene: The 3D-Scene
        :return: None
        """
        for hole_mesh in self.hole_meshes:
            scene.remove(hole_mesh)
            hole_mesh.geometry.exec_three_obj_method("dispose")
        self.hole_meshes.clear()

        diameter = self.dHoles.real() / 5
        tw = self.width / 100
        ref_hole = CylinderBufferGeometry(diameter, diameter, 1, 8, 4)
        y = -1.5

        offset = 10 - self.dHoles.value * 100 / tw

        #print(offset, diameter, tw)

        hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'),
                    position=[0, y, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
        scene.add(hole)
        self.hole_meshes.append(hole)
        for i in range(1, self.nHoles.value // 8):
            if diameter * offset * i >= self.tank_rendering.position[0] + tw / 2 or diameter * offset * i >= self.tank_rendering.position[2] + self.tank_rendering.geometry.depth / 2:
                return
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * offset * i * (-1), y, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[0, y, diameter * offset * i * (-1)], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * offset * i * (1), y, 0], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[0, y, diameter * offset * i * (1)], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * offset * i, y, diameter * offset * i], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[-diameter * offset * i, y, diameter * offset * i], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[diameter * offset * i, y, -diameter * offset * i], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)
            hole = Mesh(ref_hole, material=MeshPhongMaterial(color='lightblue'), position=[-diameter * offset * i, y, -diameter * offset * i], rotation=[pymath.pi, 0, 0, 'XYZ'])
            scene.add(hole)
            self.hole_meshes.append(hole)


def create_holes(n: int, d: float):
    return [Hole(d) for i in range(n)]


if __name__ == '__main__':
    grid = Grid(16, 16, 2, 2)
    grid.place(0, 3, Variable(18, 0, 'cm'))
    grid.print2D()
