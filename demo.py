import abc
import ipywidgets as widgets
import numpy as np
from IPython.display import display, Latex
from pythreejs import *

key_light = DirectionalLight(color='white', position=[3, 5, 1], intensity=0.5)
camera = PerspectiveCamera(aspect=3.0, children=(
    DirectionalLight(color='white', intensity=0.5, matrixWorldNeedsUpdate=True, position=(3.0, 5.0, 1.0),
                     quaternion=(0.0, 0.0, 0.0, 1.0), rotation=(0.0, 0.0, 0.0, 'XYZ'), scale=(1.0, 1.0, 1.0),
                     shadow=DirectionalLightShadow(
                         camera=OrthographicCamera(bottom=-5.0, far=500.0, left=-5.0, near=0.5,
                                                   position=(0.0, 0.0, 0.0),
                                                   projectionMatrix=(
                                                       0.2, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0,
                                                       -0.004004004004004004,
                                                       0.0, 0.0, 0.0, -1.002002002002002, 1.0),
                                                   quaternion=(0.0, 0.0, 0.0, 1.0),
                                                   right=5.0, rotation=(0.0, 0.0, 0.0, 'XYZ'), scale=(1.0, 1.0, 1.0),
                                                   top=5.0, up=(0.0, 1.0, 0.0)), mapSize=(512.0, 512.0)),
                     target=Object3D(position=(0.0, 0.0, 0.0), quaternion=(0.0, 0.0, 0.0, 1.0),
                                     rotation=(0.0, 0.0, 0.0, 'XYZ'), scale=(1.0, 1.0, 1.0), up=(0.0, 1.0, 0.0)),
                     up=(0.0, 1.0, 0.0)),), position=(-2.0089665978191187, -0.20001157433694694, -2.7971067062774404),
                           projectionMatrix=(
                               0.7148356401698529, 0.0, 0.0, 0.0, 0.0, 2.1445069205095586, 0.0, 0.0, 0.0, 0.0,
                               -1.00010000500025, -1.0, 0.0, 0.0, -0.200010000500025, 0.0), quaternion=(
        -0.0222177451136849, 0.9557239447492953, -0.07484158994219964, -0.28371966736522314),
                           rotation=(-0.06165791344523469, -1.0358918024734445, -0.053062834466495463, 'XYZ'),
                           scale=(1.0, 1.0, 1.0), up=(0.0, 1.0, 0.0))


def hexcode(rgb):
    return '#%02x%02x%02x' % rgb


class Variable:
    """
    Class for handling a model's Variable with unit representation.
    """

    def __init__(self, value, base=0, unit=" "):
        """
        Initializes a Variable with a given value, a conversion base (actual value = given value * 10^base) and the unit

        :param value: the (initial) value of the variable
        :param base: the conversion base of the variable [Default: 0]
        :param unit: the unit of the variable [Default: ' ']
        """
        self.value = value
        self.unit = unit
        self.base = base

    def real(self):
        """
        Returns the 'real' value of this Variable (aka given value * 10^base)

        :return: the converted value
        """
        return self.value * 10 ** self.base

    def rounded(self, cut=2):
        """
        Returns a String representation of this Variable with cut floating points

        :param cut: the number of floating points to represent [Default: 2]
        :return: string of cut value + unit
        """
        return f'{self.value: .{cut}f} [{self.unit}]'

    def latex(self):
        return str(self.value) + " ~~ " + '[' + self.unit + ']'

    def rounded_latex(self, cut=2):
        return f'{self.value: .{cut}f} ~~ [{self.unit}]'

    def __repr__(self):
        """
        The standard string representation of this Variable, value + unit
        :return: value + unit
        """
        return str(self.value) + " [" + self.unit + "]"

    def __str__(self):
        """
        Wrapper for __repr__
        :return: self.__repr__()
        """
        return self.__repr__()

    def __eq__(self, other):
        return self.value == other.value and self.real() == other.real() and self.unit == other.unit

    def __gt__(self, other):
        return self.value > other.value and self.real() > other.value

    def __ge__(self, other):
        return self.value >= other.value and self.real() >= other.real()


