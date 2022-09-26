################################################################################
################################################################################


import numpy as np
import pandas as pd


# Data in the ant trajectory format
# It should be a pandas dataframe with (t * n) shape where t = frame count.

class TrajectoryData:

    def __init__(self, dset):
        cols = ['frame', 'orientation', 'head_x', 'head_y',
                'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']
        t, _, _ = np.shape(dset)
        flat = dset.reshape([t,8])
        dframe = pd.DataFrame(flat, columns=cols)
        self.trajectory_ = dframe
        self.firstderivative_ = pd.DataFrame()
        self.speed_ = pd.DataFrame()

    def trajectory(self):
        return self.trajectory_

    def set_trajectory(self, newdata):
        self.trajectory_ = newdata

    def firstderivative(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(self.trajectory())
            self.speed_ = self.compute_speed(self.firstderivative_)
        return self.firstderivative_

    def speed(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(self.trajectory())
            self.speed_ = self.compute_speed(self.firstderivative_)
        return self.speed_

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
        dtable = moving_average(dtable, 5)
        colnames = ['frame', 'angular_velocity',
                    'head', 'thorax','abdomen', 'centroid']

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

        return newtable

    def moving_average(self, dframe, interval):
        mavg = dframe.rolling(interval).mean()

        return mavg
    

# EOF
