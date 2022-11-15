import time
from abc import ABC
import abc
import math as pymath

import ipycanvas

from demo import *

ROW_START = "<div class='row'>"
COLUMN_START = "<div class='column'>"
DIV_END = "</div>"
G_CONSTANT = 9.81

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

    @abc.abstractmethod
    def describe(self, canvas, label="S", scale=1, y=0):
        """
        Draws a pin on the canvas, with the given label, marking the corresponding end of the pipe

        :param canvas: the canvas to draw on
        :param label: the label of the pin
        :param scale: the scale of the canvas
        :param y: the y coordinate of the pin
        :return: None
        """
        if canvas is None:
            print("Please specify a canvas")
            return self.type + "\n" + str(self)
        y0 = self.y
        y1 = (y - 20) / scale
        y2 = (y - 30) / scale
        y3 = (y - 50) / scale
        canvas.stroke_style = "black"
        canvas.dash_style = "solid"
        canvas.line_width = 1 / scale
        x = self.rx / 8 + self.x
        canvas.stroke_line(x / scale, y0, x / scale, y1)
        canvas.stroke_circle(x / scale, y1 - 7.5, 7.5 / scale)
        old_fill_style = canvas.fill_style
        canvas.fill_style = "black"
        i = 0
        for text in label:
            i += 10
            canvas.fill_text(text, (x - 7.5 / 2) / scale, y1 - 7.5 / 2)
        canvas.dash_style = "dashed"
        canvas.fill_style = old_fill_style
        return x, y2


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

    def describe(self, canvas, label="S", scale=1, model=None, y=0):
        x, y = super().describe(canvas, label, scale, y=y)
        #if not y.isnumeric():
            #return y
        if model is None:
            canvas.stroke_circle(x / scale, 0, 5 / scale)
        else:
            model.dash_ellipse(x / scale, 1 + min(max(self.ry, 5), 10), min(max(5 / scale, self.ry / scale), 10 / scale), min(max(self.ry / scale, 5 / scale), 10 / scale))
            model.draw_arrow_hor(x / scale, (x + min(max(self.ry, 5), 10)) / scale, 5 + min(max(self.ry, 5), 10) * 2, 2, 1.5, (0, 0, 0), label="D" + label[0][-1], left=False)
            model.draw_arrow_hor(x / scale, (x - min(max(self.ry, 5), 10)) / scale, 5 + min(max(self.ry, 5), 10) * 2, -2, -1.5, (0, 0, 0), label="", left=True)
        canvas.dash_style = "solid"



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
        self.rx = 8
        self.ry = self.h * 5
        return self.x, self.y - self.ry / 2, 2, self.ry

    def describe(self, canvas, label="S", scale=1, model=None, y=0):
        x, y = super().describe(canvas, label, scale, y=y)
        #if not y.isnumeric():
            #return y
        if model is None:
            canvas.stroke_rect((x - self.rx) / scale, y, 5 / scale, 5 / scale)
        else:
            model.dash_rect(x / scale, 1 + min(max(self.ry, 5), 10),
                               min(max(5 / scale, self.rx / scale), 10 / scale),
                               min(max(self.ry / scale, 5 / scale), 10 / scale))
            model.draw_arrow_hor(x / scale, (x + min(max(self.rx, 5), 10)) / scale, 5 + min(max(self.ry, 5), 10) * 2, 2,
                                 1.5, (0, 0, 0), label="H" + label[0][-1], left=False)
            model.draw_arrow_hor(x / scale, (x - min(max(self.rx, 5), 10) / 4) / scale, 5 + min(max(self.ry, 5), 10) * 2,
                                 -2, -1.5, (0, 0, 0), label="", left=True)
            model.draw_arrow_vert((x - min(max(self.rx, 5), 10) / 4 - 2.5) / scale, (1 + min(max(self.ry, 5), 10)) / scale,
                                  (1 + min(max(self.ry, 5), 10)) / scale, -2, -1.5, (0, 0, 0), label="W" + label[0][-1], top=True)
            model.draw_arrow_vert((x - min(max(self.rx, 5), 10) / 4 - 2.5) / scale, (1 + min(max(self.ry, 5), 10)) / scale,
                                  (1 + min(max(self.ry, 5), 10) * 2) / scale, 2, 1.5, (0, 0, 0), label="", top=False)
        canvas.dash_style = "solid"


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
        #self.u1 = self.u1Param.real()
        cur_q = self.q
        self.q = self.qParam.real()

        i1Type = self.i1.type
        i2Type = self.i2.type

        self.i1 = self.i1Circ if self.i1ChoiceGroup.value == "Circle" else self.i1Rect
        self.i2 = self.i2Circ if self.i2ChoiceGroup.value == "Circle" else self.i2Rect

        self.i1dParam.set_active(self.i1.type == "Circle")
        self.i1wParam.set_active(self.i1.type == "Rectangle")
        self.i1hParam.set_active(self.i1.type == "Rectangle")

        self.i2dParam.set_active(self.i2.type == "Circle")
        self.i2wParam.set_active(self.i2.type == "Rectangle")
        self.i2hParam.set_active(self.i2.type == "Rectangle")

        if i1Type != self.i1.type or i2Type != self.i2.type:
            self.callback.update_input()

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
        if cur_q == self.q:
            self.draw()

       # self.rendering.geometry = CylinderBufferGeometry(self.i1.d / 2, self.i2.d / 2, 5, 16, 1)

    def __init__(self, i1: IntersectionForm, i2: IntersectionForm, u1, canvas=None, margin_left=50, margin_right=50):
        if canvas is not None:
            canvas.layout.width = 'auto'
            canvas.layout.height = '40%'
            self.scale = canvas.width / canvas.height * 2.5
            #self.scale = 1
            #canvas.font = f'{self.scale * 2}px serif'
            self.margin = canvas.width - margin_left - margin_right
        #self.u1 = u1
        self.canvas = canvas

        self.margin_left = margin_left
        self.margin_right = margin_right

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

        self.u1Param = FloatChangeable(u1, _min=u1, _max=u1 * 5, desc="$U_1$: ", unit="ms^{-1}")
        self.qParam = FloatChangeable(7.85, _min=0, _max=100, desc="$Q_1$", unit="m^3s^{-1}", step=0.01)
        self.q = self.qParam.real()
        shLabel = widgets.HTML(f"SHAPE")
        shLabel.add_class("heading")
        self.i1ChoiceGroup = DropDownGroup(['Circle', 'Rectangle'], ['Choose a circular end', 'Choose a rectangular end'])
        self.i1ChoiceWidget = BoxVertical([shLabel, self.i1ChoiceGroup.display])
        self.i1dParam = FloatChangeable(self.i1.d if self.i1.type == "Circle" else 1, _min=0.1, _max=5, desc="Diameter $D_1$",
                                        unit="m", step=0.01)
        self.i1dParam.set_active(self.i1.type == "Circle")

        self.i1wParam = FloatChangeable(self.i1.w if self.i1.type != "Circle" else 1, _min=1, _max=5, desc="Width $W_1$",
                                        unit="m")
        self.i1hParam = FloatChangeable(self.i1.h if self.i1.type != "Circle" else 1, _min=1, _max=5, desc="Height $H_1$",
                                        unit="m")
        self.i1wParam.set_active(self.i1.type == "Rectangle")
        self.i1hParam.set_active(self.i1.type == "Rectangle")
        self.i1yParam = FloatChangeable(self.i1.y, _min=-25, _max=25, desc="Z Position $z_1$", unit="m")

        self.i2ChoiceGroup = DropDownGroup(['Circle', 'Rectangle'],
                                           ['Choose a circular end', 'Choose a rectangular end'])
        self.i2ChoiceWidget = BoxVertical([shLabel, self.i2ChoiceGroup.display], spacing=0)
        self.i2dParam = FloatChangeable(self.i2.d if self.i2.type == "Circle" else 1, _min=0.1, _max=5, desc="Diameter $D_2$",
                                        unit="m", step=0.01)
        self.i2dParam.set_active(self.i2.type == "Circle")

        self.i2wParam = FloatChangeable(self.i2.w if self.i2.type != "Circle" else 1, _min=1, _max=5, desc="Width $W_2$",
                                        unit="m")
        self.i2hParam = FloatChangeable(self.i2.h if self.i2.type != "Circle" else 1, _min=1, _max=5, desc="Height $H_2$",
                                        unit="m")
        self.i2wParam.set_active(self.i2.type == "Rectangle")
        self.i2hParam.set_active(self.i2.type == "Rectangle")
        self.i2yParam = FloatChangeable(self.i2.y, _min=-25, _max=25, desc="Z Position $z_2$", unit="m")

        self.params = [
            ChangeableContainer(
                [self.i1ChoiceWidget, self.i1dParam, self.i1wParam, self.i1hParam, self.i1yParam]),
            ChangeableContainer([HorizontalSpace(count=15)]),
            ChangeableContainer([self.i2ChoiceWidget, self.i2dParam, self.i2wParam, self.i2hParam, self.i2yParam]),
            ChangeableContainer([self.qParam])
        ]
        self.i1.y = self.i1yParam.widget.max - self.i1yParam.real() + 75
        self.i2.y = self.i2yParam.widget.max - self.i2yParam.real() + 75
        #if self.canvas is not None:
            #self.canvas.layout.width = "100%"
        #    self.canvas.on_client_ready(self.draw)

    def q1(self):
        """
        Calculates the pressure of the water flowing in the pipe
        Invariance: Must be equal to self.q2()
        :return: the calculated pressure
        """
        if self.i1 is None:
            return 0
        return self.i1.area() * self.u1()

    def q2(self):
        """
        Calculates the pressure of the water flowing in the pipe
        Invariance: Must be equal to self.q1()
        :return: the calculated pressure
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return self.i2.area() * self.u2()

    def u1(self):
        """
        Calculates the velocity of the water flowing in the pipe

        :return: the velocity of the water flowing in the pipe (q / side 1 area)
        """
        return self.q / self.i1.area()

    def u1Var(self):
        """
        Returns u1 as Variable object with unit "ms^{-1}"

        :return: Variable object of u1
        """
        return Variable(self.u1(), "ms^{-1}")

    def u2(self):
        """
        Calculates the velocity of the water after flowing through the pipe
        :return: the velocity of the water at the second end
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return self.i1.area() / self.i2.area() * self.u1()

    def u2Var(self):
        """
        Returns u2 as Variable object with unit "ms^{-1}"

        :return: Variable object of u2
        """
        return Variable(self.u2(), "ms^{-1}")

    def dp(self):
        """
        Calculates the change of pressure in this pipe, depending on the height change
        :return: the change of pressure
        """
        if self.i1 is None or self.i2 is None:
            return 0
        return (self.u1() ** 2 - self.u2() ** 2) / (2 * G_CONSTANT) + self.i1yParam.real() - self.i2yParam.real()

    def calculate(self):
        if self.i1 is None or self.i2 is None:
            return f'Model is missing arguments. Please setup the model with two end points of type IntersectionForm.'
        return self.get_latex()

    def table(self):
        table = table_style() + f"""
<table class="tg" width="100%" height="100%" margin-right="15%">
<thead>
  <tr>
    <th class="tg-0gzz"><h1>Side 1 {spaces(5)}</h1></th>
    <th class="tg-0gzz"><h1>Side 2 {spaces(5)}</h1></th>
    <th class="tg-0gzz"><h1>Explanation {spaces(5)} </h1></th>
    <th class="tg-0gzz"><h1>Unit {spaces(2)}</h1></th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-tdqd">${{Q_1 = }}$</td>
    <td class="tg-tdqd">${{Q_2 = }}$</td>
    <td class="tg-tdqd">${{Q = {self.q:.3f}}}$ - mass conservation</td>
    <td class="tg-tdqd">${Variable("", 0, "m^3s^{-1}").latex().replace('~', '')}$</td>
  </tr>
  <tr>
    <td class="tg-tdqd">${{U_1 = {self.u1():.3f}}}$</td>
    <td class="tg-tdqd">${{U_2 = {self.u2():.3f}}}$</td>
    <td class="tg-tdqd">${{\Delta U = {self.u1() - self.u2():.3f}}}$ - {"Sides are not equal" if self.u1() != self.u2() else "Sides are equal"}</td>
    <td class="tg-tdqd">${Variable("", 0, "ms^{-1}").latex().replace('~', '')}$</td>
  </tr>
</tbody>
</table>"""
        return table

    def get_latex(self):
        q1 = Variable(self.q1(), unit='m^3s^{-1}')
        u1 = Variable(self.u1(), unit='ms^{-1}')
        #q2 = Variable(self.q2(), unit='m^3s^{-1}')
        u2 = Variable(self.u2(), unit='ms^{-1}')
        dp = Variable(self.dp(), unit='m')
        return f'{self.table()}<br />' \
               f'<table class="tg" width="100%" height="100%" margin-right="15%">' \
               f'<thead><tr><th class="tg-0gzz"><h1>Difference in Pressure</h1></th></tr></thead>' \
               f'<tbody><tr><td class="tg-tdqd">$\Delta E = \Delta h + \\frac{{\Delta p}}{{\\rho \cdot g}} + \\frac{{\Delta U^2}}{{2 \cdot g}}$</td></tr>' \
               f'<tr><td class="tg-tdqd">$\Delta E = 0$ - energy conservation, because of frictionless flow</td></tr>' \
               f'<tr><td class="tg-tdqd">$\\rightarrow 0 = (z_1 - z_2) + \\frac{{\Delta p}}{{\\rho \cdot g}} + \\frac{{(U_1^2 - U_2^2)}}{{2 \cdot g}}$</td></tr>' \
               f'<tr><td class="tg-tdqd">$\\Rightarrow \\frac{{\Delta p}}{{\\rho \cdot g}} = \\frac{{({u1.real()**2:.3f} - {u2.real()**2:.3f})}}{{2 \cdot g}} + ({self.i1yParam.real():.3f} - {self.i2yParam.real():.3f})$</td></tr>' \
               f'<tr><td class="tg-tdqd">$\\frac{{\Delta p}}{{\\rho \cdot g}} = {(u1.real()**2 - u2.real()**2) / (2 * G_CONSTANT):.3f} + {self.i1yParam.real() - self.i2yParam.real():.3f} = {dp.rounded_latex(3)}$</td></tr>' \
               f'</tbody></table>' \


    def lines(self):
        """
        Returns the lines of the pipe between the two ends with horizontal sections before and after the ends

        :return: List of lines inbetween the two ends [size: 6]
        """
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

    def direct_lines(self):
        """
        Returns the lines of the pipe between the two ends with no horizontal sections before and after the ends

        :return: List of lines inbetween the two ends [size: 2]
        """
        i1Lines = get_lines("CIRC" if self.i1.type == "Circle" else "RECT", self.i1, self.margin_left / self.scale)
        i2Lines = get_lines("CIRC" if self.i2.type == "Circle" else "RECT", self.i2, self.margin / self.scale, end=True)

        x0 = i1Lines[0][0]
        y0 = i1Lines[0][1]
        x1 = i2Lines[0][0]
        y1 = i2Lines[0][1]

        l1 = [x0, y0, x1, y1]

        x0 = i1Lines[1][0]
        y0 = i1Lines[1][1]
        x1 = i2Lines[1][0]
        y1 = i2Lines[1][1]

        l2 = [x1, y1, x0, y0]

        return [l1, l2]

    def draw(self, scale=10):
        #if self.canvas is None:
        #    return
        self.canvas.clear()
        self.canvas.reset_transform()
        self.canvas.scale(self.scale, self.scale)
        argsi1 = self.i1.display(self.margin_left / self.scale)
        argsi2 = self.i2.display(self.margin / self.scale)
        #argsi1 = [arg / self.scale for arg in argsi1]
        #argsi2 = [arg / self.scale for arg in argsi2]
        #self.canvas.stroke_line(0, 0, self.canvas.width, 0)
        #self.canvas.stroke_line(0, self.canvas.height - 1, self.canvas.width, self.canvas.height - 1)
        self.canvas.filter = "drop-shadow(-9px 9px 3px #ccc)"
        #self.canvas.line_width = 1 / self.scale
        self.canvas.fill_style = hexcode((200, 182, 195))

        connectors = self.direct_lines()
        #connectors = [[arg / self.scale for arg in connector] for connector in connectors]
        self.canvas.begin_path()
        self.canvas.move_to(connectors[0][0], connectors[0][1])
        for connector in connectors:
            self.canvas.line_to(connector[0], connector[1])
            self.canvas.line_to(connector[2], connector[3])

        gradient = self.canvas.create_linear_gradient(
            connectors[0][0],
            connectors[1][3],  # End position (x1, y1)
            connectors[1][2],
            connectors[0][1],  # Start position (x0, y0)
            # List of color stops
            [
                (0, hexcode((225, 225, 225))),
                #(0.2, hexcode((158, 144, 153))),
                (1, hexcode((100, 94, 97))),
            ],
        )

        if self.i1yParam.real() < self.i2yParam.real():
            gradient = self.canvas.create_linear_gradient(
            connectors[0][0],
            connectors[0][3],  # End position (x1, y1)
            connectors[1][2],
            connectors[0][1],  # Start position (x0, y0)
            # List of color stops
            [
                (0, hexcode((225, 225, 225))),
                #(0.2, hexcode((158, 144, 153))),
                (1, hexcode((100, 94, 97))),
            ],
            )
        if self.i1yParam.real() > self.i2yParam.real():
            gradient = self.canvas.create_linear_gradient(
            connectors[1][2],
            connectors[0][1],  # Start position (x0, y0)
            connectors[0][0],
            connectors[0][3],  # End position (x1, y1)
            # List of color stops
            [
                (0, hexcode((225, 225, 225))),
                #(0.2, hexcode((158, 144, 153))),
                (1, hexcode((100, 94, 97))),
            ],
            )

        self.canvas.fill_style = gradient
        self.canvas.fill()

        for connector in connectors:
            self.canvas.stroke_line(*connector)

        self.canvas.filter = "none"

        if self.i1.type == "Circle":
            self.draw_ellipse(argsi1[0], argsi1[1], argsi1[2] / 2, argsi1[2], gradient)
            # self.canvas.fill_circle(*argsi1)
        else:
            argsi1 = list(argsi1)
            argsi1[0] -= argsi1[2]
            self.canvas.stroke_rect(*argsi1)
            self.canvas.fill_rect(*argsi1)
        if self.i2.type == "Circle":
            self.draw_ellipse(argsi2[0], argsi2[1], argsi2[2] / 2, argsi2[2], gradient)
        else:
            self.canvas.stroke_rect(*argsi2)
            self.canvas.fill_rect(*argsi2)
        self.draw_details()
        y_max = min(self.i1.y, self.i2.y)
        r_max = max(self.i1.ry, self.i2.ry)
        self.i1.describe(self.canvas, ["S₁"], 1, model=self, y=y_max - r_max / 2)
        self.i2.describe(self.canvas, ["S₂"], 1, model=self, y=y_max - r_max / 2)
        pass

    def draw_ellipse(self, x, y, rx, ry, fill_col="white", rot=0):
        """
        Draw an ellipse on the canvas

        :param x: the x-position of the ellipse
        :param y: the y-position of the ellipse
        :param rx: the x-radius of the ellipse
        :param ry: the y-radius of the ellipse
        :param fill_col: the fill color of the ellipse
        :param rot: the rotation of the ellipse
        :return: None
        """
        self.canvas.begin_path()
        self.canvas.ellipse(x, y, rx, ry, rot, 0, 2 * pymath.pi)
        self.canvas.fill_style = fill_col
        self.canvas.stroke()
        self.canvas.fill()
        # self.canvas.end_path()

    def dash_ellipse(self, x, y, rx, ry, fill_col="white", rot=0):
        """
        Draw an ellipse on the canvas with a dashed line
        See draw_ellipse for parameters

        :return: None
        """
        i = 0
        while i <= 2:
            self.canvas.begin_path()
            self.canvas.ellipse(x, y, rx, ry, rot, i * pymath.pi, (i + 0.2) * pymath.pi)
            i += 0.3
            self.canvas.stroke()

    def draw_details(self):
        """
        Draws the details of the model, such as the height lines and the coordinate system
        :return:
        """
        hi1 = self.i1.y + self.i1.ry / 8
        hi2 = self.i2.y + self.i2.ry / 8
        xi = self.i2.rx / 2 + self.i2.x + 25
        if self.i1.y != self.i2.y:
            self.draw_heights(hi1, hi2)
        x1 = self.i1.x + (self.i1.rx / 4)
        x2 = x1 + 50
        self.draw_arrow_hor(x1, x2, (hi1 - self.i1.ry / 4), 5, 10, (50, 50, 130), "U₁")
        self.canvas.stroke_style = hexcode((50, 50, 130))
        self.canvas.stroke_style = 'black'
        self.draw_arrow_hor(xi / 2, xi / 2 + 20, 25, 5, 10, (0, 0, 0), label="x", left=False)
        self.draw_arrow_vert(xi / 2, 25, 5, 5, 10, (0, 0, 0), label="z", top=True)

    def draw_heights(self, hi1, hi2):
        """
        Draws the heights of the two ends of the pipe

        :param hi1: the height of the first end
        :param hi2: the height of the second end
        :return:
        """
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
        self.draw_arrow_vert(xi, hi1, hi2, -2.5, 4, (0, 0, 0), label="Δh", top=True)
        self.draw_arrow_vert(xi, hi2, hi1, 2.5, 4, (0, 0, 0), label="", top=False)
        return xi

    def draw_arrow_hor(self, x1, x2, y, y_offs, x_offs, rgb, label="", left=True):
        """
        Draws a horizontal arrow on the canvas

        :param x1: the x-position of the start of the arrow
        :param x2: the x-position of the end of the arrow
        :param y: the y-position of the arrow
        :param y_offs: the y-offset of the arrow head
        :param x_offs: the x-offset of the arrow head
        :param rgb: the color of the arrow as a tuple of form (r, g, b)
        :param label: the label of the arrow, written on the arrow head
        :param left: whether the arrow points to the left or to the right
        :return: None
        """
        self.canvas.stroke_style = hexcode(rgb)
        self.canvas.begin_path()
        self.canvas.move_to(x1, y)
        self.canvas.line_to(x2, y)
        self.canvas.line_to(x2 - x_offs, y + y_offs)
        self.canvas.move_to(x2, y)
        self.canvas.line_to(x2 - x_offs, y - y_offs)
        self.canvas.stroke()
        old_fill_style = self.canvas.fill_style
        self.canvas.fill_style = hexcode(rgb)
        if left:
            self.canvas.fill_text(label, x1 - x_offs, y - y_offs)
        else:
            self.canvas.fill_text(label, x2 + x_offs, y - y_offs)
        self.canvas.stroke_style = "black"
        self.canvas.fill_style = old_fill_style

    def draw_arrow_vert(self, x, y1, y2, x_offs, y_offs, rgb, label="", top=True):
        """
        Draws a vertical arrow on the canvas

        :param x: the x-position of the arrow
        :param y1: the y-position of the start of the arrow
        :param y2: the y-position of the end of the arrow
        :param x_offs: the x-offset of the arrow head
        :param y_offs: the y-offset of the arrow head
        :param rgb: the color of the arrow as a tuple of form (r, g, b)
        :param label: the label of the arrow, written on the arrow head
        :param top: whether the arrow points to the top or to the bottom
        :return: None
        """
        self.canvas.stroke_style = hexcode(rgb)
        y_top = min(y1, y2)
        y_bot = max(y1, y2)
        self.canvas.begin_path()
        self.canvas.move_to(x, y1)
        self.canvas.line_to(x, y2)
        if y_top == y1:
            self.canvas.line_to(x + x_offs, y2 - y_offs)
            self.canvas.move_to(x, y2)
            self.canvas.line_to(x - x_offs, y2 - y_offs)
        else:
            self.canvas.line_to(x + x_offs, y2 + y_offs)
            self.canvas.move_to(x, y2)
            self.canvas.line_to(x - x_offs, y2 + y_offs)
        self.canvas.stroke()
        old_fill_style = self.canvas.fill_style
        self.canvas.fill_style = hexcode(rgb)
        if top:
            self.canvas.fill_text(label, x - x_offs * 2.5, y_top + y_offs)
        else:
            self.canvas.fill_text(label, x - x_offs, y_bot - y_offs)
        self.canvas.stroke_style = "black"
        self.canvas.fill_style = old_fill_style

    def observe(self, func):
        for param in self.params:
            for p in param.params:
                if p.should_update:
                    p.observe(func)

    def get_drawing(self):
        data = self.canvas.get_image_data()
        dat_tex = DataTexture(data=data)
        plane = PlaneGeometry()
        planeMesh = Mesh(geometry=plane, material=MeshStandardMaterial(map=dat_tex), rotation=[pymath.pi, 0, 0, "XYZ"], position=[0, 0, -2])
        return dat_tex

    def dash_rect(self, x, y, sx, sy):
        """
        Draws a dashed rectangle on the canvas

        :param x: the x-position of the top-left corner of the rect
        :param y: the y-position of the top-left corner of the rect
        :param sx: the scale to the x-direction
        :param sy: the scale to the y-direction
        :return: None
        """
        c = self.canvas
        c.set_line_dash([1, 0.5])
        c.stroke_rect(x, y, sx, sy)
        c.set_line_dash([0, 0])


def get_lines(selected, i, margin=0, end=False):
    """
    Gets the lines of the selected Side

    :param selected: the selected Side ["CIRC", "RECT"]
    :param i: the side object
    :param margin: the margin to the side
    :param end: whether this side is the end or start
    :return: the lines of the selected Side
    """
    offset = i.rx / 2
    py1 = i.ry + i.y - (0 if selected == "CIRC" else i.ry / 2)
    py2 = py1 - i.ry * (2 if selected == "CIRC" else 1)

    px1 = i.rx / 2 + i.x - offset
    px2 = margin - i.rx if end else margin + i.rx

    return [(px1, py1, px2, py1), (px1, py2, px2, py2)]
