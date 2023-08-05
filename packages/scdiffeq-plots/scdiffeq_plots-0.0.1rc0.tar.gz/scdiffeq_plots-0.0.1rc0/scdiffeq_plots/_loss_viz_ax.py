
class LossVizAx:
    def __init__(
        self,
        ax,
        grid=True,
        title=None,
        x_label="Epoch",
        y_label="Sinkhorn Divergence",
        title_fontsize: int = 10,
        label_fontsize: int = 8,
        tick_param_size: int = 6,
    ):

        self.ax = ax
        self.ax.set_xlabel(x_label, fontsize=label_fontsize)
        self.ax.set_ylabel(y_label, fontsize=label_fontsize)

        if grid:
            self.ax.grid(zorder=0, alpha=0.5)
        self.ax.set_title(title, fontsize=10)
        self.ax.tick_params(axis="both", which="both", labelsize=tick_param_size)

    def __call__(self, vals, label=None, color=None, zorder=None):
        self.ax.plot(vals, label=label, color=color, zorder=zorder, lw=2)
        self.ax.legend(edgecolor="None", fontsize=8)