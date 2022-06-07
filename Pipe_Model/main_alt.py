import sys

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
from PyQt5.Qt import QGraphicsScene, QRectF, QLineF, QGraphicsEllipseItem, QPen, QBrush, QLinearGradient, QColor, \
    QPolygonF, QGradient, QRadialGradient
from model import Model, SimplePipe, IntersectionForm, Circle, Rect, AdvancedPipe
import view_alt as view


class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.pen = QPen(QtCore.Qt.black)
        self.pen.setCapStyle(QtCore.Qt.RoundCap)
        self.pen.setWidthF(0.5)
        self.pen.setJoinStyle(QtCore.Qt.RoundJoin)
        self.ui.graphicsDisplay.setScene(self.scene)
        self.pipeGradient = QLinearGradient()
        self.pipeGradient.setSpread(QGradient.PadSpread)
        self.pipeGradient.setColorAt(0, QColor(222, 202, 215))
        self.pipeGradient.setColorAt(0.5, QtCore.Qt.white)
        self.pipeGradient.setColorAt(1, QColor(158, 144, 153))
        self.pipeBrush = QBrush(self.pipeGradient)

        self.i2Brush = QBrush(QColor(158, 144, 153))
        self.i1Brush = QBrush(QColor(222, 202, 215))
        # self.ui.d2Slider.setValue(30)

        self.selectedi1 = "CIRC"
        self.selectedi2 = "CIRC"

        self.i1Circ = Circle(self.ui.i1dSlider.value(), -self.ui.i1ySlider.value())
        self.i2Circ = Circle(self.ui.i2dSlider.value(), -self.ui.i2ySlider.value())

        self.i1Rect = Rect(self.ui.i1wSlider.value(), self.ui.i1hSlider.value(), -self.ui.i1ySlider.value())
        self.i2Rect = Rect(self.ui.i2wSlider.value(), self.ui.i2hSlider.value(), -self.ui.i2ySlider.value())

        # i1 = Circle(self.ui.d1Slider.value())
        # i2 = Rect(self.ui.d1Slider.value(), self.ui.d2Slider.value())
        self.model = AdvancedPipe(self.i1Circ, self.i2Circ, self.ui.u1Slider.value())

        self.ui.i1dSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i1wSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i1hSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i1ySlider.valueChanged.connect(self.onSliderChanged)

        self.ui.i2dSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i2wSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i2hSlider.valueChanged.connect(self.onSliderChanged)
        self.ui.i2ySlider.valueChanged.connect(self.onSliderChanged)

        self.ui.u1Slider.valueChanged.connect(self.onSliderChanged)

        self.ui.i1wSlider.setVisible(False)
        self.ui.i1wLabel.setVisible(False)
        self.ui.i1wSpinner.setVisible(False)
        self.ui.i1hSlider.setVisible(False)
        self.ui.i1hLabel.setVisible(False)
        self.ui.i1hSpinner.setVisible(False)
        self.ui.i2wSlider.setVisible(False)
        self.ui.i2wLabel.setVisible(False)
        self.ui.i2wSpinner.setVisible(False)
        self.ui.i2hSlider.setVisible(False)
        self.ui.i2hLabel.setVisible(False)
        self.ui.i2hSpinner.setVisible(False)
        self.ui.intersection1Group.buttonClicked.connect(self.onI1Changed)
        self.ui.intersection2Group.buttonClicked.connect(self.onI2Changed)

        self.update()

    def onI1Changed(self, arg):
        self.selectedi1 = "CIRC" if self.ui.circle.isChecked() else "RECT"
        self.model.i1 = self.i1Circ if self.selectedi1 == "CIRC" else self.i1Rect
        self.model.i1.y = -self.ui.i1ySlider.value()
        self.update()

    def onI2Changed(self, arg):
        self.selectedi2 = "CIRC" if self.ui.circle_2.isChecked() else "RECT"
        self.model.i2 = self.i2Circ if self.selectedi2 == "CIRC" else self.i2Rect
        self.model.i2.y = -self.ui.i2ySlider.value()
        self.update()

    def onSliderChanged(self):
        if self.selectedi1 == "CIRC":
            self.model.i1.d = self.ui.i1dSlider.value()
        else:
            self.model.i1.w = self.ui.i1wSlider.value()
            self.model.i1.h = self.ui.i1hSlider.value()
        self.model.i1.y = -self.ui.i1ySlider.value()

        if self.selectedi2 == "CIRC":
            self.model.i2.d = self.ui.i2dSlider.value()
        else:
            self.model.i2.w = self.ui.i2wSlider.value()
            self.model.i2.h = self.ui.i2hSlider.value()
        self.model.i2.y = -self.ui.i2ySlider.value()

        self.model.u1 = self.ui.u1Slider.value()

        self.update()

    def update(self):
        print(self.model.calculate())
        self.draw()

    def draw(self):
        self.scene.clear()
        margin = 450
        c1 = self.model.i1.draw(50)
        c2 = self.model.i2.draw(margin)

        l1 = self.get_lines(self.selectedi1, self.model.i1, margin)
        l2 = self.get_lines(self.selectedi2, self.model.i2, margin, True)

        l1c1 = l1[0]
        l1c2 = QLineF(l2[0].x2(), l2[0].y2(), l2[0].x1(), l2[0].y1())
        l2c1 = l1[1]
        l2c1r = QLineF(l2c1.x2(), l2c1.y2(), l2c1.x1(), l2c1.y1())
        l2c2 = l2[1]

        l1c1c2 = QLineF(l1c1.x2(), l1c1.y2(), l1c2.x1(), l1c2.y1())
        l2c1c2 = QLineF(l2c2.x2(), l2c2.y2(), l2c1.x2(), l2c1.y1())

        line_polygons = self.lines_to_polygons([l1c1, l1c1c2, l1c2, l2c2, l2c1c2, l2c1r])

        hi1 = self.model.i1.y + (self.model.i1.r / 2 if self.selectedi1 == "CIRC" else self.model.i1.h / 2)
        halfLine1 = QLineF(0.0, hi1, self.size().width(), hi1)
        hi2 = self.model.i2.y + (self.model.i2.r / 2 if self.selectedi2 == "CIRC" else self.model.i2.h / 2)
        halfLine2 = QLineF(0.0, hi2, self.size().width(), hi2)

        self.pen.setStyle(QtCore.Qt.SolidLine)
        #self.pen.setBrush(self.pipeBrush)
        #print("Found polygons: " + str(len(line_polygons)))
        for line_polygon in line_polygons:
            rect = line_polygon.boundingRect()
            self.pipeBrush.gradient().setStart(rect.topLeft())
            self.pipeBrush.gradient().setFinalStop(rect.bottomRight())
            #print("Drawing Polygon: " + str(line_polygon))
            self.scene.addPolygon(line_polygon, self.pen, self.pipeBrush)
        #self.pen.setBrush(QtCore.Qt.white)
        if self.selectedi1 == "CIRC":
            self.scene.addEllipse(c1, self.pen, self.i1Brush)
        else:
            self.scene.addItem(c1)
        if self.selectedi2 == "CIRC":
            self.scene.addEllipse(c2, self.pen, self.i2Brush)
        else:
            self.scene.addItem(c2)
        # self.scene.addLine(l1c1)
        # self.scene.addLine(l2c1)
        # self.scene.addLine(l1c1c2)
        # self.scene.addLine(l2c1c2)
        # self.scene.addLine(l2c2)
        # self.scene.addLine(l1c2)

        self.pen.setStyle(QtCore.Qt.DashLine)
        self.scene.addLine(halfLine1, self.pen)
        self.scene.addLine(halfLine2, self.pen)

        if hi1 != hi2:
            self.scene.addLine(QLineF(margin + 155, hi1, margin + 155, hi2))
            hText = self.scene.addText("Delta H")
            hText.setPos(margin + 160, (hi1 + hi2) / 2)

        h = max(hi1, hi2)
        self.scene.addLine(QLineF(0.0, h + 50, self.size().width(), h + 50))
        legend = self.scene.addText("End 1 is a " + self.model.i1.type + ": \n" + str(self.model.i1))
        legend.setPos(l1c1.x1(), h + 55)
        legend = self.scene.addText("End 2 is a " + self.model.i2.type + ": \n" + str(self.model.i2))
        legend.setPos(l1c2.x1(), h + 55)
        legend = self.scene.addText(self.model.calculate())
        legend.setPos(l1c1.x1(), h + 100)

    def get_lines(self, selected, i, margin=0, end=False):
        px1 = py = px2 = 0
        if selected == "CIRC":
            py = i.r + i.y
            px1 = i.r / 8 + i.x  # (margin if end else 0)
            if end:
                px2 = margin - i.r / 4
            else:
                px2 = margin / 4 + i.r / 4
        else:
            py = i.h + i.y
            px1 = i.w / 2 + (margin if end else 0)
            if end:
                px2 = margin - i.w
            else:
                px2 = margin / 4 + i.w

        return [QLineF(px1, py, px2, py),
                QLineF(px1, py - (i.r if selected == "CIRC" else i.h), px2, py - (i.r if selected == "CIRC" else i.h))]

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

    def lines_to_polygons(self, lines):
        if len(lines) < 6:
            polygons = []
            for i in range(0, len(lines), 2):
                polygons.append(self.make_rect(lines[i], lines[i + 1]))

            return polygons
        polygon = QPolygonF()
        for line in lines:
            self.add_points(polygon, line)
        self.add_point(polygon, lines[0].x1(), lines[0].y1())
        return [polygon]


    def add_point(self, polygon, x, y):
        polygon.append(QPointF(x, y))

    def add_points(self, polygon, line):
        print("Connecting (" + str(line.x1()) + ", " + str(line.y1()) + ") with (" + str(line.x2()) + ", " + str(line.y2()) + ")")
        polygon.append(QPointF(line.x1(), line.y1()))
        polygon.append(QPointF(line.x2(), line.y2()))

    def make_rect(self, l1, l2):
        polygon = QPolygonF()
        polygon.append(QPointF(l1.x1(), l1.y1()))
        polygon.append(QPointF(l1.x2(), l1.y2()))
        polygon.append(QPointF(l2.x2(), l2.y2()))
        polygon.append(QPointF(l2.x1(), l2.y1()))
        polygon.append(QPointF(l1.x1(), l1.y1()))
        return polygon


if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = App()
    c.show()
    sys.exit(app.exec_())
    # import mesh
    # mesh.Cylinder(16, 1.5, 1)
