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
    theta_col = 'Theta'
    rad_col = 'Radius'
    dircount = 360
    m2knts = 1.943844
    conv = 360 / 2 * np.pi
    cols = [id_col, prev_col, time_col, x_col, y_col, theta_col, rad_col, sail_col]

    def __init__(self, wind, polars, initial_x, initial_y, windres, windloc):
        self.windfield = wind   #as vector field
        self.ini_x = initial_x
        self.ini_y = initial_y
        self.polar = np.array(polars[1])
        self.sails = polars[0]
        self.w_res = windres
        self.w_loc = windloc

    def winddata(self, data):
        #Retuns wind data at given location
        x = data[3]
        y = data[4]

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
        #Checks number of polars availible for checks
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

    def internal(self, rad, theta, prevtheta, prevrad):
        #find rows of closest theta
        x1 = prevtheta[prevtheta > theta]
        x2 = prevtheta[prevtheta < theta]
        if x1.shape[0] > 0 and x2.shape[0] > 0:
            x1 = int(prevtheta[prevtheta > theta].min())

            x2 = int(prevtheta[prevtheta < theta].max())
            r1, r2 = np.max(prevrad[x1]), np.max(prevrad[x2])

            coef = np.polyfit([x1, r1], [x2, r2], 1)
            rfinal = coef[0] * theta + coef[1]
            out = rad > rfinal
        else:
            out = True

        return out


    def UpdatePoints(self, maxt):
        count = 0
        time = 0
        prevdata = []
        datahold = []

        #for loop to run through data
        for t in range(time, maxt, self.timestep):

            dataprev = prevdata
            prevdata = []
            if count == 0:
                #first iteration
                #[id_col, prev_col, time_col, x_col, y_col, theta_col, rad_col, sail_col]
                data = [count, count, t, self.ini_x, self.ini_y, 0, 0, 'NA']
                prevdata.append(data)
                datahold.append(data)
                count += 1

            else:
                #prevpoints = dataf.drop(dataf[dataf[self.time_col] != t - self.timestep].index)
                dat = np.array(dataprev)

                r0, t0 = dat[:, 6].astype(float), dat[:, 5].astype(float)

                for row in dataprev:

                    if t == 1:
                        rg = np.linspace(0, self.dircount - 1, self.dircount)
                    else:
                        rg = np.linspace((row[5] - 40), (row[5] + 40), 81)
                        rg = rg % self.dircount
                    for theta in rg:

                        #true windspeed and direction
                        ang, kts = self.winddata(row)

                        #angle of boat to wind
                        boat_angle = (ang - theta) % self.dircount

                        #create linear function to find intermediate value of speed given angle
                        pol, boat_speed = self.bestpolar(kts, boat_angle)
                        dist = self.timestep * boat_speed
                        xloc, yloc = dist * np.cos(theta * self.conv) + row[3], dist * np.sin(theta * self.conv) + row[4]

                        #direction of new point to orign
                        the_ini = np.arctan(yloc / xloc) / self.conv
                        dist_ini = np.sqrt(xloc ** 2 + yloc ** 2)

                        # check if point is internal
                        bool = self.internal(dist_ini, the_ini, t0, r0)


                        if bool:
                            #[id_col, prev_col, time_col, x_col, y_col, theta_col, rad_col, sail_col]
                            data = [count, row[0], t, xloc, yloc, theta, boat_speed, self.sails[pol]]
                            prevdata.append(data)
                            count += 1
                        else:
                            print('Here' + str(count))

                datahold.extend(prevdata)

        return pd.DataFrame(datahold, columns = self.cols)




