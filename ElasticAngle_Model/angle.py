import abc
import math as pymath
import threading, time

import matplotlib.pyplot as plt
import numpy as np

from demo import *
from abc import *
from ipycanvas import hold_canvas, Canvas


class Angle(Model):
    """
    Concrete implementation of Model for the angle model
    """
    def calculate(self):
        return str(self)

    def draw(self):
        if self.canvas is None:
            return
        #self.w_0 = self.circular_frequency().real()

        with hold_canvas():
            self.canvas.clear()
            phi = self.evaluate(self.t).real()
            self.canvas.fill_rect(50 + phi, 50, 20, 20)
            self.t = (self.t + 1) % 20
            self.canvas.sleep(20)

    def lines(self):
        pass

    def __init__(self, mass, feather, start_angle, c=None):
        self.mass = FloatChangeable(mass, unit="kg", base=0, _min=1.0, desc="Masse $~~m$")
        self.feather = FloatChangeable(feather, unit="kN/m", base=3, _min=1.0, desc="Federsteifigkeit $~~k$")
        self.start_angle = FloatChangeable(start_angle, unit="rad/s", _min=0.1, _max=pymath.pi / 2, step=0.001, desc="Anfangswinkelgeschwindigkeit $~~\Phi_0$")

        self.w_0 = self.circular_frequency().real()
        self.t = FloatChangeable(0, unit="s", _min=-self.duration().real() * 3, _max=self.duration().real() * 3, desc="Zeit $~~t$", continuous_update=True, step=self.duration().real() / 100, should_update=True)
        self.canvas = c

        self.params = [
            ChangeableContainer([self.mass, self.feather, self.start_angle], alignment='flex-start'),
            ChangeableContainer([HorizontalSpace(10)]),
            ChangeableContainer([self.t], alignment='flex-start')
        ]

    def circular_frequency(self):
        """
        Calculates the circular frequency of the system

        :return: Variable object containing the circular frequency [unit: rad/s]
        """
        return Variable(pymath.sqrt((2 * self.feather.real()) / ((5. / 3.) * self.mass.real())), unit='rad/s')

    def evaluate(self, t):
        """
        Evaluates the solution of the initial value problem for the given time

        :param t: time [unit: s]
        :return: Variable object of the angle [unit: rad]
        """
        self.w_0 = self.circular_frequency().real()
        a = self.start_angle.real() / self.w_0
        if type(t) == np.ndarray:
            return a * np.sin(self.w_0 * t)
        return Variable(a * np.sin(self.w_0 * t), unit='rad')

    def frequency(self):
        """
        Calculates the frequency of the system

        :return: Variable object containing the frequency [unit: Hz]
        """
        return Variable(self.w_0 / (2 * pymath.pi), unit='Hz')

    def duration(self):
        """
        Calculates the duration of the system

        :return: Variable object containing the duration [unit: s]
        """
        return Variable(1 / self.frequency().real(), unit='s')

    def get_evaluation(self):
        """
        Returns the evaluation of the solution of the initial value problem as a string

        :return: string containing the evaluation
        """
        w_0 = self.circular_frequency()
        return f'{(self.start_angle.real() / w_0.real()):.2f} * sin({w_0.real():.2f}t)'

    def __repr__(self):
        return table_style() + f'<table class="tg"><thead><tr><th class="tg-0gzz"><h1>Ergebnisse</h1></th></tr></thead>' \
                               f'<tbody><tr><td class="tg-tdqd">Eigenkreisfrequenz $w_0 = {self.circular_frequency().rounded_latex(2)}$</td></tr>' \
                               f'<tr><td class="tg-tdqd">Schwingungsdauer $T = {self.duration().rounded_latex(2)}$</td></tr>' \
                               f'<tr><td class="tg-tdqd">Eigenfrequenz $f_0 = {self.frequency().rounded_latex(2)}$</td></tr>' \
                               f'<tr><td class="tg-tdqd">Lösung des Anfangswertproblems $\phi(t) = {self.get_evaluation()} ~~ [\mathrm{{rad}}]$</td></tr>' \
                               f'<tr><td class="tg-tdqd">Lösung für $\phi({self.t.rounded()}) = {self.evaluate(self.t.real()).rounded_latex(2)}$</td></tr></tbody></table>' \

    def __str__(self):
        return self.__repr__()

    def observe(self, func):
        self.feather.observe(func)
        self.mass.observe(func)
        self.start_angle.observe(func)
        self.t.observe(func)


