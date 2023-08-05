
# # -- import packages: ------------------------------------------------------------
# import matplotlib.pyplot as plt
# from matplotlib import cm
# import numpy as np
# import vinplots


# # -- API-facing class: -----------------------------------------------------------
# class TimeColorMap:
#     def __init__(self):

#         self.cmap = np.array(cm.plasma_r.colors)

#     def __plot__(self, save_plot):

#         self.fig, self.axes = vinplots.quick_plot(
#             nplots=1,
#             ncols=1,
#             figsize_height=0.05,
#             figsize_width=1,
#             spines_to_delete="all",
#             rm_ticks=True,
#         )

#         xr = range(len(self.cmap_dt))
#         img = self.axes[0].bar(xr, height=1, width=1, color=self.cmap_dt)
#         if not isinstance(save_plot, type(None)):
#             plt.savefig(save_plot)

#     def __call__(
#         self,
#         idx_slice=6,
#         pad_left=1,
#         pad_right=1,
#         plot=False,
#         save_plot: bool = "cbar.time.svg",
#     ):
#         """
#         Examples:
#         ---------
#         tc = dt_cmap(idx_slice=6, pad_left=1, pad_right=1, plot=True)
#         """
#         self.cmap_dt = self.cmap[::idx_slice][pad_left:-pad_right]

#         if plot:
#             self.__plot__(save_plot)

#         return self.cmap_dt