class Changeable(Variable):
    """
    Implementation of Variable which implements a UI widget to interactively change the variable's value
    """

    def __init__(self, widget, base=0, unit=" ", should_update=True):
        """
        Initializes this Changeable Object with the UI widget widget, the base for the Variable and unit for the Variable
        It is recommended to create an object of an implementation of this class, so you don't have to initialize the widget manually

        :param widget: A UI widget, recommended: ipywidgets.widget
        :param base: see Variable::base
        :param unit: see Variable::unit
        """
        super().__init__(widget.value, base, unit)
        self.widget = widget
        self.isActive = True
        self.observe(self.set_value)
        self.should_update = should_update

    def set_active(self, active):
        """
        Tells the widget to show (active) or hide (!active)

        :param active: True, to show the widget, False to hide
        :return: None
        """
        self.isActive = active

    def observe(self, func):
        """
        Registers func as callback to the ipywidgets.widget.observe method

        :param func: the callback function for this widget
        :return: None
        """
        if self.widget is not None:
            self.widget.observe(func, names='value')

    def set_value(self, args):
        """
        Updates the internal value on widget change

        :param args: The change of the UI widget
        :return: None
        """
        self.value = self.widget.value


class PseudoChangeable(Changeable):
    def __init__(self, widget, base=0, unit=" "):
        self.value = 0
        self.base = base
        self.unit = unit
        self.widget = widget
        self.isActive = True


class IntChangeable(Changeable):
    """
    Concrete Implementation of Changeable which implements an IntSlider as UI Widget
    """

    def __init__(self, value, base=0, unit=" ", _min=0, _max=10, desc="", step=1):
        """
        Initializes the internal Variable and Changeable with an ipywidgets.IntSlider with the following attributes:

        :param value: The initial value
        :param base: See Variable::base
        :param unit: See Variable::unit
        :param _min: The minimum value of the slider
        :param _max: The maximum value of the slider
        :param desc: Description of the slider, is printed right next to the Slider
        :param step: The step value of the slider
        """
        super().__init__(widgets.IntSlider(
            value=value,
            min=_min,
            max=_max,
            description=desc,
            step=step,
            continuous_update=False
        ), base, unit)
        self.unitLabel = widgets.Label(f"[{unit}]")
        self.display = widgets.HBox([self.widget, self.unitLabel])


class FloatChangeable(Changeable):
    def __init__(self, value, base=0, unit=" ", _min=.0, _max=10.0, desc="", step=0.1, continuous_update=False,
                 should_update=True):
        """
        Initializes the internal Variable and Changeable with an ipywidgets.FloatSlider with the following attributes:

        :param value: The initial value
        :param base: See Variable::base
        :param unit: See Variable::unit
        :param _min: The minimum value of the slider
        :param _max: The maximum value of the slider
        :param desc: Description of the slider, is printed right next to the Slider
        :param step: The step value of the slider
        """
        super().__init__(widgets.FloatSlider(
            value=value,
            min=_min,
            max=_max,
            description=desc,
            step=step,
            continuous_update=continuous_update
        ), base, unit, should_update=should_update)
        self.unitLabel = widgets.Label(f"$[{unit}]$")
        self.display = widgets.HBox([self.widget, self.unitLabel])


class ToggleGroup(Changeable):
    """
    Implementation of Changeable which implements a ToggleButtonGroup
    """

    def __init__(self, options, tooltips):
        """
        Initializes a ipywidgets.ToggleButtons Object with options=options and tooltips=tooltips

        :param options: List of Options for the Buttons
        :param tooltips: List of Tooltips for each option
        """
        super().__init__(widgets.ToggleButtons(
            options=options,
            tooltips=tooltips
        ))
        self.display = self.widget


class DropDownGroup(Changeable):
    def __init__(self, options, tooltips):
        super().__init__(widgets.Dropdown(
            options=options,
            tooltips=tooltips
        ))
        self.display = self.widget

    def observe(self, func):
        """
        Registers func as callback to the ipywidgets.widget.observe method

        :param func: the callback function for this widget
        :return: None
        """
        if self.widget is not None:
            self.widget.on_trait_change(func)


