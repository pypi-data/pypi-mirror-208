
import matplotlib
import numpy as np
import os

from . import utils

from typing import Union
NoneType = type(None)

from ._discretized_color_map import DiscretizedColorMap

def temporal_cmap(
    t: Union['torch.Tensor', np.ndarray, list] = None,
    cmap=matplotlib.cm.plasma_r,
    idx_slice=1,
    pad_left=5,
    pad_right=6,
    plot=False,
    save=False,
    save_format: str = "svg",
    save_dir=os.getcwd(),
    silent: bool = False,
):

    t_cmap = DiscretizedColorMap(
        **utils.extract_func_kwargs(DiscretizedColorMap, kwargs=locals())
    )()

    if isinstance(t, NoneType):
        return t_cmap
    else:
        return t_cmap[np.floor(np.linspace(0, len(t_cmap) - 1, len(t))).astype(int)]
