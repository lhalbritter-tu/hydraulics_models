import math
from demo import *

class Angle:
    def __init__(self, mass: Variable, feather: Variable, start_angle: Variable):
        self.mass = mass
        self.feather = feather
        self.start_angle = start_angle

    def circular_frequency(self):
        return Variable(math.sqrt((2 * self.feather.real()) / ((5 / 3) * self.mass.real())), unit='rad/s')

    def evaluate(self, t):
        if t == 0:
            return self.start_angle
        w_0 = self.circular_frequency().real()
        return Variable((self.start_angle.real() / w_0) * math.sin(w_0 * t), unit='rad')

    def frequency(self):
        return Variable(self.circular_frequency().real() / (2 * math.pi), unit='Hz')

    def duration(self):
        return Variable(1 / self.frequency().real(), unit='s')

    def get_evaluation(self):
        w_0 = self.circular_frequency().real()
        return f'{self.start_angle.real() / w_0} * sin({w_0}t)'

    def __repr__(self):
        return f'Elastisch gelagerter, starrer Winkel\nMasse m = {self.mass}\nFedersteifigkeit k = {self.feather}\nAnfangswinkelgeschwindigkeit phi_0 = {self.start_angle}' \
               f'\n\nEigenkreisfrequenz w_0 = {self.circular_frequency()}\nSchwingungsdauer T = {self.duration()}\nEigenfrequenz f_0 = {self.frequency()}\nPhi(t) = {self.get_evaluation()}'

    def __str__(self):
        return self.__repr__()


def setup_angle(m, k, w):
    return Angle(Variable(m, unit='kg'), Variable(k, base=3, unit='kN/m'), Variable(w, unit='rad'))


if __name__ == '__main__':
    angle = setup_angle(9, 3, 0.2)
    print(angle)
