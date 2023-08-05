
from .. import utils


import matplotlib

class PlotDimensions(utils.ABCParse):
    """
    Container for plot dimenions. Starts from the defaults read
    from the rcParams file wherein width, height are unpacked
    as: [width, height].
    """

    def __init__(self, ncols: str, nrows: str, width: float, height: float):
        super().__init__()

        self.__parse__(locals(), public=[None])

    @property
    def default_width(self):
        return matplotlib.rcParams["figure.figsize"][0]

    @property
    def default_height(self):
        return matplotlib.rcParams["figure.figsize"][1]

    @property
    def height(self):
        return self.default_height * self._nrows * self._height

    @property
    def width(self):
        return self.default_width * self._ncols * self._width

    def __call__(self):
        return self.height, self.width