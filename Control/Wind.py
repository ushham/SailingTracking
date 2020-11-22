import numpy as np
from Control import Parameters as p
from Visualisation import WindVis as wv

size = p.size
res = p.res
X, Y = np.meshgrid(np.arange(0, size[1], res[1]), np.arange(0, size[0], res[0]))

u = 2 * (Y - 5)
v = 2 * (5 - X)

#u = 10 * np.cos(X)
#v = 10 * np.sin(Y)

wind = [u, v]
