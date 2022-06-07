from abc import ABC
import abc
import math

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.Qt import QRectF


class IntersectionForm(ABC):
    def __init__(self, y, type):
        self.y = y
        self.type = type

    @abc.abstractmethod
    def area(self):
        pass

    @abc.abstractmethod
    def draw(self, dw=0):
        pass

    @abc.abstractmethod
    def display(self, dw=0):
        pass


class Circle(IntersectionForm):
    def __init__(self, d, y):
        super().__init__(y, "Circle")
        self.d = d
        self.r = self.d * 100 / 2

    def area(self):
        return (math.pi * self.d ** 2) / 4

    def __str__(self):
        return "D: " + str(self.d)

    def draw(self, dw=0):
        self.x = dw
        self.r = self.d * 100 / 2
        return QRectF(self.x, self.y, self.r / 4, self.r)
        pass

    def display(self, dw=0):
        self.x = dw
        return (self.x, self.y, self.d)


class Rect(IntersectionForm):
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
        return QGraphicsRectItem(self.x, self.y, self.w, self.h)

    def display(self, dw=0):
        self.x = dw
        return self.x, self.y, self.w, self.h


class Model(ABC):
    @abc.abstractmethod
    def calculate(self):
        pass


class SimplePipe(Model):
    def __init__(self, d1, d2, u1):
        self.d1 = d1
        self.d2 = d2
        self.u1 = u1

    def q1(self):
        return (math.pi * self.d1 ** 2) / 4 * self.u1

    def q2(self):
        return (math.pi * self.d2 ** 2) / 4 * self.u2()

    def u2(self):
        return (self.d1 ** 2) / (self.d2 ** 2) * self.u1

    def calculate(self):
        return "D1: " + str(self.d1) + "<br />D2: " + str(self.d2) + "<br />U1: " + str(self.u1) + "<br /><br />Q1 = " + \
               str(self.q1()) + "<br />Q2 = " + str(self.q2()) + "<br />U2 = " + str(self.u2())
        # return f'D1: {self.d1:.3f}<br />D2: {self.d2:.3f}<br />U1: {self.u1:.3f}<br /><br />Q1: {self.q1():.3f}'


class AdvancedPipe(Model):
    def __init__(self, i1: IntersectionForm, i2: IntersectionForm, u1):
        self.u1 = u1
        self.i1 = i1
        self.i2 = i2

    def q1(self):
        return self.i1.area() * self.u1

    def q2(self):
        return self.i2.area() * self.u2()

    def u2(self):
        return self.i1.area() / self.i2.area() * self.u1

    def dp(self):
        return self.u1 ** 2 - self.u2() ** 2 + -self.i1.y - -self.i2.y

    def calculate(self):
        return f'Q1 = Q2 = {self.i1.area():.2f} * {self.u1} = {self.q1():.2f}\nU2 = {self.i1.area():.2f} / {self.i2.area():.2f} * {self.u1} = {self.u2():.2f}' \
               f'\nChange in Pressure delta p = {self.u1 ** 2:.2f} - {self.u2() ** 2:.2f} + {-self.i1.y} - {-self.i2.y} = {self.dp():.2f}'


def get_lines(selected, i, margin=0, end=False):
    px1 = py = px2 = 0
    if selected == "CIRC":
        py = i.d + i.y
        px1 = i.d / 2 + i.x  # (margin if end else 0)
        if end:
            px2 = margin - i.d
        else:
            px2 = margin + i.d
    else:
        py = i.h + i.y
        px1 = i.w / 2 + (margin if end else 0)
        if end:
            px2 = margin - i.w
        else:
            px2 = margin / 4 + i.w

    return [(px1, py, px2, py),(px1, py - (i.d * 2 if selected == "CIRC" else i.h), px2, py - (i.d * 2 if selected == "CIRC" else i.h))]

