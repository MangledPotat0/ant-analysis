import math
import numpy as np
import pandas as pd


# A TrajectoryData object. The point of this is to keep commonly used data
# manipulations as object attributes so that it can be called easily and without
# re-writing the same function multiple times in multiple files. However this
# comes at the expense of memory use since all the derived quantities are held
# in memory even when used in scripts that don't need some of them.


class TrajectoryData:

    # Input data is a numpy array read directly from the $(EXPID)_proc.hdf file.
    def __init__(self, dset):
        cols = ['frame', 'orientation', 'head_x', 'head_y',
                'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']
        t, _, _ = np.shape(dset)
        flat = dset.reshape([t,8])
        dframe = pd.DataFrame(flat, columns=cols)
        self.dframe = dframe


    # getters

    @property
    def trajectory(self):
        return self.dframe

    @property
    def firstderivative(self):
        return self.firstderivative_

    @property
    def speed(self):
        return self.speed_
    
    @trajectory.setter
    def set_trajectory(self, newdata):
        self.trajectory_ = newdata


    # setters

    @firstderivative.setter
    def firstderivative(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(self.trajectory())
            self.firstderivative_ = self.moving_average(
                                                self.firstderivative_, 5)
            self.speed_ = self.compute_speed(self.firstderivative_)
        return self.firstderivative_
    
    @speed.setter
    def speed(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(self.trajectory())
            self.speed_ = self.compute_speed(self.firstderivative_)
        return self.speed_


    # other methods

    def derivative(self, dframe, order=1):
        colnames = dframe.columns

        data = dframe.copy().to_numpy()

        if order == 0:
            print('Zeroth order derivative detected')

        else:
            while order > 0:
                derivative = data[1:,1:] - data[:-1,1:]
                data = data[1:,:]
                data[:,1:] = derivative
                order -= 1

        return pd.DataFrame(data, columns=colnames)
    
    def compute_speed(self, dtable):
        colnames = ['frame', 'angular velocity',
                    'head', 'thorax','abdomen', 'centroid speed']

        darray = dtable.to_numpy()
        newtable = pd.DataFrame()
        for row in darray:
            head = np.sqrt(row[2]**2+row[3]**2)
            thorax = np.sqrt(row[4]**2+row[5]**2)
            abdomen = np.sqrt(row[6]**2+row[7]**2)
            newrow = np.array([row[0],row[1], head, thorax, abdomen,
                               np.mean([head,thorax,abdomen])])
            newrow = pd.DataFrame([newrow], columns=colnames)
            newtable = newtable.append(newrow, ignore_index=True)

        newtable['angular velocity'] = newtable['angular velocity'] + math.pi / 2
        newtable['angular velocity'] = newtable['angular velocity'] % math.pi
        newtable['angular velocity'] = newtable['angular velocity'] - math.pi / 2

        return newtable

    def moving_average(self, dframe, interval):
        mavg = dframe.rolling(interval).mean()

        return mavg
    

# EOF
