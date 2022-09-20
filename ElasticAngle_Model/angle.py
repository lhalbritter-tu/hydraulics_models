import abc
import math as pymath
import threading, time

import matplotlib.pyplot as plt
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
        self.mass = FloatChangeable(mass, unit="kg", base=0, _min=1.0, desc="Mass m = ")
        self.feather = FloatChangeable(feather, unit="kN/m", base=3, _min=1.0, desc="Feather stiffness k = ")
        self.start_angle = FloatChangeable(start_angle, unit="rad", _min=0.1, _max=pymath.pi / 2, step=0.001, desc="Initial angular velocity Phi(0) = ")
        self.t = FloatChangeable(0, unit="s", _min=0, _max=30, desc="Time t = ", continuous_update=True, step=30.303 / 100, should_update=False)
        self.canvas = c

        self.w_0 = self.circular_frequency().real()

        self.params = [
            ChangeableContainer([self.mass, self.feather, self.start_angle]),
            ChangeableContainer([self.t])
        ]

    def circular_frequency(self):
        return Variable(pymath.sqrt((2 * self.feather.real()) / ((5. / 3.) * self.mass.real())), unit='rad/s')

    def evaluate(self, t):
        self.w_0 = self.circular_frequency().real()
        if type(t) == np.ndarray:
            return self.start_angle.real() / self.w_0 * np.sin(self.w_0 * t)
        #if t == 0:
        #    return self.start_angle
        return Variable((self.start_angle.real() / self.w_0) * np.sin(self.w_0 * t), unit='rad')

    def frequency(self):
        return Variable(self.w_0 / (2 * pymath.pi), unit='Hz')

    def duration(self):
        return Variable(1 / self.frequency().real(), unit='s')

    def get_evaluation(self):
        w_0 = self.circular_frequency()
        return f'{(self.start_angle.real() / w_0.real()):.2f} * sin({w_0.real():.2f}t)'

    def __repr__(self):
        return f'$\large Elastisch ~~ gelagerter, ~~ starrer ~~ Winkel\\\\ ' \
               f'Masse ~~ m = {self.mass.latex()}\\\\ ' \
               f'Federsteifigkeit ~~ k = {self.feather.latex()}\\\\ ' \
               f'Anfangswinkelgeschwindigkeit ~~ phi_0 = {self.start_angle.rounded_latex()}\\\\ ' \
               f'\\\\Eigenkreisfrequenz ~~ w_0 = {self.circular_frequency().rounded_latex()}\\\\ ' \
               f'Schwingungsdauer ~~ T = {self.duration().rounded_latex()}\\\\ ' \
               f'Eigenfrequenz ~~ f_0 = {self.frequency().rounded_latex()}\\\\ ' \
               f'Phi(t) = {self.get_evaluation()} ~~ [rad]$'

    def __str__(self):
        return self.__repr__()

    def observe(self, func):
        self.feather.observe(func)
        self.mass.observe(func)
        self.start_angle.observe(func)
        self.t.observe(func)


