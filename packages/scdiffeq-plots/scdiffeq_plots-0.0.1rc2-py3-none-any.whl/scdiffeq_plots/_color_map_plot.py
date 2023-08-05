
# -- import packages: ----------------------------------------------------------
import matplotlib.pyplot as plt
import os


# -- import local dependencies: ------------------------------------------------
from . import utils, core


# -- API-facing class: ---------------------------------------------------------
class ColorMapPlot(utils.ABCParse):
    def __init__(
        self,
        cmap,
        save: bool = True,
        save_format: str = "svg",
        save_dir=os.getcwd(),
        silent: bool = False,
    ):

        self.__parse__(locals(), public=["cmap"])
        self._INFO = utils.InfoMessage()

    @property
    def _PLOT(self):
        return core.plot(
            nplots=1,
            ncols=1,
            height=0.05,
            width=1,
            delete_spines=["all"],
            rm_ticks=True,
        )

    @property
    def _NAME(self):
        return self.cmap._NAME

    @property
    def _X_RANGE(self):
        return range(self._LEN)

    @property
    def _LEN(self):
        return len(self.cmap)

    @property
    def _FNAME(self):
        return ".".join(
            ["discretized_cmap", self._NAME, f"{self._LEN}_steps", self._save_format]
        )

    @property
    def _FPATH(self):
        return os.path.join(self._save_dir, self._FNAME)

    def plot(self):
        self._fig, self._axes = self._PLOT
        img = self._axes[0].bar(self._X_RANGE, height=1, width=1, color=self.cmap())
        plt.show()
        if self._save:
            self.save()

    def _msg_save(self):
        if not self._silent:
            return self._INFO(f"Saving ColorMapBarPlot to: {self._FPATH}")

    def save(self):
        self._msg_save()
        plt.savefig(self._FPATH)
        plt.close()

    def __call__(self):
        self.plot()
