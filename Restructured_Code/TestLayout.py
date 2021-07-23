import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def create_initial_figure(fig_num):
    fig = plt.figure(num=fig_num,constrained_layout=True )
    gs = GridSpec(4, 3, figure=fig)
    GridDef = [gs[0,0],gs[0,1],gs[1:3, 0],gs[1:3, 1],gs[:, -1],gs[-1, 0],gs[-1, -2]]# gs[0,0] = subplot (0,0) in 4 x 3 subplot matrix.
    ax=[]
    for i in range(7):
        ax.append(fig.add_subplot(GridDef[i]))
    fig.suptitle("GridSpec")
    format_axes(fig)
    plt.show()
    plt.close()


def format_axes(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)


create_initial_figure(1)
