import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def figure_layout_creation(fig_num=1):
    fig = plt.figure(num=fig_num,constrained_layout=True,figsize=(10,8) )
    gs = GridSpec(4, 3, figure=fig)
    GridDef = [gs[0,0],gs[0,1],gs[1:3, 0],gs[1:3, 1],gs[:, -1],gs[-1, 0],gs[-1, -2]]  # gs[0,0] = subplot (0,0) in 4 x 3 subplot matrix.
    
    # 0-correct-same-hist, 1-correct-diff-hist,2- correct-same-raster, 3- correct-diff-raster
    # 4-correct-all-raster,5-wrong-same-raster,6-wrong-diff-raster   
    ax=[]
    for i in range(7):
        ax.append(fig.add_subplot(GridDef[i]))
        if(i==2 or i==3): # same and diff correct raster
            ax[i].set_ylim(1,40)
            ax[i].set_yticks([])
        if(i==4): # All raster
            ax[i].set_ylim(1,80)
            ax[i].set_yticks([])
            ax[i].set_xlim(-0.4,2.6)
        if(i==5 or i==6): # wrong raster
            ax[i].set_ylim(1,20)
            ax[i].set_yticks([])
        if (i==2 or i==4 or i==5):
            ax[i].set_ylabel('Trial count ->')
        if(i==4 or i==5 or i==6):
            ax[i].set_xlabel('Relative Times (s)')
        if(i!=4):
            ax[i].set_xlim(-0.2,1)
        

    ax[0].set_title('Response correct SAME trials')
    ax[0].set_ylabel('Norm. Firing Rate')
    ax[0].set_ylim(0,1)

    ax[1].set_title('Response correct DIFF trials')
    ax[1].set_ylim(0,1)
    ax[1].set_yticks([])

    ax[4].set_title('ALL Trials')

    ax[5].set_title('Response wrong SAME trials')
    ax[6].set_title('Response wrong DIFF trials')

    plt.show(block=False) # Block = False avoids the halt at plot
    return fig, ax