class BoxHorizontal(PseudoChangeable):
    def __init__(self, children):
        super().__init__(widgets.HBox(
            children=children
        ))
        self.display = self.widget
        self.should_update = True
        self.children = children

    def observe(self, func):
        for child in self.children:
            child.observe(func)


class ClickButton(PseudoChangeable):
    def __init__(self, description="Button", disabled=False, button_style='', tooltip=''):
        super().__init__(widgets.Button(
            description=description,
            disabled=disabled,
            button_style=button_style,
            tooltip=tooltip
        ))
        self.display = self.widget
        self.should_update = False

    def observe(self, func):
        self.widget.on_click(func)


class HorizontalDivider(PseudoChangeable):
    def __init__(self):
        super().__init__(widgets.HTML("<hr>"))
        self.display = self.widget
        self.should_update = False

    def observe(self, func):
        pass


class HorizontalSpace(PseudoChangeable):
    def __init__(self, count=3):
        super().__init__(widgets.HTML("&nbsp;" * count))
        self.display = self.widget
        self.should_update = False

    def observe(self, func):
        pass


class Model(abc.ABC):
    """
    Interface for pipe models
    """

    @abc.abstractmethod
    def calculate(self):
        """
        Returns a string showing all the important calculations for this specific Model
        :return: Representation of all the important calculations
        """
        pass

    @abc.abstractmethod
    def lines(self):
        """
        Returns lines, connecting IntersectionForm 1 with IntersectionForm 2 of this Pipe
        :return: A list of points, which will create a pipe from i1 to i2
        """
        pass

    def render(self):
        """
        Returns a 3D representation of this model

        :return: pythreejs Mesh object
        """
        return BoxBufferGeometry(0, 0, 0)

    def update(self, change):
        """
        Updates the model's attributes when a single Changeable that is subscribed to this model is changed

        :param change: callback param needed for ipywidgets.Widget.observe()
        :return: None
        """
        if self.callback is not None:
            self.callback.update_output()

    def set_callback(self, callback):
        """
        Sets the Demo Callback for this model

        :param callback: A concrete Demo Object
        :return: None
        """
        self.callback = callback


class ChangeableContainer:
    """
    Container class for Changeable Objects. It saves a list of Changeables and provides a (orientation) Layout Box
    containing all the Changeables.
    """

    def __init__(self, changeables: [Changeable], orientation='vertical'):
        """
        Initializes this container with changeable list and orientation

        :param changeables: A list of Changeable Objects to display
        :param orientation: Either 'vertical' for vertical presentation or 'horizontal' for horizontal presentation
                                [Default: vertical]
        """
        self.params = changeables
        self.update(orientation)

    def add(self, changeable: Changeable):
        self.params.append(changeable)
        self.update()

    def update(self, orientation='vertical'):
        """
        Updates the presentation with given orientation

        :param orientation: See ChangeableContainer::__init__()::orientation
        :return: None
        """
        if orientation == 'vertical':
            self.display = widgets.VBox([param.display for param in self.params if param.isActive])
        else:
            self.display = widgets.HBox([param.display for param in self.params if param.isActive])


