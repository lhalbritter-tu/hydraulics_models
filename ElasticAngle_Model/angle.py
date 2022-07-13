import abc
import math as pymath
import threading, time

import numpy as np

from demo import *
from abc import *
from ipycanvas import hold_canvas, Canvas


class Angle(Model):
    def calculate(self):
        return str(self)

    def draw(self):
        if self.canvas is None:
            return

        with hold_canvas():
            self.canvas.clear()
            phi = self.evaluate(self.t).real()
            self.canvas.fill_rect(50 + phi, 50, 20, 20)
            self.t = (self.t + 1) % 20
            self.canvas.sleep(20)

    def lines(self):
        pass

    def __init__(self, mass, feather, start_angle, c=None):
        self.mass = FloatChangeable(mass, unit="kg", _min=1.0, desc="Mass m = ")
        self.feather = FloatChangeable(feather, unit="kN/m", base=3, _min=1.0, desc="Feather stiffness k = ")
        self.start_angle = FloatChangeable(start_angle, unit="rad", _min=0.1, desc="Initial angular velocity Phi(0) = ")
        self.t = FloatChangeable(0, unit="s", _min=0, _max=30, desc="Time t = ", continuous_update=True, step=0.0001)
        self.canvas = c

        self.params = [
            ChangeableContainer([self.mass, self.feather, self.start_angle]),
            ChangeableContainer([self.t])
        ]

    def circular_frequency(self):
        return Variable(pymath.sqrt((2 * self.feather.real()) / ((5. / 3.) * self.mass.real())), unit='rad/s')

    def evaluate(self, t):
        if t == 0:
            return self.start_angle
        w_0 = self.circular_frequency().real()
        return Variable((self.start_angle.real() / w_0) * pymath.sin(w_0 * t), unit='rad')

    def frequency(self):
        return Variable(self.circular_frequency().real() / (2 * pymath.pi), unit='Hz')

    def duration(self):
        return Variable(1 / self.frequency().real(), unit='s')

    def get_evaluation(self):
        w_0 = self.circular_frequency().real()
        return f'{self.start_angle.real() / w_0} * sin({w_0}t)'

    def __repr__(self):
        return f'$\large Elastisch ~~ gelagerter, ~~ starrer ~~ Winkel\\\\ ' \
               f'Masse ~~ m = {self.mass}\\\\ ' \
               f'Federsteifigkeit ~~ k = {self.feather}\\\\ ' \
               f'Anfangswinkelgeschwindigkeit ~~ phi_0 = {self.start_angle}\\\\ ' \
               f'\\\\Eigenkreisfrequenz ~~ w_0 = {self.circular_frequency()}\\\\ ' \
               f'Schwingungsdauer ~~ T = {self.duration()}\\\\ ' \
               f'Eigenfrequenz ~~ f_0 = {self.frequency()}\\\\ ' \
               f'Phi(t) = {self.get_evaluation()}$'

    def __str__(self):
        return self.__repr__()

    def observe(self, func):
        self.feather.observe(func)
        self.mass.observe(func)
        self.start_angle.observe(func)
        self.t.observe(func)


