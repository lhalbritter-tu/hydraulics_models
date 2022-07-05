import math as pymath
from demo import *


class Angle(Model):
    def calculate(self):
        return str(self)

    def lines(self):
        pass

    def __init__(self, mass, feather, start_angle):
        self.mass = FloatChangeable(mass, unit="kg", _min=1.0, desc="Mass m = ")
        self.feather = FloatChangeable(feather, unit="kN/m", base=3, _min=1.0, desc="Feather stiffness k = ")
        self.start_angle = FloatChangeable(start_angle, unit="rad", _min=0.1, desc="Initial angular velocity Phi(0) = ")

        self.params = [
            ChangeableContainer([self.mass, self.feather, self.start_angle])
        ]

    def circular_frequency(self):
        return Variable(pymath.sqrt((2 * self.feather.real()) / ((5 / 3) * self.mass.real())), unit='rad/s')

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


def setup_angle(m, k, w):
    return Angle(Variable(m, unit='kg'), Variable(k, base=3, unit='kN/m'), Variable(w, unit='rad'))


if __name__ == '__main__':
    angle = setup_angle(9, 3, 0.2)
    print(angle)