class AngleCanvas():
    def __init__(self, angle: Angle, plot: Plot, width=600, height=200, L=2):
        super().__init__()
        self.angle = angle
        self.plot = plot
        self.plot.grid()
        self.plot.add_line(self.angle.duration().real(), color='red', label='T')
        self.canvas = Canvas(width=width, height=height)
        #self.canvas2 = Canvas(width=L * 2, height=50)
        self.play_btn = ClickButton(
            description="Oscilate",
            disabled=False,
            button_style='',
            tooltip='Starts an animation of the model.',
        )
        self.play_btn.observe(self.start_oscilate)

        #self.canvas_box = widgets.VBox([self.canvas])
        self.t = 0
        self.L = L
        self.osc = None
        self.scale = width / height * 2.5
        #self.canvas.layout.width = "75%"
        #self.canvas.layout.height = "75%"
        #self.angle.observe(self.on_angle_changed)
        # self.draw(None)
        self.canvas.on_client_ready(self.do_draw)
        self.oscilating = False
        self.lock = threading.Lock()

    def on_angle_changed(self, args):
        self.start_oscilate(args)

    def oscilate(self):
        # print("Running")
        max_t = self.angle.duration().real()
        self.oscilating = True
        vals = np.linspace(0, 30, 100)
        plt.ioff()
        # print(vals)
        for t in vals:
            phi = self.angle.evaluate(t)
            with hold_canvas(self.canvas):
                # canvas.canvas.rotate(phi.real())
                self.draw(phi.real())
                self.plot.mark(t, phi.real())
            self.canvas.sleep(20)
        #print("I am outta here!")
        self.canvas.reset_transform()
        #self.plot.update_plot()
        self.draw()
        self.stop_oscilate(None)
        plt.ion()

    def pl_thr(self):
        vals = np.linspace(0, 30, 100)
        for t in vals:
            phi = self.angle.evaluate(t)
            with hold_canvas(self.canvas):
                self.plot.mark(t, phi.real())
            time.sleep(0.002)

    def do_draw(self):
        self.draw()

    def draw_time(self, t):
        self.draw(self.angle.evaluate(t).real())

    """def draw(self, args):
        self.canvas.clear()
        self.canvas.rotate(0)
        x = self.canvas.width / 4
        y = 15

        self.canvas.fill_style = hexcode((230, 230, 230))
        if args is not None and 'angle' in args:
            cx = x
            cy = self.angle.mass.real() / 2 + self.L + y - 5
            pivot = (cx, cy)

            s = np.sin(args['angle'])
            c = np.cos(args['angle'])

            px = x - cx
            py = y - cy

            # yr = self.angle.mass.real() / 2 + self.L + y - 5
            xp = px * c - py * s
            yp = px * s + py * c

            x1 = x
            y1 = self.angle.mass.real() / 2 + self.L + y - 5
            x2 = x - 5
            y2 = self.angle.mass.real() / 2 + self.L + y
            x3 = x + 5
            y3 = self.angle.mass.real() / 2 + self.L + y

            xp1, yp1 = self.rotate_point(pivot, (x1, y1), s, c)
            xp2, yp2 = self.rotate_point(pivot, (x2, y2), s, c)
            xp3, yp3 = self.rotate_point(pivot, (x3, y3), s, c)

            self.canvas.stroke_line(xp + cx, self.angle.mass.real() + yp + cy, xp1 + cx,
                                    self.angle.mass.real() / 2 + y + self.L)
            #self.canvas.stroke_line(x, y, xp, yp)self.canvas.fill_style = hexcode((230, 230, 230))
            self.canvas.fill_circle(xp + cx, yp + cy, 9)
            self.canvas.stroke_text('m', xp - 4.5 + cx, yp + 2 + cy)
            self.canvas.stroke_circle(xp + cx, yp + cy, 9)

            self.canvas.fill_style = hexcode((0, 0, 0))

            self.canvas.fill_polygon([(xp1 + cx, yp1 + cy),
                                      (xp2 + cx, yp2 + cy),
                                      (xp3 + cx, yp3 + cy),
                                      ])

            self.canvas.fill_style = hexcode((230, 230, 230))

            xr1 = x - self.L
            yr1 = self.angle.mass.real() / 2 + y + self.L
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

            self.canvas.fill_polygon([(xpr1 + cx, ypr1 + cy), (xpr2 + cx, ypr2 + cy), (xpr3 + cx, ypr3 + cy), (xpr4 + cx, ypr4 + cy)])
            self.canvas.stroke_polygon([(xpr1 + cx, ypr1 + cy), (xpr2 + cx, ypr2 + cy), (xpr3 + cx, ypr3 + cy), (xpr4 + cx, ypr4 + cy)])

            self.canvas.fill_arc(xpa1 + cx, ypa1 + cy, 2.5, pymath.pi / 2,
                                 3 * pymath.pi / 2, True)
            self.canvas.stroke_arc(xpa1 + cx, ypa1 + cy, 2.5, pymath.pi / 2,
                                   3 * pymath.pi / 2, True)
            self.canvas.fill_arc(xpa2 + cx, ypa2 + cy, 2.5, pymath.pi / 2,
                                 3 * pymath.pi / 2)
            self.canvas.stroke_arc(xpa2 + cx, ypa2 + cy, 2.5, pymath.pi / 2,
                                   3 * pymath.pi / 2)

            ezz1 = self.zigzag_stretch(xpr4 + cx, ypr4 + cy, xpr4 + cx, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=5)
            ezz2 = self.zigzag_stretch(xpr3 + cx, ypr3 + cy, xpr3 + cx, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=5)

            self.fancy_line(x - self.L - 10, x - self.L + 10, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=3)
            self.fancy_line(x + self.L - 10, x + self.L + 10, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=3)

            self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x - 5,
                                    self.angle.mass.real() / 2 + self.L + y + 15)
            self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x + 5,
                                    self.angle.mass.real() / 2 + self.L + y + 15)
            self.canvas.fill_style = hexcode((255, 255, 255))
            self.canvas.fill_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)
            self.canvas.stroke_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)

            self.fancy_line(x - 10, x + 10, self.angle.mass.real() / 2 + y + self.L + 15, x_offset=3)

            #self.canvas.rotate(args['angle'])
        else:
            self.canvas.stroke_line(x, self.angle.mass.real() + y, x,
                                        self.angle.mass.real() / 2 + y + self.L)
            self.canvas.fill_circle(x, y, 9)
            self.canvas.stroke_text('m', x - 4.5, y + 2)
            self.canvas.stroke_circle(x, y, 9)

            self.canvas.fill_style = hexcode((0, 0, 0))


            self.canvas.reset_transform()

            self.canvas.fill_polygon([(x, self.angle.mass.real() / 2 + self.L + y - 5),
                                      (x - 5, self.angle.mass.real() / 2 + self.L + y),
                                      (x + 5, self.angle.mass.real() / 2 + self.L + y),
                                      ])

            self.canvas.fill_style = hexcode((230, 230, 230))

            self.canvas.fill_rect(x - self.L, self.angle.mass.real() / 2 + y + self.L, self.L * 2, 5)
            self.canvas.stroke_rect(x - self.L, self.angle.mass.real() / 2 + y + self.L, self.L * 2, 5)

            ezz1 = self.zigzag_stretch(x - self.L, self.angle.mass.real() / 2 + y + self.L + 5, x - self.L, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=5)
            ezz2 = self.zigzag_stretch(x + self.L, self.angle.mass.real() / 2 + y + self.L + 5, x + self.L, self.angle.mass.real() / 2 + y + self.L + 5 + 20, x_offset=5)

            self.fancy_line(ezz1[0] - 10, ezz1[0] + 10, ezz1[1], x_offset=3)
            self.fancy_line(ezz2[0] - 10, ezz2[0] + 10, ezz2[1], x_offset=3)

            self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x - 5,
                                    self.angle.mass.real() / 2 + self.L + y + 15)
            self.canvas.stroke_line(x, self.angle.mass.real() / 2 + self.L + y + 5, x + 5,
                                    self.angle.mass.real() / 2 + self.L + y + 15)
            self.canvas.fill_style = hexcode((255, 255, 255))
            self.canvas.fill_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)
            self.canvas.stroke_arc(x, self.angle.mass.real() / 2 + y + self.L + 5, 5, 0, pymath.pi)

            self.canvas.fill_arc(x + self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2,
                                 3 * pymath.pi / 2, True)
            self.canvas.stroke_arc(x + self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2,
                                   3 * pymath.pi / 2, True)
            self.canvas.fill_arc(x - self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2,
                                 3 * pymath.pi / 2)
            self.canvas.stroke_arc(x - self.L, self.angle.mass.real() / 2 + y + self.L + 2.5, 2.5, pymath.pi / 2,
                                   3 * pymath.pi / 2)

            self.fancy_line(x - 10, x + 10, self.angle.mass.real() / 2 + y + self.L + 15, x_offset=3)

        # self.canvas.scale(10, 10)"""

    def draw(self, angle=0):
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

        # yr = self.angle.mass.value / 2 + self.L + y - 5
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

        self.canvas.stroke_line(xp + cx, self.angle.mass.value + yp + cy, xp1 + cx,
                                self.angle.mass.value / 2 + y + self.L)
        # self.canvas.stroke_line(x, y, xp, yp)self.canvas.fill_style = hexcode((230, 230, 230))
        self.canvas.fill_circle(xp + cx, yp + cy, 9)
        self.canvas.stroke_text('m', xp - 4.5 + cx, yp + 2 + cy)
        self.canvas.stroke_circle(xp + cx, yp + cy, 9)

        self.canvas.fill_style = hexcode((0, 0, 0))

        self.canvas.fill_polygon([(xp1 + cx, yp1 + cy),
                                  (xp2 + cx, yp2 + cy),
                                  (xp3 + cx, yp3 + cy),
                                  ])

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
                                   x_offset=5)
        ezz2 = self.zigzag_stretch(xpr3 + cx, ypr3 + cy, xpr3 + cx, self.angle.mass.value / 2 + y + self.L + 5 + 20,
                                   x_offset=5)

        self.fancy_line(x - self.L - 10, x - self.L + 10, self.angle.mass.value / 2 + y + self.L + 5 + 20, x_offset=3)
        self.fancy_line(x + self.L - 10, x + self.L + 10, self.angle.mass.value / 2 + y + self.L + 5 + 20, x_offset=3)


    def rotate_point(self, pivot, point, s, c):
        cx, cy = pivot
        x, y = point
        px = x - cx
        py = y - cy
        xp = px * c - py * s
        yp = px * s + py * c
        return xp, yp

    def zigzag(self, x, y, steps=7, x_offset=10, y_offset=5, y1=None):
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

    def zigzag_stretch(self, x0, y0, x1, y1, steps=7, x_offset=10):
        y_offset = abs(y1 - y0) / (steps + 2)
        ezz = self.zigzag(x0, y0, steps=steps, y_offset=y_offset, x_offset=x_offset)
        if ezz[1] < y1:
            self.canvas.stroke_line(x0, ezz[1], x0, y1)
        return x0, y1

    def fancy_line(self, x_0, x_1, y, x_offset=2.5, y_offset=5):
        self.canvas.stroke_line(x_0, y, x_1, y)
        x = x_0
        while x < x_1 - x_offset:
            self.canvas.stroke_line(x, y + y_offset, x + x_offset, y)
            x += x_offset

    def start_oscilate(self, btn):
        #print("Start oscilate")
        if self.osc is None:
            self.osc = threading.Thread(target=self.oscilate)
            #self.pl = threading.Thread(target=self.pl_thr)
            self.osc.start()
            #self.pl.start()
            self.play_btn.disabled = True

    def stop_oscilate(self, btn):
        #print("STOP!")
        if self.osc is not None:
            self.oscilating = False
            self.play_btn.disabled = False
            self.osc = None
            self.pl = None


def setup_angle(m, k, w):
    return Angle(m, k, w)


if __name__ == '__main__':
    angle = setup_angle(9, 3, 0.2)
    print(angle.circular_frequency(), Variable(2 * pymath.pi / angle.duration().real(), "s^-1"))
    #for i in range(0, 30):
    #   print(angle.evaluate(i))
