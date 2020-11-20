import numpy as np
import matplotlib.pyplot as plt

def polarplt(arr, cols):
    rows = 360
    ang = 2 * np.pi * (rows - 1) / 360
    theta = np.linspace(0, ang, rows)
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    if arr.shape[0] != rows:
        dim = arr.shape[0]
        for d in range(dim):
            print(arr[d, :, cols])
            ax.plot(theta, arr[d, :, cols].T)
    else:
        ax.plot(theta, arr[:, cols])

    plt.show()
    return 0