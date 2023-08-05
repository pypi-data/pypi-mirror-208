
from .. import utils

class SpineStyler(utils.ABCParse):
    def __init__(self, ax):
        super().__init__()

        self.__parse__(locals())

    def __select__(self, kwargs, ignore=[]):
        ignore += ["self"]
        return {k: v for k, v in kwargs.items() if not k in ignore}

    def color(self, color, left=False, right=False, bottom=False, top=False):

        spines = self.__select__(locals(), ignore=["color"])
        [self.ax.spines[spine].set_color(color) for spine, val in spines.items() if val]

    def delete(self, left=False, right=False, bottom=False, top=False):
        spines = self.__select__(locals())
        [
            self.ax.spines[spine].set_visible(False)
            for spine, val in spines.items()
            if val
        ]

    def position(
        self,
        amount,
        position_type="outward",
        top=False,
        bottom=False,
        right=False,
        left=False,
    ):

        spines = self.__select__(locals(), ignore=["position_type", "amount"])
        [
            self.ax.spines[spine].set_position((position_type, amount))
            for spine, val in spines.items()
            if val
        ]
        
def convert_args(spine_list=[]):
    if spine_list == "all":
        spine_list = ["top", "bottom", "right", "left"]
    return {spine: True for spine in spine_list}


def style_spines(
    ax, color=None, move=0, delete_spines=[], color_spines=[], move_spines=[]
):

    spine_style = SpineStyler(ax)
    if color:
        spine_style.color(color, **convert_args(color_spines))
    spine_style.delete(**convert_args(delete_spines))
    if move:
        spine_style.position(
            amount=move, position_type="outward", **convert_args(move_spines)
        )
