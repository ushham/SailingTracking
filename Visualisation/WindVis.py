import numpy as np
import matplotlib.pyplot as plt

def SailType(col):
    cols = ['red', 'green']
    color = []
    for i in col:
        color.append(cols[int(i)])
    return color

def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))

def WindVec(u, v, x, y, xx, yy, path, col, sail, bool):
    fig1, ax1 = plt.subplots()
    M = np.hypot(u, v) / 500
    Q = ax1.quiver(x, y, u/5, v/5, M, pivot='tip', width=0.002, scale=1/0.015)
    if bool:
        T = ax1.scatter(xx, yy)
    clr = SailType(col)[1:]
    for i in range(len(path) - 1):
        xt, yt = [xx[path[i]], xx[path[i + 1]]], [yy[path[i]], yy[path[i + 1]]]
        ax1.plot(xt, yt, color=clr[i], label=sail[int(col[i+1])])
    legend_without_duplicate_labels(ax1)
    ax1.scatter(x, y, color='0.5', s=1)
    plt.show()


