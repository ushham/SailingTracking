from BoundaryGenerator import BoundaryUpdate as bu
from BoundaryGenerator import PolarData as pol
from Visualisation import PolarPlots as plt
import matplotlib.pyplot as p
from Control import Wind
import numpy as np


loc = r'C:\Users\UKOGH001\Documents\05 Personal Projects\02 Vendee\02 Routing\Polars'

polars = pol.Polars(loc).readfiles()
point = bu.PointUpdate(Wind.wind, polars, 5, 5)
df = point.UpdatePoints(4, 5)
df1 = df[df['Time'] == 1]
df2 = df[df['Time'] == 2]
df3 = df[df['Time'] == 3]

x1 = df1['x_loc'].to_numpy()
y1 = df1['y_loc'].to_numpy()

x2 = df2['x_loc'].to_numpy()
y2 = df2['y_loc'].to_numpy()

x3 = df3['x_loc'].to_numpy()
y3 = df3['y_loc'].to_numpy()

print(df)

#[id_col, prev_col, time_col, x_col, y_col, theta_col, rad_col, sail_col]

p.scatter(x1, y1)
p.scatter(x2, y2)
p.scatter(x3, y3)
p.show()
