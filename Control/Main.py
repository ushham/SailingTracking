from BoundaryGenerator import BoundaryUpdate as bu
from BoundaryGenerator import PolarData as pol
from Visualisation import PolarPlots as plt
import matplotlib.pyplot as p
import numpy as np

size = [10, 10]

windloc = [0, 0]
windres = [1, 1]

wind1 = np.ones((1, 100, 100))
wind = np.zeros((1, 100, 100))

wind = np.concatenate((wind1, wind), axis=0)


loc = r'C:\Users\UKOGH001\Documents\05 Personal Projects\02 Vendee\02 Routing\Polars'

polars = pol.Polars(loc).readfiles()
point = bu.PointUpdate(wind, polars, 50, 50, windres, windloc)
df = point.UpdatePoints(3)
df1 = df[df['Time'] == 1]
df2 = df[df['Time'] == 2]

x1 = df1['x_loc'].to_numpy()
y1 = df1['y_loc'].to_numpy()

x2 = df2['x_loc'].to_numpy()
y2 = df2['y_loc'].to_numpy()

print(df)

#[id_col, prev_col, time_col, x_col, y_col, theta_col, rad_col, sail_col]

p.scatter(x1, y1)
p.scatter(x2, y2)
p.show()
