import abc
import ipywidgets as widgets
from IPython.display import display, Latex
from pythreejs import *


key_light = DirectionalLight(color='white', position=[3, 5, 1], intensity=0.5)
camera = PerspectiveCamera(position=[0, 0, 5], up=[0, 1, 0], children=[key_light], aspect=600 / 200)


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


class Changeable(Variable):
    """
    Implementation of Variable which implements a UI widget to interactively change the variable's value
    """
    def __init__(self, widget, base=0, unit=" "):
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
    def __init__(self, value, base=0, unit=" ", _min=.0, _max=10.0, desc="", step=0.1):
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
            continuous_update=False
        ), base, unit)
        self.unitLabel = widgets.Label(f"[{unit}]")
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

    def __init__(self, params: [ChangeableContainer], model: Model, drawable=None):
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
        for container in params:
            for param in container.params:
                param.observe(model.update)

    def show(self):
        """
        Shows all the UI Elements as well as Output widgets and the optional drawable widget

        :return: None
        """
        display(self.widget_output)
        if self.canvas is None:
            display(self.output)
        else:
            display(widgets.VBox([self.canvas, self.output]))
        self.update_output()
        # self.model.update(None)

    def update_output(self):
        """
        Callback Method to update the output widgets

        :return: None
        """
        self.widget_output.clear_output()
        for container in self.params:
            container.update()
        with self.widget_output:
            display(widgets.HBox([param.display for param in self.params]))

        self.output.clear_output()
        with self.output:
            display(Latex(self.model.calculate()))
