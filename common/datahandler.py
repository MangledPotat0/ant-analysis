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

    def trajectory(self):
        return self.trajectory_

    def set_trajectory(self, newdata):
        self.trajectory_ = newdata

    def firstderivative(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(self.trajectory())
        return self.firstderivative_

    def derivative(self, dframe, order=1):

        data = dframe.to_numpy()

        if order == 0:
            print('Zeroth order derivative detected')

        else:
            while order > 0:
                derivative = data[1:,1:] - data[:-1,1:]
                data = data[1:,:]
                data[:,1:] = derivative
                order -= 1

        return pd.DataFrame(data)
               
