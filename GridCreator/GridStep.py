import numpy as np
import pandas as pd
import math

class GridStep:
    minSpacing = 11
    conv = 2 * np.pi / 360
    cols = ['Band', 'ID', 'x', 'y']
    dist = np.array([0.1, 0.2, 0.3])

    def __init__(self, start, end, bound):
        self.start = start
        self.end = end
        self.bound = bound


    def GraphBuild(self, spacing, theta1, theta2, res):
        #distance between start and end
        dist = np.sqrt((self.start[0] - self.end[0]) ** 2 + (self.start[1] - self.end[1]) ** 2)
        num = math.ceil(dist / spacing)
        const = 2 * np.pi * 2 * theta1 / (360 * res)
        band_num = [max(2 * int(const * x) + 1, self.minSpacing) for x in range(0, num)]

        #Direction from start to end
        if (self.end[0] - self.start[0]) == 0:
            t_0 = 90 if (self.start[1] < self.end[1]) else 270
        else:
            t_0 = (np.arctan((self.end[1] - self.start[1]) / (self.end[0] - self.start[0])) / self.conv) % 360

        #Tapering angle details
        psi = 180 - (theta1 + theta2)
        hyp = dist * np.sin(theta2 * self.conv) / np.sin(psi * self.conv)
        adj = hyp * np.cos(theta1 * self.conv)
        print(adj / dist)

        id = 1
        point = []
        #first point
        row = [0, 0, self.start[0], self.start[1]]
        point.append(row)

        for band in range(1, num):
            r = spacing * band
            scale = 1 if r < adj else 1 - (r - adj)/(dist - adj)
            for n in range(math.ceil(band_num[band] * scale)):
                th = (t_0 + (2 * theta1 / math.ceil(band_num[band] * scale) * n - theta1) * scale) * self.conv


                x = r * np.cos(th) + self.start[0]
                y = r * np.sin(th) + self.start[1]

                if self.bound[0][0] <= x <= self.bound[0][1]:
                    if self.bound[1][0] <= y <= self.bound[1][1]:
                        row = [band, id, x, y]
                        point.append(row)
                        id += 1
        row = [num, id, self.end[0], self.end[1]]
        point.append(row)
        return pd.DataFrame(point, columns=self.cols)

    def Suround(self, x1, x2, y1, y2, d, bool):
        if bool:
            midp_x, midp_y = (x1 + x2) / 2, (y1 + y2) / 2
        else:
            midp_x, midp_y = x1, y1

        slope = -(x2 - x1) / (y2 - y1)
        const = midp_y - slope * midp_x
        a, b = 1 + slope ** 2, -2 * (midp_x + slope * midp_y - const * slope)
        c = const ** 2 + midp_x ** 2 + midp_y ** 2 - 2 * midp_y * const - d ** 2
        disc = np.sqrt(b ** 2 - 4 * a * c)
        solx = np.array([(- b + disc) / (2 * a), (- b - disc) / (2 * a)])
        solx = solx.ravel()
        if bool:
            solx = np.append(solx, midp_x)
        soly = slope * solx + const
        return solx, soly

    def GridRebuild(self, graph, num):
        #make close extra points
        point = []
        graphmerg = pd.concat([graph, graph.shift(-1).add_prefix('next_')], axis=1)
        d = self.dist / num
        id = 0
        band = 0
        for row in graphmerg.iloc[:-1, :].itertuples():
            #add row data
            rowadd = [band, id, row[3], row[4]]
            point.append(rowadd)
            #surrounding points to x1, y1:
            if id > 0:
                sols = self.Suround(row[3], row[7], row[4], row[8], d, False)
                for i, j in zip(sols[0], sols[1]):
                    id += 1
                    rowadd = [band, id, i, j]
                    point.append(rowadd)

            band += 1
            #make intermediate points
            sols = self.Suround(row[3], row[7], row[4], row[8], d, True)
            for i, j in zip(sols[0], sols[1]):
                id += 1
                rowadd = [band, id, i, j]
                point.append(rowadd)
            band += 1
            id += 1

        lastrow = graph.iloc[-1, :]
        rowadd = [band, id, lastrow['x'], lastrow['y']]
        point.append(rowadd)
        return pd.DataFrame(point, columns = self.cols)

