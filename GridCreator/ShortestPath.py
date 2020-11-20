import numpy as np
import pandas as pd
import math
from GridCreator import GridStep as gs


class Shortpath:
    conv = 360 / (2 * np.pi)
    dircount = 360

    def __init__(self, graph, polar, wind, res):
        self.graph = graph
        self.sail = polar[0]
        self.polar = polar[1]
        self.wind = wind
        self.res = res

    def bestpolar(self, k, theta):
        x1, x2 = math.floor(theta) % self.dircount, math.ceil(theta) % self.dircount
        if len(self.polar.shape) == 2:
            y1, y2 = self.polar[x1, k], self.polar[x2, k]
            pol = 0
        elif len(self.polar.shape) == 3:
            inx = np.argmax(self.polar[:, x1, k])
            y1, y2 = self.polar[inx, x1, k], self.polar[inx, x2, k]
            pol = inx
        return pol, y1, y2

    def timetravel(self, p1, p2, row):
        dist = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        if (p2[0] - p1[0]) == 0:
            theta = np.pi / 2 if (p2[1] - p1[1]) > 0 else 3 * np.pi / 2
        elif (p2[1] - p1[1]) == 0:
            theta = 0 if (p2[0] - p1[0]) > 0 else np.pi
        else:
            theta = (2 * np.pi - np.arctan((p2[1] - p1[1]) / (p2[0] - p1[0]))) % (2 * np.pi) if (p2[0] - p1[0])>0 else np.arctan((p2[1] - p1[1]) / (p2[0] - p1[0]))

        x, y = int(p1[0] / self.res[0]), int(p1[1] / self.res[1])

        if (x > self.wind[0].shape[1] - 1) or (y > self.wind[0].shape[0] - 1):
            time = np.inf
            pol = 0
        else:
            u, v = self.wind[0][y, x], self.wind[1][y, x]
            if v == 0:
                t_w = 0 if u < 0 else np.pi
            elif u == 0:
                t_w = np.pi / 2 if v > 0 else 3 * np.pi / 2
            else:
                t_w = np.pi - np.arctan(v / u) if u > 0 else (2 * np.pi -  np.arctan(v / u)) % (2 * np.pi)

            s_w = int(np.sqrt(u ** 2 + v ** 2))

            t_ab = (t_w - theta) * self.conv % self.dircount

            pol, y1, y2 = self.bestpolar(s_w, t_ab)

            x1, x2 = math.floor(t_ab), math.ceil(t_ab)
            if x1 == x2:
                speed = y1
            else:
                coef = np.polyfit([x1, x2], [y1, y2], 1)
                speed = coef[0] * t_ab + coef[1]
            time = dist / speed if speed > 0 else np.inf
        return time, pol

    def Dijkstra(self):
        #input graph, outputs pandas df with list of vertices and times for all points
        #make list of vertices with infinite distance
        vertices = self.graph.shape[0]
        dist = np.inf * np.ones(vertices)
        sail = np.zeros(vertices)
        pred = np.zeros(vertices)
        vert = [x for x in range(0, vertices)]

        #fist element
        dist[0] = 0


        while len(vert) > 0:
            #find vertex in dist with min time
            inx_temp = np.argmin(dist[vert])
            inx = np.arange(dist.shape[0])[vert][inx_temp]
            vert.remove(inx)

            band = self.graph.at[inx, 'Band']
            x1, y1 = self.graph.at[inx, 'x'], self.graph.at[inx, 'y']
            for row in self.graph[(self.graph['Band'] >= band) & (self.graph['Band'] <= band + 1)].itertuples():
                id = row[2]
                if id in vert:
                    x2, y2 = row[3], row[4]
                    timesail = self.timetravel([x1, y1], [x2, y2], row)
                    md = dist[inx] + timesail[0]
                    if md < dist[id]:
                        sail[id] = timesail[1]
                        dist[id] = md
                        pred[id] = inx

        return dist, pred, sail

    def Path(self, sol):
        x = np.inf
        p = []
        p.append(len(sol) - 1)
        while x > 0:
            x = int(sol[p[0]])
            p.insert(0, x)
        return p
