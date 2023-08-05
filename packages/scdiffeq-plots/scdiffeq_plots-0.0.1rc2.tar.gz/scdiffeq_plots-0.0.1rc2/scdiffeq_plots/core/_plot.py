
import matplotlib.pyplot as plt
import matplotlib
import math

from .. import utils

from ._plot_dimensions import PlotDimensions
from ._style_spines import style_spines


from typing import List


# -- Main class: ---------------------------------------------------------------
class Plot(utils.ABCParse):
    def __init__(
        self,
        nplots: int =1,
        ncols: int =1,
        scale: float =None,
        width: float =1,
        height: float =1,
        hspace: float =0,
        wspace: float =0,
        width_ratios: List[float]=None,
        height_ratios: List[float]=None,
        *args,
        **kwargs,
    ):
        super().__init__()
        
        self.__parse__(locals(), private = [None])
        
        self._configure_plot_size()
        
    def _configure_plot_size(self):

        if not self._is_none(self.scale):
            self.height = self.width = self.scale
            
        self._plot_dim_config = PlotDimensions(self.ncols, self.nrows, self.width, self.height)
        self.height, self.width = self._plot_dim_config()
    
    
    @property
    def nrows(self):
        return math.ceil(self.nplots / self.ncols)
        
        
    @property
    def gridspec(self):
        return matplotlib.gridspec.GridSpec(
            nrows=self.nrows,
            ncols=self.ncols,
            width_ratios=self.width_ratios,
            height_ratios=self.height_ratios,
            hspace=self.hspace,
            wspace=self.wspace,
        )
    
    @property
    def figure(self):
        return plt.figure(figsize=(self.width, self.height))
    
    def rm_ticks(self):

        for ax in self.axes:
            ax.set_xticks([])
            ax.set_yticks([])
            
    def linearize_axes(self):

        axes = []

        for i, row in self.AxesDict.items():
            for j, col in row.items():
                axes.append(self.AxesDict[i][j])
        return axes

    def __call__(
        self,
        linearize: bool = True,
        rm_ticks: bool = False,
    ):

        plot_count = 0
        self.AxesDict = {}

        self.fig = self.figure
        gridspec = self.gridspec

        for ax_i in range(self.nrows):
            self.AxesDict[ax_i] = {}
            for ax_j in range(self.ncols):
                plot_count += 1
                self.AxesDict[ax_i][ax_j] = self.fig.add_subplot(gridspec[ax_i, ax_j])
                if plot_count >= self.nplots:
                    break

        if not linearize:
            return self.fig, self.AxesDict
        else:
            self.axes = self.linearize_axes()
            if rm_ticks:
                self.rm_ticks()
                
            return self.fig, self.axes


# -- API-facing function: ------------------------------------------------------
def plot(
    nplots: int = 1,
    ncols: int = 1,
    scale: float = None,
    width: float = 1,
    height: float = 1,
    hspace: float = 0,
    wspace: float = 0,
    width_ratios: List[float] = None,
    height_ratios: List[float] = None,
    linearize=True,
    rm_ticks=False,
    color=[None],
    move=[0],
    xy_spines=False,
    delete_spines=[[]],
    color_spines=[[]],
    move_spines=[[]],
):
    """
    Parameters:
    -----------

    Returns:
    --------
    fig, axes
    """

    plot_obj = Plot(
        nplots=nplots,
        ncols=ncols,
        scale=scale,
        width=width,
        height=height,
        hspace=hspace,
        wspace=wspace,
        width_ratios=width_ratios,
        height_ratios=height_ratios,
    )
    
    fig, axes = plot_obj(linearize=linearize, rm_ticks=rm_ticks)
    
    color = color * nplots
    move = move * nplots
        
    if xy_spines:
        delete_spines = [["top", "right"]] * nplots
    elif delete_spines == True:
        delete_spines = [["top", "bottom", "right", "left"]] * nplots
    else:
        delete_spines = delete_spines * nplots

    color_spines = color_spines * nplots
    move_spines = move_spines * nplots
        
    # styling in function requires linearization
    if linearize:
        for n, ax in enumerate(axes):
            style_spines(
                ax,
                color=color[n],
                move=move[n],
                delete_spines=delete_spines[n],
                color_spines=color_spines[n],
                move_spines=move_spines[n],
            )
        
    return fig, axes