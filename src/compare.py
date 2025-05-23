import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection


def compare():

    buffer = np.array([2,3,5,7,9,11])
    buffermin = np.array([2,3,4.99,7.01,9,11])
    buffermax = np.array([2,3.01,5,7.04,9.04,11.14])

    hanna = np.array([1.97,2.85,5.02,7.04,9.11,11.2])
    ardui = np.array([np.nan,2.82,4.99,7.04,9.03,11.19])
    ardui_2 = np.array([1.94,2.81,4.98,np.nan,9.09,11.07])

    fig, ax = plt.subplots(1)
    # for i in range(len(buffer)):
    #     ax.plot([buffer[i],buffer[i]],[buffermin[i],buffermax[i]],'o-', color='C0')

    ax.plot(buffer, hanna-buffer,'o', color='C1')
    ax.plot(buffer, ardui-buffer,'o', color='C2')
    ax.plot(buffer, ardui_2-buffer,'o', color='C2')
    r = Rectangle((1,-0.05),11,0.1)
    p = PatchCollection([r], facecolor='C0',alpha=0.4)
    ax.add_collection(p)

    plt.show()

compare()