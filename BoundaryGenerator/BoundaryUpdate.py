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
    conv = 360 / 2 * np.pi
    w_res = p.res
    cols = [id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]

    def __init__(self, wind, polars, initial_x, initial_y):
        self.wind = wind   #as vector field
        self.ini_x = initial_x
        self.ini_y = initial_y
        self.polar = np.array(polars[1])
        self.sails = polars[0]

    def winddata(self, data):
        #Retuns wind data at given location
        x = int(data[3] // p.res[0])
        y = int(data[4] // p.res[1])

        u, v = self.wind[0][y, x], self.wind[1][y, x]
        if v == 0:
            t_w = 0 if u < 0 else np.pi
        elif u == 0:
            t_w = np.pi / 2 if v > 0 else 3 * np.pi / 2
        else:
            t_w = np.pi - np.arctan(v / u) if u > 0 else (2 * np.pi - np.arctan(v / u)) % (2 * np.pi)

        s_w = int(np.sqrt(u ** 2 + v ** 2))

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

    def filt_data(self, list, res):
        #filter data into even spacing by res
        df = pd.DataFrame(list, columns=self.cols)

        indexlist = []
        for theta in range(0, self.dircount, res):
            #filter data so only have values in allowed neighbourhood
            dtfilt = df[(df[self.the_o_col] >= theta - self.pm_res) & (df[self.the_o_col] <= theta + self.pm_res)]
            if dtfilt.shape[0] > 0:
                indexlist.append(df.iloc[dtfilt[self.rad_col].idxmax()].tolist())

        return indexlist

    def UpdatePoints(self, maxt, res):
        count = 0
        time = 0
        #two lists, one storeing the previous iteration, the other all the data to store
        prevdata = []
        datahold = []

        #for loop to run through data
        for t in range(time, maxt, self.timestep):

            dataprev = prevdata
            prevdata = []
            if count == 0:
                #first iteration
                #[id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]
                data = [count, count, t, self.ini_x, self.ini_y, 0, 0, 0, 'NA']
                prevdata.append(data)
                datahold.append(data)
                count += 1

            else:
                dat = np.array(dataprev)

                #radius and direction from origin
                #r0, t0 = dat[:, 6].astype(float), dat[:, 5].astype(float)
                for row in dataprev:
                    if t == 1:
                        #first time step, do full circle
                        rg = np.linspace(0, self.dircount - 1, self.dircount)
                    else:
                        #only look for solutions +- certain angle from previous direction
                        rg = np.linspace((row[5] - self.pm_angle), (row[5] + self.pm_angle), int(self.pm_angle / res))
                        rg = rg % self.dircount

                    for theta in rg:
                        #true windspeed and direction
                        ang, kts = self.winddata(row)

                        #angle of boat to wind
                        boat_angle = (ang - theta) % self.dircount

                        #Find best polar and resulting boat speed given true wind
                        pol, boat_speed = self.bestpolar(kts, boat_angle)
                        dist = self.timestep * boat_speed

                        #find new x and y location
                        xloc, yloc = dist * np.cos(theta / self.conv) + row[3], dist * np.sin(theta / self.conv) + row[4]

                        #direction of new point to orign
                        the_ini = np.arctan((yloc - self.ini_y) / (xloc - self.ini_x)) * self.conv
                        dist_ini = np.sqrt((xloc - self.ini_x) ** 2 + (yloc - self.ini_y) ** 2)

                        #[id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]
                        data = [count, row[0], t, xloc, yloc, dist_ini, the_ini, boat_speed, self.sails[pol]]
                        prevdata.append(data)
                        count += 1

                    #filter list so that only keep the best points
                    prevdata = self.filt_data(prevdata, res)

                datahold.extend(prevdata)

        return pd.DataFrame(datahold, columns = self.cols)

    def Sailable(self, point1, point2, t_w, s_w):
        #Returns false if points can be reached in time
        #find sailing angle
        if point2[0] - point1[0] == 0:
            theta = 0 if point2[1] >= point1[1] else np.pi
        else:
            theta = np.arctan((point2[1] - point1[1]) / (point2[0] - point1[0]))

        theta = (90 - theta * self.conv) % self.dircount
        dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

        #wind relative to boat
        boat_ang = (t_w - theta) % self.dircount
        pol, speed = self.bestpolar(s_w, boat_ang)
        return dist / speed > self.timestep, pol, speed

    def MaxDist(self, point1, mindist, angle):
        #finds the maximum distance from origin to point2 given point1
        angle = ((90 - angle) % self.dircount) / self.conv
        point2 = [mindist * np.cos(angle), mindist * np.sin(angle)]
        t_w, s_w = self.winddata(point1)

        dist = mindist
        distdelta = 1
        i = 0
        increase = True
        pol, speed = 0, 0
        if self.Sailable(point1, point2, t_w, s_w)[0]:
            while distdelta > 0.01 or i < 100:
                i += 1
                previnc = increase
                bool, pol, speed = self.Sailable(point1, point2, t_w, s_w)
                if bool:
                    dist = dist + distdelta
                    increase = True
                else:
                    dist = dist - distdelta
                    increase = False

                point2 = [mindist * np.cos(angle), mindist * np.sin(angle)]

                if i > 1 and (previnc != increase):
                    distdelta = distdelta / 2

        return dist, point2, pol, speed

    def ReturnPoint(self, angle, list, time, newid):
        #given list, return point
        #find min distance given angle
        #list consists of all points in previous layer
        mindist = list[list[self.the_o_col >= angle] & list[self.the_o_col <= angle]].min(level=self.rad_col)

        #run through set of points and find max distance
        dist = np.zeros((list.shape[0], 4))
        ###### MAKE MORE EFFICINET BY NOT SEARCHING ALL POSSIBLE SOLUTIONS####
        for index, row in list.iterrows():
            point1 = [row[self.x_col], row[self.y_col]]
            dist[index, :] = self.MaxDist(point1, mindist, angle)
        id = np.argmax(dist[:, 0])
        #cols = [id_col, prev_col, time_col, x_col, y_col, rad_col, the_o_col, speed_col, sail_col]
        point = [newid, list.iloc[id][self.prev_col], time, dist[id, 1][0], dist[id, 1][1], dist[id, 0], angle, dist[id, 2], dist[id, 3]]

        return point



    def MaxPoint(self, maxt, res):
        #works outward from previous boundary along line until it only has one point still connected


    #re order code so that row is only appended to list if it is the max at that angle




