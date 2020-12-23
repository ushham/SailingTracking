import numpy as np
import math
from GridCreator import GridStep as gs

class Shortpath:
    conv = 360 / (2 * np.pi)
    dircount = 360

    def __init__(self, polar, wind, res):
        self.sail = polar[0]
        self.polar = polar[1]
        self.wind = wind
        self.res = res

    def bestpolar(self, k, angle):
        # Returns best polar given wind data
        # Checks number of polars availible for checks
        x1, x2 = math.floor(angle) % self.dircount, math.ceil(angle) % self.dircount
        if len(self.polar.shape) == 2:
            y1, y2 = self.polar[x1, k], self.polar[x2, k]
            pol = 0
        elif len(self.polar.shape) == 3:
            inx = np.argmax(self.polar[:, x1, k])
            y1, y2 = self.polar[inx, x1, k], self.polar[inx, x2, k]
            pol = inx
        else:
            print('Error with polar data')
            y1, y2 = 0, 0
            pol = 0

        # profprms a linear regression on two speeds given two angles
        if x1 == x2 or y1 == y2:
            boat_speed = y1
        else:
            coef = np.polyfit([x1, x2], [y1, y2], 1)
            boat_speed = coef[0] * angle + coef[1]
        return pol, boat_speed

    def timetravel(self, p1, p2):
        dist = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        if (p2[0] - p1[0]) == 0:
            theta = np.pi / 2 if (p2[1] - p1[1]) > 0 else 3 * np.pi / 2
        elif (p2[1] - p1[1]) == 0:
            theta = 0 if (p2[0] - p1[0]) > 0 else np.pi
        else:
            theta = (2 * np.pi - np.arctan((p2[1] - p1[1]) / (p2[0] - p1[0]))) % (2 * np.pi) if (p2[0] - p1[0])>0 else np.pi - np.arctan((p2[1] - p1[1]) / (p2[0] - p1[0]))

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
                t_w = np.pi - np.arctan(v / u) if u > 0 else (2 * np.pi - np.arctan(v / u)) % (2 * np.pi)

            s_w = int(np.sqrt(u ** 2 + v ** 2))
            t_ab = (t_w - theta) * self.conv % self.dircount

            pol, speed = self.bestpolar(s_w, t_ab)

            time = dist / speed if speed > 0 else np.inf
        return time, pol, [t_ab, t_w * self.conv, theta * self.conv], s_w

    def Dijkstra(self, graph, upper):
        #input graph, outputs pandas df with list of vertices and times for all points
        #make list of vertices with infinite distance
        vertices = graph.shape[0]
        dist = np.inf * np.ones(vertices)
        sail = np.zeros(vertices)
        pred = np.zeros(vertices)
        wind_speed = np.zeros(vertices)
        angle = np.zeros((vertices, 3))
        vert = [x for x in range(0, vertices)]

        #fist element
        dist[0] = 0

        while len(vert) > 0:
            #find vertex in dist with min time
            inx_temp = np.argmin(dist[vert])
            inx = np.arange(dist.shape[0])[vert][inx_temp]
            vert.remove(inx)
            #print(dist, inx)

            band = graph.at[inx, 'Band']
            x1, y1 = graph.at[inx, 'x'], graph.at[inx, 'y']
            for row in graph[(graph['Band'] >= band) & (graph['Band'] <= band + upper)].itertuples():
                id = row[2]
                if id in vert:
                    x2, y2 = row[3], row[4]
                    timesail = self.timetravel([x1, y1], [x2, y2])
                    md = dist[inx] + timesail[0]
                    if md < dist[id]:
                        sail[id] = timesail[1]
                        angle[id, :] = timesail[2]
                        wind_speed[id] = timesail[3]
                        dist[id] = md
                        pred[id] = inx

        return dist, pred, sail, angle, wind_speed

    def Path(self, sol):
        x = np.inf
        p = []
        p.append(len(sol) - 1)
        while x > 0:
            x = int(sol[p[0]])
            p.insert(0, x)
        return p
