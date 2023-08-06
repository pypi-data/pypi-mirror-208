""" Number chart """


class TableHeader:
  """ Table header chart configuration """

  def __init__(self, label, key):
    """ Constructor

    Arguments
    ---
    label (str): Label of the header
    key (str): Key of the header
    """
    self._label = label
    self._key = key

  @property
  def label(self):
    """ Get the label """
    return self._label

  @property
  def key(self):
    """ Get the key """
    return self._key


class TableRow:
  """ Table row chart configuration """

  def __init__(self, data):
    """ Constructor

    Arguments
    ---
    data (dict): Data of the row
    """
    self._data = data

  @property
  def data(self):
    """ Get the data """
    return self._data


class TableChart:
  """
  Table chart configuration
  """

  def __init__(self, columns, rows):
    """
    Constructor

    Arguments
    ---
    columns (list[TableHeader]): List of columns
    rows (list[TableRow]): List of rows
    """
    self._columns = columns
    self._rows = rows

  @property
  def columns(self):
    """ Get the columns """
    return self._columns

  @property
  def rows(self):
    """ Get the rows """
    return self._rows

  def render(self):
    """
    Render chart to a graphic Library.
    """
    return {
      'library': 'FLUTTER',
      'chart': 'TABLE',
      'configuration': self._render_flutter(),
    }

  def _render_flutter(self):
    """
    Converts the configuration of the chart to a Flutter native components.
    """
    return {
      'columns': [{
        'key': column.key,
        'label': column.label
      } for column in self._columns],
      'rows': [{
        'data': row.data
      } for row in self._rows],
    }
