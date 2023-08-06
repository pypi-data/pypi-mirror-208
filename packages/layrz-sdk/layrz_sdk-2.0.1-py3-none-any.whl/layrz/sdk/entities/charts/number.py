""" Number chart """


class NumberChart:
  """
  Number chart configuration
  """

  def __init__(self, value, color, label):
    """
    Constructor

    Arguments
    ---
    value (num): Value of the number
    color (str): Color of the number
    label (str): Label of the number
    """
    self._value = value
    self._color = color
    self._label = label

  @property
  def value(self):
    """ Get the value """
    return self._value

  @property
  def color(self):
    """ Get the color """
    return self._color

  @property
  def label(self):
    """ Get the label """
    return self._label

  def render(self):
    """
    Render chart to a graphic Library.
    """
    return {
      'library': 'FLUTTER',
      'chart': 'NUMBER',
      'configuration': self._render_flutter(),
    }

  def _render_flutter(self):
    """
    Converts the configuration of the chart to a Flutter native components.
    """
    return {
      'value': self._value,
      'color': self._color,
      'label': self._label,
    }
