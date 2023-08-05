# __init__.py

__version__ = __Version__ = "0.0.1rc1"

from . import core
from . import utils

from .core._plot import plot

from ._loss_viz_ax import LossVizAx



from ._color_map_plot import ColorMapPlot
from ._discretized_color_map import DiscretizedColorMap

from ._temporal_cmap import temporal_cmap
