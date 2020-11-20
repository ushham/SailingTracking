import numpy as np
from Control import Parameters as p
from Visualisation import WindVis as wv

size = p.size
res = p.res
X, Y = np.meshgrid(np.arange(0, size[1], res[1]), np.arange(0, size[0], res[0]))

# u = 0.4 * (5 - Y)
# v = 0.4 * (X - 5)

u = np.sin(X)
v = np.cos(Y)

wind = [u, v]
