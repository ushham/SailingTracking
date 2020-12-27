import numpy as np
import matplotlib.pyplot as plt

def polarplt(arr, windspeed):
    rows = 360
    ang = 2 * np.pi * (rows - 1) / rows
    theta = np.linspace(0, ang, rows)
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    if arr.shape[0] != rows:
        dim = arr.shape[0]
        for d in range(dim):
            print(arr[d, :, windspeed])
            ax.plot(theta, arr[d, :, windspeed].T)
    else:
        ax.plot(theta, arr[:, windspeed])

    plt.show()
    return 0