class Demo:
    """
    Class for setting up a Jupyter interactive Demo of any given implementation of Model
    """

    def __init__(self, params: [ChangeableContainer], model: Model, drawable=None, extra_output=None):
        """
        Initializes the demo object with the interactable params of the model and optionally a drawable widget

        :param params: the interactive changeable params (UI elements) of this specific model
        :param model: the specific model to calculate and draw
        :param drawable: [optional] a canvas or similar widget to draw on
        """
        self.model = model
        self.params = params
        self.canvas = drawable
        self.model.set_callback(self)
        self.widget_output = widgets.Output()
        self.output = widgets.Output()
        self.extra_output = extra_output
        for container in params:
            for param in container.params:
                if param.should_update:
                    param.observe(model.update)

    def show(self):
        """
        Shows all the UI Elements as well as Output widgets and the optional drawable widget

        :return: None
        """
        display(self.widget_output)
        if self.canvas is not None:
            display(self.canvas)
        display(self.output)
        self.update_output()
        # self.model.update(None)

    def update_output(self):
        """
        Callback Method to update the output widgets

        :return: None
        """
        self.widget_output.clear_output(wait=True)
        for container in self.params:
            container.update()
        with self.widget_output:
            display(widgets.HBox([param.display for param in self.params]))

        self.output.clear_output(wait=True)
        op = widgets.HTMLMath(self.model.calculate(), layout=widgets.Layout(width='100%'))
        if self.extra_output is not None:
            op = widgets.HBox(
                [widgets.HTMLMath(self.model.calculate(), layout=widgets.Layout(width='100%')), self.extra_output])
        with self.output:
            display(op)


import matplotlib.pyplot as plt


