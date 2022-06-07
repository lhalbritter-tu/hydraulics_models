import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
from PyQt5.Qt import QGraphicsScene, QRectF, QLineF, QGraphicsEllipseItem, QPen
from model import Model, SimplePipe, IntersectionForm, Circle, Rect, AdvancedPipe
import view


class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.pen = QPen(QtCore.Qt.darkBlue)
        self.ui.graphicsDisplay.setScene(self.scene)
        self.ui.d2Slider.setValue(30)

        #i1 = Circle(self.ui.d1Slider.value())
        #i2 = Rect(self.ui.d1Slider.value(), self.ui.d2Slider.value())
        self.model = SimplePipe(self.ui.d1Slider.value(), self.ui.d2Slider.value(), self.ui.u1Slider.value())
        #self.model = AdvancedPipe(i1, i2, self.ui.u1Slider.value())
        self.ui.d1Slider.valueChanged.connect(self.onSliderChanged)
        self.ui.d2Slider.valueChanged.connect(self.onSliderChanged)
        self.ui.u1Slider.valueChanged.connect(self.onSliderChanged)
        self.update()

    def onSliderChanged(self):
        self.model.i1.d = self.ui.d1Slider.value()
        self.model.i2.w = self.ui.d1Slider.value()
        self.model.i2.h = self.ui.d2Slider.value()
        self.model.u1 = self.ui.u1Slider.value()
        self.update()

    def update(self):
        self.ui.textDisplay.setHtml("<h1>Simple Pipe</h1><p>" + self.model.calculate() + "</p>")
        self.draw()

    def draw(self):
        self.scene.clear()
        margin = 250
        c1 = self.model.i1.draw(0, 25 + self.ui.d2Slider.value() / 2)
        c2 = self.model.i2.draw(margin, 25 + self.ui.d1Slider.value() / 2)

        l1c1 = QLineF(self.ui.d1Slider.value() / 2, 25 + self.ui.d2Slider.value() / 2,
                      margin / 4 + self.ui.d1Slider.value(), 25 + self.ui.d2Slider.value() / 2)
        l2c1 = QLineF(self.ui.d1Slider.value() / 2, 25 + self.ui.d1Slider.value() + self.ui.d2Slider.value() / 2,
                      margin / 4 + self.ui.d1Slider.value(),
                      25 + self.ui.d1Slider.value() + self.ui.d2Slider.value() / 2)

        l1c1c2 = QLineF(l1c1.x2(), l1c1.y2(), l1c1.x2() + margin / 4, 25 + self.ui.d1Slider.value() / 2)
        l2c1c2 = QLineF(l2c1.x2(), l2c1.y2(), l2c1.x2() + margin / 4,
                        25 + self.ui.d2Slider.value() + self.ui.d1Slider.value() / 2)

        l1c2 = QLineF(l1c1c2.x2(), l1c1c2.y2(), margin + self.ui.d2Slider.value() / 2, l1c1c2.y2())
        l2c2 = QLineF(l2c1c2.x2(), l2c1c2.y2(), margin + self.ui.d2Slider.value() / 2, l2c1c2.y2())

        self.scene.addItem(c1)
        self.scene.addItem(c2)
        self.scene.addLine(l1c1)
        self.scene.addLine(l2c1)
        self.scene.addLine(l1c1c2)
        self.scene.addLine(l2c1c2)
        self.scene.addLine(l2c2)
        self.scene.addLine(l1c2)
        pass

    def get_arrow(self, x1, x2, y1, y2):
        if x1 == x2:
            return self.vert_arrow(x1, y1, y2)
        if y1 == y2:
            return self.hor_arrow(x1, x2, y1)
        return None

    def vert_arrow(self, x, y1, y2):
        l1 = QLineF(x, y1, x, y2)
        l2 = QLineF(x, y1, x + 25, y1 + 25)
        l3 = QLineF(x, y1, x - 25, y1 + 25)
        return [l1, l2, l3]

    def hor_arrow(self, x1, x2, y):
        l1 = QLineF(x1, y, x2, y)
        l2 = QLineF(x2, y, x2 - 25, y + 25)
        l3 = QLineF(x2, y, x2 - 25, y - 25)
        return [l1, l2, l3]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = App()
    c.show()
    sys.exit(app.exec_())
