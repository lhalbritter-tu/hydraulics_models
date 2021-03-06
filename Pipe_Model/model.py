from abc import ABC
import abc
import math as pymath
from demo import *


class IntersectionForm(ABC):
    """
    Interface for Pipe Intersection Types. Defines the height of the Form
    """

    def __init__(self, y, type):
        self.y = y
        self.type = type

    @abc.abstractmethod
    def area(self):
        """
        Calculates the area of this specific Form
        :return: the correct area
        """
        pass

    @abc.abstractmethod
    def draw(self, dw=0):
        """
        Returns a QtGraphicsItem, using the form's attributes as values

        :param dw: specifies the margin to the left side of the canvas
        :return: Specific QtGraphicsItem implementation corresponding to the type of this form
        """
        pass

    @abc.abstractmethod
    def display(self, dw=0):
        """
        Returns a tuple of correctly sorted attributes of this form, for jupyter notebook usage

        :param dw: specifies the margin to the left side of the canvas
        :return: tuple of attributes
        """
        pass


class Circle(IntersectionForm):
    """
    Concrete Implementation of IntersectionForm, representing a circular form. Additional
    attribute d is for the diameter of the circle.
    """

    def __init__(self, d, y):
        super().__init__(y, "Circle")
        self.d = d
        self.r = self.rx = self.ry = self.d * 100 / 2

    def area(self):
        return (pymath.pi * self.d ** 2) / 4

    def __str__(self):
        return "D: " + str(self.d)

    def draw(self, dw=0):
        self.x = dw
        self.r = self.rx = self.ry = self.d * 100 / 2
        pass

    def display(self, dw=0):
        self.x = dw
        self.r = self.rx = self.ry = self.d * 10 / 2
        return self.x, self.y, self.r


class Rect(IntersectionForm):
    """
    Concrete Implementation of IntersectionForm, representing a rectangular Form. Additional attributes
    w for width and h for height of the rectangle.
    """

    def __init__(self, w, h, y):
        super().__init__(y, "Rectangle")
        self.w = w
        self.h = h

    def area(self):
        return self.h * self.w

    def __str__(self):
        return "W: " + str(self.w) + "\tH: " + str(self.h)

    def draw(self, dw=0):
        self.x = dw

    def display(self, dw=0):
        self.x = dw
        self.rx = self.w * 20 / 2
        self.ry = self.h * 20 / 2
        return self.x, self.y, self.rx, self.ry


class SimplePipe(Model):
    """
    Concrete implementation of Model, which represents a simple pipe with two circular endings.
    """

    def update(self, args):
        if self.callback is None:
            return -1
        if self.callback.params is None:
            return -2
        if len(self.callback.params) < 3:
            return -3
        self.d1, self.d2, self.u1 = self.callback.params
        super().update(args)

    def __init__(self, d1, d2, u1):
        self.d1 = d1
        self.d2 = d2
        self.u1 = u1

    def q1(self):
        """
        Calculates the pressure of the water flowing in the pipe
        Invariance: Must be equal to self.q2()
        :return: the calculated pressure
        """
        return (pymath.pi * self.d1 ** 2) / 4 * self.u1

    def q2(self):
        """
        Calculates the pressure of the water flowing out of the pipe.
        Invariance: Must be equal to self.q1()
        :return: the calculated pressure
        """
        return (pymath.pi * self.d2 ** 2) / 4 * self.u2()

    def u2(self):
        """
        Calculates the velocity of the water after flowing through the pipe
        :return: the velocity of the water at the second end
        """
        return (self.d1 ** 2) / (self.d2 ** 2) * self.u1

    def calculate(self):
        return "D1: " + str(self.d1) + "<br />D2: " + str(self.d2) + "<br />U1: " + str(self.u1) + "<br /><br />Q1 = " + \
               str(self.q1()) + "<br />Q2 = " + str(self.q2()) + "<br />U2 = " + str(self.u2())
        # return f'D1: {self.d1:.3f}<br />D2: {self.d2:.3f}<br />U1: {self.u1:.3f}<br /><br />Q1: {self.q1():.3f}'

    def lines(self):
        return [0, 0, 0, 0]


