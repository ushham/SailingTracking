import numpy as np
import pandas as pd
import os

class Polars:
    ftype = '.csv'
    def __init__(self, loc):
        self.fileloc = loc

    def readfiles(self):
        #read all files in from folder
        arr = os.listdir(self.fileloc)
        files = [x for x in arr if x.endswith(self.ftype)]
        datahold = []
        dataname = []
        for file in files:
            dt = np.genfromtxt(self.fileloc + '\\' + file, delimiter=',', skip_header=True)
            datahold.append(dt[:, 1:])
            str = file.split('.')
            dataname.append(str[0])
        datahold = np.asarray(datahold)
        return dataname, datahold