import matplotlib.pyplot as plt
import customlib as lib
import numpy as np

 
def format_axes(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)

ax0= lib.figure_layout_creation(0)
x = np.random.randn(4, 1)
y=2*x
for i in range(7):
    ax0[i].plot(x,y)

plt.show()

