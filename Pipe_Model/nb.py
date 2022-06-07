import model
import ipywidgets as widgets
from IPython.display import display, Markdown, Latex

def demo(canvas):
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
        canvas.clear()
        draw_circle(canvas, c1, 25)
        draw_circle(canvas, c2, 400)
        lc1 = draw_lines(canvas, c1, 25)
        lc2 = draw_lines(canvas, c2, 400, True)
        canvas.stroke_line(lc1[0][2], lc1[0][1], lc2[0][2] + 1, lc2[0][1])
        canvas.stroke_line(lc1[1][2], lc1[1][1], lc2[1][2] + 1, lc2[1][1])

    redraw()
    
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