class Plot:
    def __init__(self, x, y, width=5, height=3.5, title="Plot", xlabel="x", ylabel="y", xlim=None, ylim=None):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlim = xlim
        self.ylim = ylim
        self.fig, self.ax = plt.subplots(figsize=(width, height))
        self.ax.set_title(title)
        self.pl = self.ax.plot(x, y)[0]
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.widget = self.fig.canvas

    def update_plot(self, x=None, y=None, title=None, xlabel=None, ylabel=None, xlim=None, ylim=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.title = title if title is not None else self.title
        self.xlabel = xlabel if xlabel is not None else self.xlabel
        self.ylabel = ylabel if ylabel is not None else self.ylabel
        self.xlim = xlim if xlim is not None else self.xlim
        self.ylim = ylim if ylim is not None else self.ylim
        self.ax.set_title(self.title)
        self.pl.set_data(self.x, self.y)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.widget.draw()
        self.widget.flush_events()

    def set_data(self, x, y):
        self.ax.set_data(x, y)

    def set_xlim(self, xlim):
        self.xlim = xlim
        self.ax.set_xlim(self.xlim)

    def grid(self):
        self.ax.grid()

    def add_line(self, x, color='gray', label=None):
        """
        Adds a vertical line to the plot

        :param x: the x position for the line
        :return: None
        """
        line = self.ax.axvline(x=x, color=color)
        if label is not None:
            self.ax.text(x + 0.5, self.ax.get_ylim()[1] / 2, label)
        self.widget.draw()
        self.widget.flush_events()
        return line

    def update_line(self, line, x):
        line.set_xdata(x)
        self.widget.draw()
        self.widget.flush_events()


class MarkerPlot:
    """
    Helper Class for including a matplotlib Plot with a moveable marker
    """

    def __init__(self, x, y, width=5, height=3.5, title="Plot", xlabel="x", ylabel="y"):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.fig, self.ax = plt.subplots(figsize=(width, height))
        self.ax.set_title(title)
        self.ax.plot(x, y)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_ylim([-0.25, 0.25])
        self.widget = self.fig.canvas
        self.marker = None
        self.mark(0, 0)

    def update_plot(self, x=None, y=None):
        """
        Updates the plot with the new y function and/or new values for x

        :param x: new values for x, Default: None
        :param y: new function for y, Default: None
        :return: None
        """
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.ax.clear()
        self.ax.set_title(self.title)
        self.ax.plot(self.x, self.y)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_ylim([-0.5, 0.5])
        self.marker = None
        self.widget.draw()
        self.widget.flush_events()

    def mark(self, x, y, symbol='o'):
        """
        Moves the marker to position (x, y) on the plot

        :param x: the x position for the marker
        :param y: the y position for the marker
        :param symbol: if there isn't a marker yet, you can specify a symbol (see matplotlib documentation for available symbols), default: 'o'
        :return: None
        """

        self.marker_pos = (x, y)

        if self.marker is None:
            self.marker = plt.plot([x], [y], marker=symbol)[0]
        self.marker.set_data([x], [y])
        self.widget.draw()
        self.widget.flush_events()

    def add_line(self, x, color='gray', label=None):
        """
        Adds a vertical line to the plot

        :param x: the x position for the line
        :return: None
        """
        self.ax.axvline(x=x, color=color)
        if label is not None:
            self.ax.text(x + 0.5, self.ax.get_ylim()[1] / 2, label)
        self.widget.draw()
        self.widget.flush_events()

    def grid(self, axis='both', color='gray', linestyle='-', linewidth=0.2):
        self.ax.grid(axis=axis, color=color, linestyle=linestyle, linewidth=linewidth)
        self.widget.draw()
        self.widget.flush_events()


def from_geometry(geom):
    return BufferGeometry.from_geometry(geom)


def get_attribute(geom, name):
    if name not in geom.attributes:
        return -1
    return geom.attributes[name]


class Cylinder:
    def __init__(self, radiusTop, radiusBottom, height, segments, h_segments):
        self.vertices = []
        self.indices = []
        self.uv = []
        self.normals = []
        self.segments = segments
        self.h_segments = h_segments
        self.height = height

        self.radiusTop = radiusTop
        self.radiusBottom = radiusBottom

        slope = (radiusBottom - radiusTop) / height

        min_height = -self.height / 2
        offset = self.height / max(1, self.h_segments)

        # print(min_height, offset)

        step = 2. * np.pi / segments
        count_extra = 0

        for h in range(1, self.h_segments + 1):
            rt = lerp(radiusBottom, radiusTop, h / self.h_segments)
            rb = lerp(radiusBottom, radiusTop, (h - 1) / self.h_segments)
            # ---------------------- Vertices ------------------ #
            for i in range(segments):
                angle = i * step
                self.vertices.append([rt * np.cos(angle), min_height + offset * h, rt * np.sin(angle)])
                vert = self.vertices[-1].copy()
                vert[1] = slope if 1 < h < self.h_segments else 0
                # vert[0] *= -1 if h == self.h_segments - 1 else 1
                # vert[2] *= -1 if h == self.h_segments - 1 else 1

                # if h == self.h_segments:
                # vert[2] *= -1
                # vert[0] *= -4

                # if h < self.h_segments - 1:
                # self.normals.append([np.cos(angle), slope, np.sin(angle)])
                # else:
                # self.normals.append([-np.cos(angle), slope, -np.sin(angle)])

            for i in range(segments):
                angle = i * step
                self.vertices.append(
                    [rb * np.cos(angle), min_height + offset * (h - 1), rb * np.sin(angle)])
                vert = self.vertices[-1].copy()
                vert[1] = slope if 1 < h < self.h_segments else 0
                # vert[0] *= -1 if h == self.h_segments - 1 else 1
                # vert[2] *= -1 if h == self.h_segments - 1 else 1

                # if h < self.h_segments - 1:
                # self.normals.append([np.cos(angle), slope, np.sin(angle)])
                # else:
                # self.normals.append([-np.cos(angle), slope, -np.sin(angle)])
            if h == self.h_segments:
                self.vertices.append([0, min_height + offset * h, 0])
            if h == 1:
                self.vertices.append([0, min_height + offset * (h - 1), 0])
            center_top_i = len(self.vertices) - 1
            center_bot_i = len(self.vertices) - 1

            # ---------------------- Indices --------------------- #
            if h == self.h_segments:
                for i in range(segments):
                    self.indices.append([((i + 1) % segments) + (2 * segments * (h - 1)) + count_extra])
                    self.indices.append([i + (2 * segments * (h - 1)) + count_extra])
                    self.indices.append([center_top_i])
            if h == 1:
                for i in range(segments):
                    self.indices.append([i + segments + (2 * segments * (h - 1))])
                    self.indices.append([((i + 1) % segments + segments) + (2 * segments * (h - 1))])
                    self.indices.append([center_bot_i])

            for i in range(segments):
                self.indices.append([i + (2 * segments * (h - 1)) + count_extra])
                self.indices.append([((i + 1) % segments) + (2 * segments * (h - 1)) + count_extra])
                self.indices.append([i + segments + (2 * segments * (h - 1)) + count_extra])

                self.indices.append([((i + 1) % segments + segments) + (2 * segments * (h - 1)) + count_extra])
                self.indices.append([i + segments + (2 * segments * (h - 1)) + count_extra])
                self.indices.append([((i + 1) % segments) + (2 * segments * (h - 1)) + count_extra])

            # ----------------------- Normals -------------------------- #
            for i in range(segments * 2):
                vert = self.vertices[i + (2 * segments * (h - 1)) + count_extra].copy()
                vert[1] = slope
                self.normals.append(normalize(vert))
            if h == self.h_segments:
                for i in range(segments):
                    self.normals.append([0., 1., 0.])
                self.normals.append([0., 1., 0.])
                count_extra += 1
            if h == 1:
                #for i in range(segments - 1):
                #    self.normals.append([0., -1., 0.])
                self.normals.append([0., -1., 0.])
                count_extra += 1

            # -------------------------- UVs ----------------------------- #
            max_angle = step * (segments - 1)
            for i in range(segments):
                    u = i * step
                    self.uv.append([u, min_height + offset * (h - 1)])

            for i in range(segments):
                    u = i * step
                    self.uv.append([u, min_height + offset * h])

            for i in range(segments):
                angle = i * step
                u = rt * np.cos(angle) / max_angle
                v = rt * np.sin(angle) / max_angle

                self.uv.append([u, v])

            for i in range(segments):
                angle = i * step
                u = rb * np.cos(angle) / max_angle
                v = rb * np.sin(angle) / max_angle

                self.uv.append([u, v])
            self.uv.append([0., 0.])
            #self.uv.append([0., min_height + offset * (h - 1)])

    def my_cyl(self):
        return BufferGeometry(index=BufferAttribute(array=np.array(self.indices, dtype=np.uint16)), attributes={
            'position': BufferAttribute(array=np.array(self.vertices, dtype=np.float32), normalized=True),
            'normal': BufferAttribute(array=np.array(self.normals, dtype=np.float32), normalized=True),
            'uv': BufferAttribute(array=np.array(self.uv, dtype=np.float32), normalized=True),
        })

    def set_radiusTop(self, radiusTop):
        self.radiusTop = radiusTop
        step = 2. * np.pi / self.segments
        for h in range(1, self.h_segments + 1):
            rt = lerp(self.radiusBottom, radiusTop, h / self.h_segments)
            rb = lerp(self.radiusBottom, radiusTop, (h - 1) / self.h_segments)
            for i in range(self.segments):
                angle = i * step
                self.vertices[i + (2 * self.segments * (h - 1)) + (h - 1) * 2] = [rt * np.cos(angle), self.height / 2,
                                                                                  rt * np.sin(angle)]

    def set_radiusBottom(self, radiusBottom):
        self.radiusBottom = radiusBottom
        step = 2. * np.pi / self.segments
        for h in range(1, self.h_segments + 1):
            rt = lerp(radiusBottom, self.radiusTop, h / self.h_segments)
            rb = lerp(radiusBottom, self.radiusTop, (h - 1) / self.h_segments)
            for i in range(self.segments, self.segments * 2):
                angle = i * step
                self.vertices[i + (2 * self.segments * (h - 1)) + (h - 1) * 2] = [rb * np.cos(angle), -self.height / 2,
                                                                                  rb * np.sin(angle)]


def normalize(vec: list):
    x, y, z = vec[0], vec[1], vec[2]
    l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    return [x / l, y / l, z / l]


def lerp(v0, v1, t):
    return (1 - t) * v0 + t * v1


class MultiPlot:
    def __init__(self, width=3, height=3):
        self.width = width
        self.height = height
        self.clear()

    def add_ax(self, x, y, color='blue', xlim=None, ylim=None, xlabel=None, ylabel=None, title=None):
        self.axes[-1].plot(x, y, color=color)
        self.ax_data[self.axes[-1]] = {'xlim': xlim, 'ylim': ylim, 'xlabel': xlabel, 'ylabel': ylabel, 'title': title}
        self.axes[-1].set_xlabel(xlabel)
        self.axes[-1].set_ylabel(ylabel)
        self.axes[-1].set_title(title)
        self.axes.append(plt.axes())
        self.marker.append(None)
        self.mark(len(self.axes) - 2, x[0], y[0])
        return len(self.axes) - 2

    def grid(self, i, axis='both', color='gray', linestyle='-', linewidth=0.2):
        self.axes[i].grid(axis=axis, color=color, linestyle=linestyle, linewidth=linewidth)
        self.widget.draw()
        self.widget.flush_events()

    def set_visible(self, i):
        for j in range(len(self.axes)):
            self.axes[j].set_visible(i == j)
        xlim = self.ax_data[self.axes[i]]['xlim']
        ylim = self.ax_data[self.axes[i]]['ylim']
        xlabel = self.ax_data[self.axes[i]]['xlabel']
        ylabel = self.ax_data[self.axes[i]]['ylabel']
        title = self.ax_data[self.axes[i]]['title']
        print(xlim, ylim)
        self.axes[i].set_xlim(xlim)
        self.axes[i].set_ylim(ylim)
        self.widget.draw()
        self.widget.flush_events()

    def set_data(self, i, x, y):
        if i < 0 or i >= len(self.axes):
            return False
        ax = self.axes[i]
        col = ax.get_lines()[0].get_color()
        xlim, ylim, xlabel, ylabel, title = ax.get_xlim(), ax.get_ylim(), ax.get_xlabel(), ax.get_ylabel(), ax.get_title()
        ax.clear()
        ax.plot(x, y, color=col)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        self.marker[i] = None
        # self.mark(i, x[0], y[0])
        # self.axes[i].set_data(x, y)
        return True

    def clear(self):
        self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))
        self.widget = self.fig.canvas
        self.axes = [self.ax]
        self.ax_data = {self.ax: {'x': [], 'y': []}}
        self.marker = []

    def __len__(self):
        return len(self.axes) - 1

    def canvas(self):
        return self.fig.canvas

    def show(self):
        self.fig.show()

    def mark(self, i, x, y, symbol='o'):
        if self.marker[i] is None:
            self.marker[i] = self.axes[i].plot([x], [y], marker=symbol)[0]
        self.marker[i].set_data([x], [y])
        self.widget.draw()
        self.widget.flush_events()


