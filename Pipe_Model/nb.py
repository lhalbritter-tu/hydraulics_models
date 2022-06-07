import math

import model
import ipywidgets as widgets
from ipycanvas import canvas
from IPython.display import display, Markdown, Latex
    
def task1():
    display(Markdown("## Task 1\nLook at the following sketch and enter the correct value for U2\n![sketch1](au01.png)"))
    
    confirm = widgets.Button(description = "Confirm")
    inp = widgets.FloatText(
        value=7.5,
        description='Solution:',
        disabled=False)
    display(widgets.HBox([inp, confirm]))
    
    t = Task(model.SimplePipe(29, 39, 35))
    res = widgets.Label("Enter your solution and confirm it with the button to see if you got the correct answer.")
    def confirmed(arg):
        if t.compare(inp.value):
            res.value = "You did it!"
        else:
            res.value = "That is not the correct answer. Try again!"
    confirm.on_click(confirmed)
    display(res)    
    

class Task():
    def __init__(self, model):
        self.model = model
    
    def compare(self, value):
        return str(value) in self.model.calculate()

class Demo():
    def __init__(self, canvas: canvas.Canvas):
        self.canvas = canvas
    
    def show(self):
        pass

class SimpleDemo(Demo):
    def __init__(self, canvas = None):
        super().__init__(canvas)
    
    def show(self):
        d1Slider = widgets.IntSlider(
        min = 10,
        max = 150,
        step = 1,
        description = "D1",
        value = 10
        )
        display(d1Slider)

        d2Slider = widgets.IntSlider(
            min = 10,
            max = 150,
            step = 1,
            description = "D2",
            value = 10
        )
        display(d2Slider)

        u1Slider = widgets.IntSlider(
            min = 1,
            max = 150,
            step = 1,
            description = "U1",
            value = 5
        )
        display(u1Slider)
        display(Markdown("### Output"))
        pipe = model.SimplePipe(d1Slider.value, d2Slider.value, u1Slider.value)
        l = widgets.HTMLMath(
            value=f"$$U_2 = \\frac{{{pipe.d1 ** 2}}}{{{pipe.d2 ** 2}}} \cdot {pipe.u1} = {pipe.u2()}$$"
        )
        display(l)

        def output(change):
            pipe.d1 = d1Slider.value
            pipe.d2 = d2Slider.value
            pipe.u1 = u1Slider.value
            l.value = f'$U2 = \\frac{{{pipe.d1 ** 2}}}{{{pipe.d2 ** 2}}} \cdot {pipe.u1} = {pipe.u2()}$'
            redraw()

        d1Slider.observe(output)
        d2Slider.observe(output)
        u1Slider.observe(output)

        display(Markdown("### Sketch"))

        from ipycanvas import Canvas

        def draw_circle(c, circ, x):
            circ.y = 20 + circ.d
            c.stroke_circle(x + circ.d, circ.y, circ.d)

        def draw_lines(c, circ, x = 0, end = False):
            circ.x = x
            lines = model.get_lines("CIRC", circ, x, end)
            for line in lines:
                c.stroke_line(line[0], line[1], line[2], line[3])
            return lines

        c1 = model.Circle(pipe.d1, 20 + pipe.d1)
        c2 = model.Circle(pipe.d2, 20 + pipe.d2)

        def redraw():
            c1.d = pipe.d1
            c2.d = pipe.d2
            self.canvas.clear()
            draw_circle(self.canvas, c1, 25)
            draw_circle(self.canvas, c2, 400)
            lc1 = draw_lines(self.canvas, c1, 25)
            lc2 = draw_lines(self.canvas, c2, 400, True)
            self.canvas.stroke_line(lc1[0][2], lc1[0][1], lc2[0][2] + 1, lc2[0][1])
            self.canvas.stroke_line(lc1[1][2], lc1[1][1], lc2[1][2] + 1, lc2[1][1])

        redraw()

