from demo import *


class Addition(Model):
    # Ein Modell, welches zwei Zahlen addiert

    def __init__(self):
        self.a = IntChangeable(
            0,  # Startwert
            0,  # Exponent der Einheit
            "m",  # Einheit
            0,  # Minimalwert
            10,  # Maximalwert
            "Erste Zahl",  # Beschreibung,
            step=1  # Schrittweite
        )
        self.b = IntChangeable(0, 0, "m", 0, 10, "Zweite Zahl", step=1)

        # Dieser Schritt ist sehr wichtig, um die Eingaben später an die Simulation zu übergeben
        self.params = [ChangeableContainer([self.a, self.b])]
        #self.params = [ChangeableContainer([self.a]), ChangeableContainer([self.b])]

    def calculate(self):
        return f"{self.a} + {self.b} = {self.a + self.b}"