if __name__ == '__main__':
    mp = MultiPlot()
    # mp.add_ax([0, 1, 2, 3, 4], [2, 4, 6, 8, 10], color='orange')
    # mp.add_ax([0, 1, 2, 3, 4], [3, 6, 9, 25, 15], color='green')
    # mp.add_ax([5, 6, 7, 8], [0, -2, -5, 10], color='red')
    # mp.add_ax([0, 1, 2, 3, 4], [30, 10, 30, 10, 30], color='yellow')
    # mp.add_ax([0, 1, 2, 3, 4], [5, 0, -5, 0, 5], color='purple')
    mp.add_ax([0, 0.01, 2, 3], [10, 0, 0, 0])
    mp.add_ax([4, 4.01], [10, 0], color='red')
    mp.add_ax([4.01, 5, 6], [10, 10, 10], color='red')
    mp.add_ax([4.01, 5.5], [5, 5], color='red')
    mp.add_ax([4.01, 5, 6], [0, 0, 0], color='red')
    mp.add_ax([7, 10], [10, 10], color='green')
    mp.add_ax([7, 7.01], [9, 1], color='green')
    mp.add_ax([7, 10], [0, 0], color='green')
    mp.add_ax([10, 10.01], [9, 1], color='green')
    mp.show()
    while True:
        n = input("Enter Plot to show [0-" + str(len(mp) - 1) + "]: ")
        if int(n) > len(mp) - 1 or int(n) < 0:
            mp.clear()
            continue
        mp.set_visible(int(n))
        mp.show()