class AdvancedPipe(Model):
    """
    Concrete implementation of Model, representing a Pipe with changeable Ends.
    """

    def update(self, args):
        self.u1 = self.u1Param.real()

        self.i1 = self.i1Circ if self.i1ChoiceGroup.value == "Circle" else self.i1Rect
        self.i2 = self.i2Circ if self.i2ChoiceGroup.value == "Circle" else self.i2Rect

        self.i1dParam.set_active(self.i1.type == "Circle")
        self.i1wParam.set_active(self.i1.type == "Rectangle")
        self.i1hParam.set_active(self.i1.type == "Rectangle")

        self.i2dParam.set_active(self.i2.type == "Circle")
        self.i2wParam.set_active(self.i2.type == "Rectangle")
        self.i2hParam.set_active(self.i2.type == "Rectangle")

        if self.i1.type == "Circle":
            self.i1.d = self.i1dParam.real()
        else:
            self.i1.w = self.i1wParam.real()
            self.i1.h = self.i1hParam.real()
        self.i1.y = self.i1yParam.widget.max - self.i1yParam.real() + 75

        if self.i2.type == "Circle":
            self.i2.d = self.i2dParam.real()
        else:
            self.i2.w = self.i2wParam.real()
            self.i2.h = self.i2hParam.real()
        self.i2.y = self.i2yParam.widget.max - self.i2yParam.real() + 75

        super().update(args)
        if self.canvas is not None:
            self.draw()

       # self.rendering.geometry = CylinderBufferGeometry(self.i1.d / 2, self.i2.d / 2, 5, 16, 1)

    def __init__(self, i1: IntersectionForm, i2: IntersectionForm, u1, canvas=None):
        self.u1 = u1
        self.canvas = canvas

        self.i1Circ = i1 if i1.type == "Circle" else Circle(1, 0)
        self.i2Circ = i2 if i2.type == "Circle" else Circle(1, 0)
        self.i1Rect = i1 if i1.type == "Rectangle" else Rect(1, 1, 0)
        self.i2Rect = i2 if i2.type == "Rectangle" else Rect(1, 1, 0)

        self.i1 = i1
        self.i2 = i2

        self.i1.display(0)
        self.i2.display(0)

        self.rendering = Mesh(
            CylinderBufferGeometry(self.i1.d / 2, self.i2.d / 2, 5, 16, 1),
            position=[0, 0, 0],
            rotation=[0, 0, pymath.pi / 2, 'XYZ'],
            scale=[1, 3, 1],
            material=MeshLambertMaterial(color='red')
        )

        self.u1Param = FloatChangeable(u1, _min=u1, _max=u1 * 5, desc="U1: ", unit="m/s")
        self.i1ChoiceGroup = ToggleGroup(['Circle', 'Rectangle'], ['Choose a circular end', 'Choose a rectangular end'])
        self.i1dParam = FloatChangeable(self.i1.d if self.i1.type == "Circle" else 1, _min=1, _max=5, desc="Diameter: ",
                                        unit="m")
        self.i1dParam.set_active(self.i1.type == "Circle")

        self.i1wParam = FloatChangeable(self.i1.w if self.i1.type != "Circle" else 1, _min=1, _max=5, desc="Width: ",
                                        unit="m")
        self.i1hParam = FloatChangeable(self.i1.h if self.i1.type != "Circle" else 1, _min=1, _max=5, desc="Height: ",
                                        unit="m")
        self.i1wParam.set_active(self.i1.type == "Rectangle")
        self.i1hParam.set_active(self.i1.type == "Rectangle")
        self.i1yParam = FloatChangeable(self.i1.y, _min=-25, _max=25, desc="Y Position: ")

        self.i2ChoiceGroup = ToggleGroup(['Circle', 'Rectangle'], ['Choose a circular end', 'Choose a rectangular end'])
        self.i2dParam = FloatChangeable(self.i2.d if self.i2.type == "Circle" else 1, _min=1, _max=5, desc="Diameter: ",
                                        unit="m")
        self.i2dParam.set_active(self.i2.type == "Circle")

        self.i2wParam = FloatChangeable(self.i2.w if self.i2.type != "Circle" else 1, _min=1, _max=5, desc="Width: ",
                                        unit="m")
        self.i2hParam = FloatChangeable(self.i2.h if self.i2.type != "Circle" else 1, _min=1, _max=5, desc="Height: ",
                                        unit="m")
        self.i2wParam.set_active(self.i2.type == "Rectangle")
        self.i2hParam.set_active(self.i2.type == "Rectangle")
        self.i2yParam = FloatChangeable(self.i2.y, _min=-25, _max=25, desc="Y Position: ")

        self.params = [
            ChangeableContainer(
                [self.i1ChoiceGroup, self.i1dParam, self.i1wParam, self.i1hParam, self.i1yParam, self.u1Param]),
            ChangeableContainer([self.i2ChoiceGroup, self.i2dParam, self.i2wParam, self.i2hParam, self.i2yParam])
        ]

        self.i1.y = self.i1yParam.widget.max - self.i1yParam.real() + 75
        self.i2.y = self.i2yParam.widget.max - self.i2yParam.real() + 75
        if self.canvas is not None:
            self.canvas.layout.width = "100%"
            self.canvas.on_client_ready(self.draw)

    def q1(self):
        """
        Calculates the pressure of the water flowing in the pipe
        Invariance: Must be equal to self.q2()
        :return: the calculated pressure
        """
        if self.i1 is None:
            return 0
        return self.i1.area() * self.u1

    def q2(self):
        """
        Calculates the pressure of the water flowing in the pipe
        Invariance: Must be equal to self.q1()
        :return: the calculated pressure
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return self.i2.area() * self.u2()

    def u2(self):
        """
        Calculates the velocity of the water after flowing through the pipe
        :return: the velocity of the water at the second end
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return self.i1.area() / self.i2.area() * self.u1

    def dp(self):
        """
        Calculates the change of pressure in this pipe, depending on the height change
        :return: the change of pressure
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return self.u1 ** 2 - self.u2() ** 2 + self.i1yParam.real() - self.i2yParam.real()

    def calculate(self):
        if self.i1 is None or self.i2 is None:
            return f'Model is missing arguments. Please setup the model with two end points of type IntersectionForm.'
        return self.get_latex()

    def get_latex(self):
        q1 = Variable(self.q1(), unit='m^3s^{-1}')
        u2 = Variable(self.u2(), unit='m/s')
        dp = Variable(self.dp(), unit='Pa')
        return f'$\large Calculations \\\\ Q1 = Q2 = {self.i1.area():.2f} \cdot {self.u1} = {q1.rounded_latex()} \\\\ ' \
               f'U2 = \\frac{{{self.i1.area():.2f}}}{{{self.i2.area():.2f}}} \cdot {self.u1} = {u2.rounded_latex()} \\\\ ' \
               f'Change ~~ in ~~ pressure ~~ \Delta p = {self.u1:.2f}^2 - {self.u2():.2f}^2 + {self.i1yParam.real()} - {self.i2yParam.real()} = {dp.rounded_latex()}$'

    def lines(self):
        margin = 450
        i1Lines = get_lines("CIRC" if self.i1.type == "Circle" else "RECT", self.i1, 50)
        i2Lines = get_lines("CIRC" if self.i2.type == "Circle" else "RECT", self.i2, margin, end=True)

        l1 = i1Lines
        l2 = i2Lines

        l1c1 = l1[0]
        l1c2 = l2[0]
        l1c2r = [l1c2[2], l1c2[3], l1c2[0], l1c2[1]]
        l2c1 = l1[1]
        l2c1r = [l2c1[2], l2c1[3], l2c1[0], l2c1[1]]
        l2c2 = l2[1]

        l1c1c2 = (l1c1[2], l1c1[3], l1c2[2], l1c2[1])
        l2c1c2 = (l2c2[2], l2c2[3], l2c1[2], l2c1[1])

        return [l1c1, l1c1c2, l1c2r, l2c2, l2c1c2, l2c1r]
        # return [l1c1, l2c1, l1c2, l2c2, l1c1c2, l2c1c2]

    def draw(self, scale=10):
        argsi1 = self.i1.display(50)
        argsi2 = self.i2.display(450)
        self.canvas.clear()
        self.canvas.stroke_line(0, 0, self.canvas.width, 0)
        self.canvas.stroke_line(0, self.canvas.height - 1, self.canvas.width, self.canvas.height - 1)
        self.canvas.filter = "drop-shadow(-9px 9px 3px #ccc)"
        self.canvas.fill_style = hexcode((200, 182, 195))

        connectors = self.lines()
        self.canvas.begin_path()
        self.canvas.move_to(connectors[0][0], connectors[0][1])
        for connector in connectors:
            self.canvas.line_to(connector[0], connector[1])
            self.canvas.line_to(connector[2], connector[3])

        gradient = self.canvas.create_linear_gradient(
            connectors[0][0],
            connectors[0][1],  # Start position (x0, y0)
            connectors[2][2],
            connectors[2][3],  # End position (x1, y1)
            # List of color stops
            [
                (0, hexcode((222, 202, 215))),
                (0.5, "white"),
                (1, hexcode((158, 144, 153))),
            ],
        )

        self.canvas.fill_style = gradient
        self.canvas.fill()

        for connector in connectors:
            self.canvas.stroke_line(*connector)

        self.canvas.filter = "none"

        if self.i1.type == "Circle":
            self.draw_ellipse(argsi1[0], argsi1[1], argsi1[2] / 2, argsi1[2], hexcode((222, 202, 215)))
            # self.canvas.fill_circle(*argsi1)
        else:
            self.canvas.stroke_rect(*argsi1)
            self.canvas.fill_rect(*argsi1)
        if self.i2.type == "Circle":
            self.draw_ellipse(argsi2[0], argsi2[1], argsi2[2] / 2, argsi2[2], hexcode((158, 144, 153)))
        else:
            self.canvas.stroke_rect(*argsi2)
            self.canvas.fill_rect(*argsi2)
        self.draw_details()
        pass

    def draw_ellipse(self, x, y, rx, ry, fill_col="white", rot=0):
        self.canvas.begin_path()
        self.canvas.ellipse(x, y, rx, ry, rot, 0, 2 * pymath.pi)
        self.canvas.fill_style = fill_col
        self.canvas.stroke()
        self.canvas.fill()
        # self.canvas.end_path()

    def draw_details(self):
        hi1 = self.i1.y + (self.i1.ry / 8 if self.i1.type == "Circle" else self.i1.ry / 2)
        hi2 = self.i2.y + (self.i2.ry / 8 if self.i2.type == "Circle" else self.i2.ry / 2)
        if self.i1.y != self.i2.y:
            self.draw_heights(hi1, hi2)
        x1 = self.i1.x + (self.i1.rx / 4)
        x2 = x1 + 50
        self.draw_arrow_hor(x1, x2, hi1 - self.i1.ry / 4, 5, 10, (50, 50, 130), "")
        self.canvas.stroke_style = hexcode((50, 50, 130))
        self.canvas.stroke_text("U1", self.i1.x + self.i1.rx / 4 - 15 * 3, hi1 - self.i1.ry / 4 - 5)
        self.canvas.stroke_style = 'black'

    def draw_heights(self, hi1, hi2):
        halfLine1 = (0.0, hi1, self.canvas.width, hi1)
        halfLine2 = (0.0, hi2, self.canvas.width, hi2)

        if hi1 == hi2:
            return
        self.canvas.set_line_dash([10, 5])
        self.canvas.stroke_style = "gray"
        self.canvas.stroke_line(*halfLine1)
        self.canvas.stroke_line(*halfLine2)
        self.canvas.set_line_dash([0, 0])
        self.canvas.stroke_style = "black"
        xi = self.i2.rx + self.i2.x + 25
        self.canvas.stroke_line(xi, hi1, xi, hi2)
        self.canvas.stroke_text("Delta H", xi + 25, (hi1 + hi2) / 2)

    def draw_arrow_hor(self, x1, x2, y, y_offs, x_offs, rgb, label=""):
        self.canvas.stroke_style = hexcode(rgb)
        self.canvas.begin_path()
        self.canvas.move_to(x1, y)
        self.canvas.line_to(x2, y)
        self.canvas.line_to(x2 - x_offs, y + y_offs)
        self.canvas.move_to(x2, y)
        self.canvas.line_to(x2 - x_offs, y - y_offs)
        self.canvas.stroke()
        self.canvas.stroke_text(label, x1 - x_offs, y - y_offs)
        self.canvas.stroke_style = "black"

    def observe(self, func):
        for param in self.params:
            for p in param.params:
                p.observe(func)

    def get_drawing(self):
        data = self.canvas.get_image_data()
        dat_tex = DataTexture(data=data)
        plane = PlaneGeometry()
        planeMesh = Mesh(geometry=plane, material=MeshStandardMaterial(map=dat_tex), rotation=[pymath.pi, 0, 0, "XYZ"], position=[0, 0, -2])
        return dat_tex


class AdvancedPipe3D(AdvancedPipe):
    def draw(self):
        pass


def get_lines(selected, i, margin=0, offset=10, end=False):
    px1 = py = px2 = 0
    if selected == "CIRC":
        py = i.r + i.y
        px1 = i.r / 8 + i.x  # (margin if end else 0)
        if end:
            px2 = margin - i.rx - offset
        else:
            px2 = margin + i.rx + offset
    else:
        py = i.ry + i.y
        px1 = i.rx / 2 + i.x  # (margin if end else 0)
        if end:
            px2 = margin - i.rx - offset
        else:
            px2 = margin + i.rx + offset

    return [(px1, py, px2, py),
            (px1, py - (i.r * 2 if selected == "CIRC" else i.ry), px2, py - (i.r * 2 if selected == "CIRC" else i.ry))]


if __name__ == '__main__':
    m = AdvancedPipe(Circle(43, 30), Circle(43, 10), 20)
    m.i1.draw(50)
    m.i2.draw(450)
    print(m.lines())
