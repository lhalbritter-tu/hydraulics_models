import abc
import ipywidgets as widgets
from IPython.display import display, Latex


class Variable:
    def __init__(self, value, base=0, unit=" "):
        self.value = value
        self.unit = unit
        self.base = base

    def real(self):
        return self.value * 10 ** self.base

    def __repr__(self):
        return str(self.value) + " [" + self.unit + "]"

    def __str__(self):
        return self.__repr__()


class Changeable(Variable):
    def __init__(self, widget, base=0, unit=" "):
        super().__init__(widget.value, base, unit)
        self.widget = widget
        self.isActive = True
        self.observe(self.set_value)

    def set_active(self, active):
        self.isActive = active

    def observe(self, func):
        if self.widget is not None:
            self.widget.observe(func)

    def set_value(self, args):
        self.value = self.widget.value


class IntChangeable(Changeable):
    def __init__(self, value, base=0, unit=" ", _min=0, _max=10, desc="", step=1):
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
    def __init__(self, options, tooltips):
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

    def update(self, args):
        self.callback.update_output()

    def set_callback(self, callback):
        self.callback = callback


class ChangeableContainer:
    def __init__(self, changeables: [Changeable], orientation='vertical'):
        self.params = changeables
        self.update(orientation)

    def update(self, orientation='vertical'):
        if orientation == 'vertical':
            self.display = widgets.VBox([param.display for param in self.params if param.isActive])
        else:
            self.display = widgets.HBox([param.display for param in self.params if param.isActive])


class Demo:
    def __init__(self, params: [ChangeableContainer], model: Model, drawable=None):
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
        display(self.widget_output)
        if self.canvas is None:
            display(self.output)
        else:
            display(widgets.VBox([self.canvas, self.output]))
        self.update_output()
        self.model.update(None)

    def update_output(self):
        self.widget_output.clear_output()
        for container in self.params:
            container.update()
        with self.widget_output:
            display(widgets.HBox([param.display for param in self.params]))

        self.output.clear_output()
        with self.output:
            display(Latex(self.model.calculate()))
