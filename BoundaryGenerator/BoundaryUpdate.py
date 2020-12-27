from Control import Parameters as p
import numpy as np
import pandas as pd
import math

class PointUpdate:
    timestep = 1
    id_col = 'ID'
    prev_col = 'Prev_ID'
    sail_col = 'Sail'
    time_col = 'Time'
    x_col = 'x_loc'
    y_col = 'y_loc'
    rad_col = 'Radius'
    the_o_col = 'Theta_Origin'
    speed_col = 'Speed'
    dircount = 360
    m2knts = 1.943844
    pm_angle = 90
    pm_res = 0.5
    conv = 360 / (2 * np.pi)
    w_res = p.res
    cols = [id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]

    def __init__(self, wind, polars, initial_x, initial_y):
        self.wind = wind   #as vector field
        self.ini_x = initial_x
        self.ini_y = initial_y
        self.polar = np.array(polars[1])
        self.sails = polars[0]

    def func(self, time):
        #function to increase the number of points in boundary as time increases
        t0 = 40
        t10 = 300
        return int((t10 - t0) * math.log(time, 10) + (t10 - t0))

    def winddata(self, data):
        #Retuns wind data at given location
        #converts direction to wind direction relative boat location
        x = int(data[0] // p.res[0])
        y = int(data[1] // p.res[1])

        u, v = self.wind[0][y, x], self.wind[1][y, x]
        t_w = 2 * np.pi - np.arctan2(v, u)
        s_w = int(np.sqrt(u ** 2 + v ** 2))
        #print(u, v, s_w, t_w)
        return t_w, s_w

    def bestpolar(self, k, angle):
        #Returns best polar given wind data
        #angle in degrees
        #Checks number of polars availible for checks
        #k refers to windspeed
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

        #profprms a linear regression on two speeds given two angles
        if x1 == x2 or y1 == y2:
            boat_speed = y1
        else:
            coef = np.polyfit([x1, x2], [y1, y2], 1)
            boat_speed = coef[0] * angle + coef[1]
        return pol, boat_speed

    def UpdatePoints(self, maxt, res):
        count = 0
        time = 0
        #two lists, one storeing the previous iteration, the other all the data to store
        prevdata = []
        datahold = []

        #for loop to run through data
        for t in range(time, maxt, self.timestep):
            print(t)

            dataprev = prevdata
            prevdata = []
            if count == 0:
                #first iteration
                #[id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]
                data = [count, count, t, self.ini_x, self.ini_y, 0, 0, 0, np.nan]
                prevdata.append(data)
                datahold.append(data)
                count += 1

            else:
                dat = np.array(dataprev)

                for dir_angle in np.linspace(0, self.dircount, self.func(t)):
                    #Find max dist from centre given previous points
                    prevdata.append(self.ReturnPoint(dir_angle, dat, t, count))
                    count += 1
                datahold.extend(prevdata)

        return pd.DataFrame(datahold, columns=self.cols)


    def Sailable(self, point1, point2, t_w, s_w):
        #Returns false if points can be reached in time
        #find sailing angle
        theta = np.arctan2(point2[1] - point1[1], point2[0] - point1[0])

        theta = theta * self.conv if theta > 0 else (2 * np.pi + theta) * self.conv
        dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

        #wind relative to boat
        boat_ang = (theta - t_w * self.conv) % self.dircount

        pol, speed = self.bestpolar(s_w, boat_ang)
        out = dist / speed < self.timestep if speed !=0 else False

        out = True if dist == 0 else out
        return out, pol, speed

    def MaxDist(self, point1, mindist, angle, t_w, s_w):
        #finds the maximum distance from origin to point2 given point1
        ang = ((np.pi / 2 - angle) % (2 * np.pi))   #converts angle from math to compass angles
        point2x, point2y = mindist * np.cos(ang) + self.ini_x, mindist * np.sin(ang) + self.ini_y

        dist = mindist
        distdelta = 2
        i = 0
        increase = True
        pol, speed = 0, 0
        if self.Sailable(point1, [point2x, point2y], t_w, s_w)[0]:
            while distdelta > 0.001 and i < 30:
                i += 1
                previnc = increase
                bool, pol, speed = self.Sailable(point1, [point2x, point2y], t_w, s_w)
                #print(angle, i, distdelta, dist, self.Sailable(point1, [point2x, point2y], t_w, s_w))
                if bool:
                    dist = dist + distdelta
                    increase = True
                else:
                    dist = dist - distdelta
                    increase = False
                point2x, point2y = dist * np.cos(ang) + self.ini_x, dist * np.sin(ang) + self.ini_y

                if i > 1 and (previnc != increase):
                    distdelta = distdelta / 2

        return dist, point2x, point2y, speed, pol

    def ReturnPoint(self, angle, list, time, newid):
        #given list, return point
        #find min distance given angle
        #list consists of all points in previous layer
        filtlist = list[(list[:, 6] >= angle - 1) & (list[:, 6] <= angle + 1)]
        mindist = np.min(filtlist[:, 5]) if filtlist.shape[0] > 0 else 0

        #run through set of points and find max distance
        dist = np.zeros((list.shape[0], 5))
        maxdist, id = 0, 0
        #run through every n-th row, and then find closest for reinspection
        n = 10
        for row in list[0::n]:
            point1 = [row[3], row[4]]
            t_w, s_w = self.winddata(point1)
            d = self.MaxDist(point1, mindist, angle / self.conv, t_w, s_w)[0]
            if d > maxdist:
                maxdist = d
                id = row[0]

        #filter array and re search points not run
        filtlist = list[(list[:, 0] >= id - n) & (list[:, 0] <= id + n)]
        i = 0
        for row in filtlist:
            point1 = [row[3], row[4]]
            t_w, s_w = self.winddata(point1)
            dist[i, :] = self.MaxDist(point1, mindist, angle / self.conv, t_w, s_w)
            i += 1


        id = np.argmax(dist[:, 0])
        #cols = [id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]
        point = [newid, list[id, 0], time, dist[id, 1], dist[id, 2], dist[id, 0], angle, dist[id, 3], dist[id, 4]]

        return point