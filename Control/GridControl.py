import numpy as np
import pandas as pd
from Control import Wind
from Visualisation import WindVis as wv
from Visualisation import PolarPlots as pp
from GridCreator import GridStep as gs
from Control import Parameters as p
from BoundaryGenerator import PolarData as pol
import matplotlib.pyplot as plt
from GridCreator import ShortestPath as sp

np.set_printoptions(precision=3, suppress=True)

loc = r'C:\Users\UKOGH001\Documents\05 Personal Projects\02 Vendee\02 Routing\Polars'
polars = pol.Polars(loc).readfiles()
#pp.polarplt(polars[1], [1])

grdbuild = gs.GridStep(p.start, p.end, p.bound)
grid = grdbuild.GraphBuild(1, 60, 90, 0.5)

x = grid['x'].to_numpy()
y = grid['y'].to_numpy()

#grid.to_csv(r'C:\Users\UKOGH001\Documents\05 Personal Projects\02 Vendee\02 Routing\graph.csv')
wv.WindVec(Wind.u, Wind.v, Wind.X, Wind.Y, x, y, [], [], [], True)

vert = sp.Shortpath(polars, Wind.wind, p.res)
sol = vert.Dijkstra(grid, 1)
path = vert.Path(sol[1])
print("Total Time: " + str(sol[0][-1]))

wv.WindVec(Wind.u, Wind.v, Wind.X, Wind.Y, x, y, path, sol[2][path], polars[0], False)
regrid = grid
for i in range(10):
    regrid = grdbuild.GridRebuild(regrid.loc[path, :], 1)

    x = regrid['x'].to_numpy()
    y = regrid['y'].to_numpy()
    wv.WindVec(Wind.u, Wind.v, Wind.X, Wind.Y, x, y, [], [], [], True)
    sol = vert.Dijkstra(regrid, min(i + 1, 2))
    path = vert.Path(sol[1])
    print("Total Time: " + str(sol[0][-1]))

    wv.WindVec(Wind.u, Wind.v, Wind.X, Wind.Y, x, y, path, sol[2][path], polars[0], False)