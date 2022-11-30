from demo import *


class Addition(Model):
    # Ein Modell, welches zwei Zahlen addiert

    def __init__(self, canvas=None):
        self.a = IntChangeable(
            0,  # Startwert
            0,  # Exponent der Einheit
            "m",  # Einheit
            0,  # Minimalwert
            10,  # Maximalwert
            "a",  # Beschreibung,
            step=1  # Schrittweite
        )
        self.b = IntChangeable(0, 0, "m", 0, 10, "b", step=1)

        # Dieser Schritt ist sehr wichtig, um die Eingaben später an die Simulation zu übergeben
        self.params = [ChangeableContainer([self.a, self.b])]
        #self.params = [ChangeableContainer([self.a]), ChangeableContainer([self.b])]
        self.canvas = canvas

    def update(self, change):
        # update Methode der Superklasse aufrufen, damit die Grundfunktionalität nicht verloren geht
        super().update(change)
        # Zeichnungen aktualisieren
        self.draw()

    def calculate(self):
        return f"{self.a} + {self.b} = {self.a + self.b}"

    def draw(self):
        # Es soll nur gezeichnet werden, wenn es etwas zum bezeichnen gibt
        if self.canvas is None:
            return
        # Zeichenfläche leeren
        self.canvas.clear()

        # Die stroke_rect(x, y, sx, sy) Methode zeichnet ein leeres Rechteck mit der linken oberen Ecke an (x, y) und der Größe (sx, sy)
        self.canvas.stroke_rect(10, 10, 200, 50)
        self.canvas.stroke_rect(10, 80, 200, 50)
        self.canvas.stroke_rect(10, 150, 400, 50)

        # Die fill_text(text, x, y) Methode zeichnet den Text text an die Position (x, y)
        self.canvas.fill_text("a: ", 5, 5)
        self.canvas.fill_text("b: ", 5, 75)
        self.canvas.fill_text("Sum: ", 5, 145)

        # Die fill_rect(x, y, sx, sy) Methode zeichnet ein gefülltes Rechteck mit der linken oberen Ecke an (x, y) und der Größe
        # Das fill_style Attribut setzt die Füllfarbe und kann als hexcode oder als Farbname angegeben werden
        self.canvas.fill_style = "red"
        self.canvas.fill_rect(10, 10, self.a.real() * 20, 50)

        self.canvas.fill_style = "green"
        self.canvas.fill_rect(10, 80, self.b.real() * 20, 50)

        self.canvas.fill_style = "blue"
        self.canvas.fill_rect(10, 150, (self.a + self.b).real() * 20, 50)
        self.canvas.fill_style = "black"