class AngleCanvas:
    """
    Represents the canvas for the angle model
    """
    def __init__(self, angle: Angle, plot: Plot, width=600, height=200, L=2):
        super().__init__()
        self.angle = angle
        self.plot = plot
        self.plot.grid()
        self.line = self.plot.add_line(0, color='red')
        self.canvas = Canvas(width=width, height=height)
        self.play_btn = ClickButton(
            description="Schwingung starten",
            disabled=False,
            button_style='primary',
            tooltip='Starts an animation of the model.',
        )
        self.play_btn.observe(self.start_oscilate)

        self.stop_btn = ClickButton(
            description="Schwingung stoppen",
            disabled=False,
            button_style='danger',
            tooltip='Stops the animation of the model.',
        )
        self.stop_btn.observe(self.stop_oscilate)

        self.t = 0
        self.L = L
        self.osc = None
        self.scale = width / height * 2.5
        self.canvas.on_client_ready(self.do_draw)
        self.oscilating = False
        self.lock = threading.Lock()

    def on_angle_changed(self, args):
        """
        Callback for when the angle changes

        :param args: Arguments for the oscilation
        :return: None
        """
        self.start_oscilate(args)

    def oscilate(self):
        """
        Thread that oscilates the visualization of the model

        :return: None
        """
        max_t = self.angle.duration().real()
        self.oscilating = True
        vals = np.linspace(0, max_t * 15, 500)
        plt.ioff()
        i = 0
        t = vals[i]
        while not (not self.oscilating and -0.01 < t % max_t < 0.01):
            t = vals[i]
            phi = self.angle.evaluate(t)
            with hold_canvas(self.canvas):
                # canvas.canvas.rotate(phi.real())
                self.draw(phi.real())
                self.plot.set_xlim([t - max_t, t + max_t])
                self.plot.update_line(self.line, [t])
                self.plot.flush()
            self.canvas.sleep(10)
            self.plot.sleep(0.01)
            i = (i + 1) % len(vals)
        self.canvas.reset_transform()
        self.draw()
        self.plot.set_xlim([-max_t, max_t])
        self.plot.update_line(self.line, [0])
        self.plot.flush()
        plt.ion()

    def pl_thr(self):
        """
        Thread that moves the plot along the oscilation

        :return: None
        """
        vals = np.linspace(0, 30, 100)
        for t in vals:
            phi = self.angle.evaluate(t)
            with hold_canvas(self.canvas):
                self.plot.mark(t, phi.real())
            time.sleep(0.002)

    def do_draw(self):
        self.draw()

    def draw_time(self, t):
        """
        Draws the model at a given time

        :param t: Time to draw the model at
        :return: None
        """
        self.draw(self.angle.evaluate(t).real())

    def draw(self, angle=0):
        """
        Draws the model at a given angle

        :param angle: the angle of the system
        :return: None
        """
        self.canvas.clear()
        self.canvas.reset_transform()
        self.canvas.scale(self.scale, self.scale)
        x = self.canvas.width / self.scale / 2
        y = 15
        self.canvas.fill_style = hexcode((230, 230, 230))
        cx = x
        cy = self.angle.mass.value / 2 + self.L + y - 5
        pivot = (cx, cy)

        s = np.sin(angle)
        c = np.cos(angle)

        px = x - cx
        py = y - cy

        xp = px * c - py * s
        yp = px * s + py * c

        x1 = x
        y1 = self.angle.mass.value / 2 + self.L + y - 5
        x2 = x - 5
        y2 = self.angle.mass.value / 2 + self.L + y
        x3 = x + 5
        y3 = self.angle.mass.value / 2 + self.L + y

        xp1, yp1 = self.rotate_point(pivot, (x1, y1), s, c)
        xp2, yp2 = self.rotate_point(pivot, (x2, y2), s, c)
        xp3, yp3 = self.rotate_point(pivot, (x3, y3), s, c)

        self.canvas.stroke_line(xp + cx, 9 + yp + cy, xp1 + cx,
                                self.angle.mass.value / 2 + y + self.L)
        self.canvas.fill_circle(xp + cx, yp + cy, 9)
        if self.osc is None:
            self.canvas.stroke_text('m', xp - 4.5 + cx, yp + 2 + cy)
        self.canvas.stroke_circle(xp + cx, yp + cy, 9)

        self.canvas.fill_style = hexcode((0, 0, 0))

        self.canvas.fill_polygon([(xp1 + cx, yp1 + cy),
                                  (xp2 + cx, yp2 + cy),
                                  (xp3 + cx, yp3 + cy),
                                  ])
        if self.osc is None:
            self.canvas.stroke_style = hexcode((20, 20, 20))
            self.canvas.font = "10px Arial"
            self.canvas.stroke_text('a', xp1 + cx - 9, yp1 + cy - 2)
            self.canvas.stroke_style = 'black'

        self.canvas.stroke_line(x, self.angle.mass.value / 2 + self.L + y + 5, x - 5,
                                self.angle.mass.value / 2 + self.L + y + 15)
        self.canvas.stroke_line(x, self.angle.mass.value / 2 + self.L + y + 5, x + 5,
                                self.angle.mass.value / 2 + self.L + y + 15)

        self.fancy_line(x - 10, x + 10, self.angle.mass.value / 2 + y + self.L + 15, x_offset=3)

        self.canvas.fill_style = hexcode((255, 255, 255))
        self.canvas.fill_arc(x, self.angle.mass.value / 2 + y + self.L + 5, 5, 0, pymath.pi)
        self.canvas.stroke_arc(x, self.angle.mass.value / 2 + y + self.L + 5, 5, 0, pymath.pi)

        self.canvas.fill_style = hexcode((230, 230, 230))

        xr1 = x - self.L
        yr1 = self.angle.mass.value / 2 + y + self.L
        xr2 = xr1 + self.L * 2
        yr2 = yr1
        xr3 = xr1 + self.L * 2
        yr3 = yr1 + 5
        xr4 = xr1
        yr4 = yr3

        xpr1, ypr1 = self.rotate_point(pivot, (xr1, yr1), s, c)
        xpr2, ypr2 = self.rotate_point(pivot, (xr2, yr2), s, c)
        xpr3, ypr3 = self.rotate_point(pivot, (xr3, yr3), s, c)
        xpr4, ypr4 = self.rotate_point(pivot, (xr4, yr4), s, c)

        xa1 = xr2
        ya1 = yr1 + 2.5
        xa2 = xr1
        ya2 = ya1

        xpa1, ypa1 = self.rotate_point(pivot, (xa1, ya1), s, c)
        xpa2, ypa2 = self.rotate_point(pivot, (xa2, ya2), s, c)

        self.canvas.fill_arc(xpa1 + cx, ypa1 + cy, 2.5, pymath.pi / 2,
                             3 * pymath.pi / 2, True)
        self.canvas.stroke_arc(xpa1 + cx, ypa1 + cy, 2.5, pymath.pi / 2,
                               3 * pymath.pi / 2, True)
        self.canvas.fill_arc(xpa2 + cx, ypa2 + cy, 2.5, pymath.pi / 2,
                             3 * pymath.pi / 2)
        self.canvas.stroke_arc(xpa2 + cx, ypa2 + cy, 2.5, pymath.pi / 2,
                               3 * pymath.pi / 2)

        self.canvas.fill_polygon(
            [(xpr1 + cx, ypr1 + cy), (xpr2 + cx, ypr2 + cy), (xpr3 + cx, ypr3 + cy), (xpr4 + cx, ypr4 + cy)])
        self.canvas.stroke_polygon(
            [(xpr1 + cx, ypr1 + cy), (xpr2 + cx, ypr2 + cy), (xpr3 + cx, ypr3 + cy), (xpr4 + cx, ypr4 + cy)])

        ezz1 = self.zigzag_stretch(xpr4 + cx, ypr4 + cy, xpr4 + cx, self.angle.mass.value / 2 + y + self.L + 5 + 20,
                                   x_offset=5, label='k' if self.osc is None else '')
        ezz2 = self.zigzag_stretch(xpr3 + cx, ypr3 + cy, xpr3 + cx, self.angle.mass.value / 2 + y + self.L + 5 + 20,
                                   x_offset=5, label='k' if self.osc is None else '')

        self.fancy_line(x - self.L - 10, x - self.L + 10, self.angle.mass.value / 2 + y + self.L + 5 + 20, x_offset=3)
        self.fancy_line(x + self.L - 10, x + self.L + 10, self.angle.mass.value / 2 + y + self.L + 5 + 20, x_offset=3)


    def rotate_point(self, pivot, point, s, c):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        :param pivot: the origin of the rotation
        :param point: the point to rotate
        :param s: the sine of the angle
        :param c: the cosine of the angle
        :return: the rotated point
        """
        cx, cy = pivot
        x, y = point
        px = x - cx
        py = y - cy
        xp = px * c - py * s
        yp = px * s + py * c
        return xp, yp

    def zigzag(self, x, y, steps=7, x_offset=10, y_offset=5, y1=None):
        """
        Draw a zigzag line

        :param x: the x coordinate of the start of the line
        :param y: the y coordinate of the start of the line
        :param steps: the number of steps in the zigzag
        :param x_offset: the x distance between each step
        :param y_offset: the y distance between each step
        :param y1: the y coordinate of the end of the line (if None, the end of the line is calculated)
        :return: the x and y coordinates of the end of the line
        """
        self.canvas.stroke_line(x, y, x, y + y_offset)
        self.canvas.stroke_line(x, y + y_offset, x - x_offset, y + y_offset * 2)
        for i in range(2, steps):
            x_0 = x + x_offset * (-1) ** (i - 1)
            y_0 = y + y_offset * i
            x_1 = x + x_offset * (-1) ** i
            y_1 = y + y_offset * (i + 1)
            self.canvas.stroke_line(x_0, y_0, x_1, y_1)
        self.canvas.stroke_line(x + x_offset * (-1) ** (steps - 1), y + y_offset * steps,
                                x, y + y_offset * (steps + 1))
        if y1 is None:
            self.canvas.stroke_line(x, y + y_offset * (steps + 1), x, y + y_offset * (steps + 2))
        else:
            self.canvas.stroke_line(x, y + y_offset * (steps + 1), x, y1)
        return x, y + y_offset * (steps + 2) if y1 is None else y1

    def zigzag_stretch(self, x0, y0, x1, y1, steps=7, x_offset=10, label=''):
        """
        Draw a zigzag line with a label that stretches between the start and end of the line

        :param x0: the x coordinate of the start of the line
        :param y0: the y coordinate of the start of the line
        :param x1: the x coordinate of the end of the line [same as x0]
        :param y1: the y coordinate of the end of the line
        :param steps: the number of steps in the zigzag
        :param x_offset: the x distance between each step (the y distance is calculated)
        :param label: the label to draw
        :return: the x and y coordinates of the end of the line
        """
        y_offset = abs(y1 - y0) / (steps + 2)
        ezz = self.zigzag(x0, y0, steps=steps, y_offset=y_offset, x_offset=x_offset)
        center = abs(y1 - y0) / 2 + min(y0, y1)
        self.canvas.stroke_text(label, x0 - 15, center)
        if ezz[1] < y1:
            self.canvas.stroke_line(x0, ezz[1], x0, y1)
        return x0, y1

    def fancy_line(self, x_0, x_1, y, x_offset=2.5, y_offset=5):
        """
        Draw a horizontal line with multiple diagonal vertical lines that extend from the horizontal line

        :param x_0: the x coordinate of the start of the horizontal line
        :param x_1: the x coordinate of the end of the horizontal line
        :param y: the y coordinate of the horizontal line
        :param x_offset: the x distance between each vertical line
        :param y_offset: the extent of each vertical line
        :return:
        """
        self.canvas.stroke_line(x_0, y, x_1, y)
        x = x_0
        while x < x_1 - x_offset:
            self.canvas.stroke_line(x, y + y_offset, x + x_offset, y)
            x += x_offset

    def start_oscilate(self, btn):
        """
        Start the oscillation thread of the system

        :param btn: catcher param
        :return: None
        """
        if self.osc is None:
            self.oscilating = True
            self.osc = threading.Thread(target=self.oscilate)
            self.osc.start()
            self.play_btn.disabled = True

    def stop_oscilate(self, btn):
        """
        Stops the oscillation thread of the system

        :param btn: catcher param
        :return: None
        """
        if self.oscilating:
            self.oscilating = False
            self.osc.join()
            self.play_btn.disabled = False
            self.osc = None
            self.pl = None
            self.draw(0)


def setup_angle(m, k, w):
    """
    Factory method for creating an angle object

    :param m: Mass of the angle
    :param k: Feathering coefficient of the angle
    :param w: Initial Angular velocity of the angle
    :return: an angle object
    """
    return Angle(m, k, w)