class AngleCanvas():
    def __init__(self, angle: Angle, width=600, height=200, L=5):
        super().__init__()
        self.angle = angle
        self.canvas = Canvas(width=width, height=height)
        self.canvas2 = Canvas(width=L * 2, height=50)
        self.play_btn = widgets.Button(
            description="Oscilate",
            disabled=False,
            button_style='',
            tooltip='Starts an animation of the model.',
        )
        self.play_btn.on_click(self.start_oscilate)

        self.canvas_box = widgets.VBox([self.canvas, widgets.HBox([self.play_btn])])
        self.t = 0
        self.L = L
        self.osc = None
        self.angle.observe(self.on_angle_changed)
        # self.draw(None)
        self.canvas.on_client_ready(self.do_draw)
        self.oscilating = False

    def on_angle_changed(self, args):
        self.draw_time(self.angle.t.real())

    def oscilate(self):
        #print("Running")
        max_t = self.angle.duration().real()
        self.oscilating = True
        vals = np.linspace(1, max_t, 120)
        #print(vals)
        for t in vals:
            with hold_canvas(self.canvas):
                phi = self.angle.evaluate(t)
                # canvas.canvas.rotate(phi.real())
                self.draw({'angle': phi.real()})
            self.canvas.sleep(20)
        print("I am outta here!")
        self.canvas.reset_transform()
        self.draw(None)
        self.stop_oscilate(None)

    def do_draw(self):
        self.draw(None)

    def draw_time(self, t):
        self.draw({
            'angle': self.angle.evaluate(t).real()
        })

    def draw(self, args):
        self.canvas.clear()
        self.canvas.rotate(0)
        x = self.canvas.width / 4
        y = 15
        self.canvas.fill_style = hexcode((230, 230, 230))
        self.canvas.fill_circle(x, y, 9)
        self.canvas.stroke_text('m', x - 4.5, y + 2)
        self.canvas.stroke_circle(x, y, 9)

        if args is not None:
            self.canvas.rotate(args['angle'])

        self.canvas.stroke_line(x, self.angle.mass.real() + y, x, self.angle.mass.real() / 2 + y + self.L)

        self.canvas.fill_style = hexcode((0, 0, 0))
        self.canvas.fill_polygon([(x, self.angle.mass.real() / 2 + self.L + y - 5),
                                  (x - 5, self.angle.mass.real() / 2 + self.L + y),
                                  (x + 5, self.angle.mass.real() / 2 + self.L + y),
                                  ])

        self.canvas.fill_style = hexcode((230, 230, 230))
        self.canvas.fill_rect(x - self.L, self.angle.mass.real() / 2 + y + self.L, self.L * 2, 5)
        self.canvas.stroke_rect(x - self.L, self.angle.mass.real() / 2 + y + self.L, self.L * 2, 5)

        ezz1 = self.zigzag(x - self.L, self.angle.mass.real() / 2 + y + self.L + 5, x_offset=5, y_offset=2.5)
        ezz2 = self.zigzag(x + self.L, self.angle.mass.real() / 2 + y + self.L + 5, x_offset=5, y_offset=2.5)

        self.fancy_line(ezz1[0] - 10, ezz1[0] + 10, ezz1[1], x_offset=3)
        self.fancy_line(ezz2[0] - 10, ezz2[0] + 10, ezz2[1], x_offset=3)

        self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x - 5, self.angle.mass.real() / 2 + self.L + y + 15)
        self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x + 5, self.angle.mass.real() / 2 + self.L + y + 15)
        self.canvas.fill_style = hexcode((255, 255, 255))
        self.canvas.fill_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)
        self.canvas.stroke_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)

        self.canvas.fill_arc(x + self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2, 3 * pymath.pi / 2, True)
        self.canvas.stroke_arc(x + self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2, 3 * pymath.pi / 2, True)
        self.canvas.fill_arc(x - self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2, 3 * pymath.pi / 2)
        self.canvas.stroke_arc(x - self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2, 3 * pymath.pi / 2)

        self.fancy_line(x - 10, x + 10, self.angle.mass.real() / 2 + y + self.L + 15, x_offset=3)

        self.canvas.reset_transform()

    def zigzag(self, x, y, steps=7, x_offset=10, y_offset=5):
        self.canvas.stroke_line(x, y, x, y + y_offset)
        self.canvas.stroke_line(x, y + y_offset, x - x_offset, y + y_offset * 2)
        for i in range(2, steps):
            x_0 = x + x_offset * (-1)**(i-1)
            y_0 = y + y_offset * i
            x_1 = x + x_offset * (-1)**i
            y_1 = y + y_offset * (i + 1)
            self.canvas.stroke_line(x_0, y_0, x_1, y_1)
        self.canvas.stroke_line(x + x_offset * (-1)**(steps - 1), y + y_offset * steps,
                                x, y + y_offset * (steps + 1))
        self.canvas.stroke_line(x, y + y_offset * (steps + 1), x, y + y_offset * (steps + 2))
        return (x, y + y_offset * (steps + 2))

    def fancy_line(self, x_0, x_1, y, x_offset=2.5, y_offset=5):
        self.canvas.stroke_line(x_0, y, x_1, y)
        x = x_0
        while x < x_1 - x_offset:
            self.canvas.stroke_line(x, y + y_offset, x + x_offset, y)
            x += x_offset

    def start_oscilate(self, btn):
        print("Start oscilate")
        if self.osc is None:
            self.osc = threading.Thread(target=self.oscilate)
            self.osc.start()
            self.play_btn.disabled = True

    def stop_oscilate(self, btn):
        print("STOP!")
        if self.osc is not None:
            self.oscilating = False
            self.play_btn.disabled = False
            self.osc = None



def setup_angle(m, k, w):
    return Angle(m, k, w)


if __name__ == '__main__':
    angle = setup_angle(9, 3, 0.2)
    for i in range(0, 30):
        print(angle.evaluate(i))
