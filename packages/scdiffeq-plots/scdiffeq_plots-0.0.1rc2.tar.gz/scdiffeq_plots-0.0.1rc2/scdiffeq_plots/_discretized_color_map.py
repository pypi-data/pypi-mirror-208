import numpy as np
import matplotlib
import os

from . import utils
from ._color_map_plot import ColorMapPlot

class DiscretizedColorMap(utils.ABCParse):
    def __init__(
        self,
        cmap: matplotlib.colors.Colormap = matplotlib.cm.plasma_r,
        idx_slice=5,
        pad_left=5,
        pad_right=6,
        plot=False,
        save=True,
        save_format: str = 'svg',
        save_dir=os.getcwd(),
        silent: bool = False,
    ):

        self.__parse__(locals(), public=[None])

    @property
    def _CMAP(self):
        return np.array(self._cmap.colors)

    @property
    def handle(self):
        return self._CMAP[:: self._idx_slice][self._pad_left : -self._pad_right]

    def __len__(self):
        return int(len(self.handle) - 1)

    @property
    def _NAME(self):
        return self._cmap.name
    
    @property
    def _PLOT_KWARGS(self):
        return utils.extract_func_kwargs(func = ColorMapPlot, kwargs = self._PARAMS, ignore=['self', 'cmap'])
        
    @property
    def plot(self):
        return ColorMapPlot(cmap=self, **self._PLOT_KWARGS).plot()
        

    def __call__(self):
        return self.handle