class AdvancedDemo(Demo):
    def __init__(self, canvas = None, margin_y = 100):
        super().__init__(canvas)
        self.model = model.AdvancedPipe(None, None, 10)
        self.margin_y = margin_y
        self.initialize()

    def initialize(self):
        self.endCirc1 = model.Circle(1, 25 + self.margin_y)
        self.endCirc2 = model.Circle(1, 25 + self.margin_y)
        self.endRect1 = model.Rect(1, 1, 25 + self.margin_y)
        self.endRect2 = model.Rect(1, 1, 25 + self.margin_y)
        self.initialize_ui()

    def initialize_ui(self):
        self.end1Label = widgets.HTML("<h1>End 1</h1>")
        self.end2Label = widgets.HTML("<h1>End 2</h1>")
        self.end1ChoiceGroup = widgets.ToggleButtons(
            options=['Circle', 'Rectangle'],
            tooltips=['Choose a circular end', 'Choose a rectangular end']
        )
        self.end2ChoiceGroup = widgets.ToggleButtons(
            options=['Circle', 'Rectangle'],
            tooltips=['Choose a circular end', 'Choose a rectangular end']
        )
        self.end1ChoiceGroup.observe(self.choose_node)
        self.end2ChoiceGroup.observe(self.choose_node)
        self.output = widgets.Output()
        self.end1SliderOutput = widgets.Output()
        self.end2SliderOutput = widgets.Output()
        self.end1CircleSlider = widgets.FloatSlider(value=1.0,
                                min=1.0,
                                max=10.0,
                                step=0.1,
                                description='Diameter: ',
                                disabled=False,
                                continuous_update=False,
                                orientation='horizontal')
        self.end1CircleSlider.observe(self.update_values)

        self.end2CircleSlider = widgets.FloatSlider(value=1.0,
                                min=1.0,
                                max=10.0,
                                step=0.1,
                                description='Diameter: ',
                                disabled=False,
                                continuous_update=False,
                                orientation='horizontal')
        self.end2CircleSlider.observe(self.update_values)

        self.end1RectSliders = [
            widgets.FloatSlider(value = 1.0,
                                min = 1.0,
                                max = 10.0,
                                step = 0.1,
                                description = 'Width: ',
                                orientation = 'horizontal'),
            widgets.FloatSlider(value = 1.0,
                                min = 1.0,
                                max = 10.0,
                                step = 0.1,
                                description = 'Height: ',
                                orientation = 'horizontal')
        ]
        for slider in self.end1RectSliders:
            slider.observe(self.update_values)

        self.end2RectSliders = [
            widgets.FloatSlider(value=1.0,
                                min=1.0,
                                max=10.0,
                                step=0.1,
                                description='Width: ',
                                orientation='horizontal'),
            widgets.FloatSlider(value=1.0,
                                min=1.0,
                                max=10.0,
                                step=0.1,
                                description='Height: ',
                                orientation='horizontal')
        ]
        for slider in self.end2RectSliders:
            slider.observe(self.update_values)

        self.end1YSlider = widgets.FloatSlider(value = 0.0,
                                              min = -25.0,
                                              max = 25.0,
                                              step = 0.1,
                                              description = 'Y: ',
                                              orientation = 'horizontal')
        self.end1YSlider.observe(self.update_values)

        self.end2YSlider = widgets.FloatSlider(value=0.0,
                                               min=-25.0,
                                               max=25.0,
                                               step=0.1,
                                               description='Y: ',
                                               orientation='horizontal')
        self.end2YSlider.observe(self.update_values)

        self.u1Slider = widgets.FloatSlider(value = 10.0,
                                            min = 10.0,
                                            max = 30.0,
                                            step = 0.1,
                                            description = "U1: ",
                                            orientation = 'horizontal')
        self.u1Slider.observe(self.update_values)

    def show(self):
        self.end1 = widgets.VBox([self.end1Label, self.end1ChoiceGroup, self.end1SliderOutput])
        self.end2 = widgets.VBox([self.end2Label, self.end2ChoiceGroup, self.end2SliderOutput])
        display(widgets.HBox([self.end1, self.end2]))
        display(self.u1Slider)
        display(widgets.VBox([self.canvas, self.output]))

        self.choose_node(None)
        pass

    def update_values(self, change):
        self.set_values(self.model.i1, 1)
        self.set_values(self.model.i2, 2)
        self.model.u1 = self.u1Slider.value
        self.recalculate()
        pass

    def set_values(self, i, ind):
        if ind == 1:
            endCircleSlider = self.end1CircleSlider
            endRectSliders = self.end1RectSliders
            endYSlider = self.end1YSlider
        else:
            endCircleSlider = self.end2CircleSlider
            endRectSliders = self.end2RectSliders
            endYSlider = self.end2YSlider
        if i.type == "Circle":
            i.d = endCircleSlider.value
        else:
            i.w = endRectSliders[0].value
            i.h = endRectSliders[1].value
        i.y = endYSlider.max - endYSlider.value + self.margin_y

    def choose_node(self, change):
        self.model.i1 = self.endCirc1 if self.end1ChoiceGroup.value == "Circle" else self.endRect1
        self.model.i2 = self.endCirc2 if self.end2ChoiceGroup.value == "Circle" else self.endRect2
        self.end1SliderOutput.clear_output()
        self.end2SliderOutput.clear_output()

        with self.end1SliderOutput:
            display(self.get_output_box(self.model.i1, 1))
            pass

        with self.end2SliderOutput:
            display(self.get_output_box(self.model.i2, 2))
            pass

        self.recalculate()
        pass

    def get_output_box(self, i, ind):
        if ind == 1:
            endCircleSlider = self.end1CircleSlider
            endRectSliders = self.end1RectSliders
            endYSlider = self.end1YSlider
        else:
            endCircleSlider = self.end2CircleSlider
            endRectSliders = self.end2RectSliders
            endYSlider = self.end2YSlider
        v_box = None
        if i.type == "Circle":
            v_box = widgets.VBox([endCircleSlider, endYSlider])
        else:
            v_box = widgets.VBox(endRectSliders + [endYSlider])
        return v_box

    def recalculate(self):
        self.output.clear_output()
        with self.output:
            display(Latex(self.model.get_latex()))
        self.draw()
        pass

    def draw(self):
        argsi1 = self.model.i1.display(50)
        argsi2 = self.model.i2.display(450)
        self.canvas.clear()
        self.canvas.stroke_line(0, 0, self.canvas.width, 0)
        self.canvas.stroke_line(0, self.canvas.height - 1, self.canvas.width, self.canvas.height - 1)
        self.canvas.filter = "drop-shadow(-9px 9px 3px #ccc)"
        self.canvas.fill_style = hex((200, 182, 195))

        connectors = self.model.lines()
        self.canvas.begin_path()
        self.canvas.move_to(connectors[0][0], connectors[0][1])
        for connector in connectors:
            self.canvas.line_to(connector[0], connector[1])
            self.canvas.line_to(connector[2], connector[3])

        gradient = self.canvas.create_linear_gradient(
            connectors[0][0],
            connectors[0][1],  # Start position (x0, y0)
            connectors[2][2],
            connectors[2][3],  # End position (x1, y1)
            # List of color stops
            [
                (0, hex((222, 202, 215))),
                (0.5, "white"),
                (1, hex((158, 144, 153))),
            ],
        )

        self.canvas.fill_style = gradient
        self.canvas.fill()

        for connector in connectors:
            self.canvas.stroke_line(*connector)

        self.canvas.filter = "none"

        if self.model.i1.type == "Circle":
            self.draw_ellipse(argsi1[0], argsi1[1], argsi1[2] / 2, argsi1[2], hex((222, 202, 215)))
            #self.canvas.fill_circle(*argsi1)
        else:
            self.canvas.stroke_rect(*argsi1)
            self.canvas.fill_rect(*argsi1)
        if self.model.i2.type == "Circle":
            self.draw_ellipse(argsi2[0], argsi2[1], argsi2[2] / 2, argsi2[2], hex((158, 144, 153)))
        else:
            self.canvas.stroke_rect(*argsi2)
            self.canvas.fill_rect(*argsi2)
        self.draw_details()
        pass

    def draw_ellipse(self, x, y, rx, ry, fill_col = "white", rot = 0):
        self.canvas.begin_path()
        self.canvas.ellipse(x, y, rx, ry, rot, 0, 2 * math.pi)
        self.canvas.fill_style = fill_col
        self.canvas.stroke()
        self.canvas.fill()
        #self.canvas.end_path()

    def draw_details(self):
        hi1 = self.model.i1.y + (self.model.i1.r / 4 if self.model.i1.type == "Circle" else self.model.i1.ry / 2)
        halfLine1 = (0.0, hi1, self.canvas.width, hi1)
        hi2 = self.model.i2.y + (self.model.i2.r / 4 if self.model.i2.type == "Circle" else self.model.i2.ry / 2)
        halfLine2 = (0.0, hi2, self.canvas.width, hi2)
        if hi1 == hi2:
            return
        self.canvas.set_line_dash([10, 5])
        self.canvas.stroke_style = "gray"
        self.canvas.stroke_line(*halfLine1)
        self.canvas.stroke_line(*halfLine2)
        self.canvas.set_line_dash([0, 0])
        self.canvas.stroke_style = "black"
        xi = (self.model.i2.r if self.model.i2.type == "Circle" else self.model.i2.rx) + self.model.i2.x + 25
        self.canvas.stroke_line(xi, hi1, xi, hi2)
        self.canvas.stroke_text("Delta H", xi + 25, (hi1 + hi2) / 2)


def hex(rgb):
    return '#%02x%02x%02x' % rgb