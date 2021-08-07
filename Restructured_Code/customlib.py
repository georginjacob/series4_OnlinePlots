import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def figure_layout_creation(fig_num=1):
    fig = plt.figure(num=fig_num,constrained_layout=True )
    gs = GridSpec(4, 3, figure=fig)
    GridDef = [gs[0,0],gs[0,1],gs[1:3, 0],gs[1:3, 1],gs[:, -1],gs[-1, 0],gs[-1, -2]]  # gs[0,0] = subplot (0,0) in 4 x 3 subplot matrix.
    ax=[]
    for i in range(7):
        ax.append(fig.add_subplot(GridDef[i]))
  
    plt.show(block=False) # Block = False avoids the halt at plot
    return ax

