################################################################################
################################################################################


import numpy as np
import pandas as pd


# Data in the ant trajectory format
# It should be a pandas dataframe with (t * n) shape where t = frame count.

class TrajectoryData:

    def __init__(dframe):
        self.trajectory_ = dframe
        self.firstderivative_ = pd.DataFrame()

    def trajectory(self):
        return self.trajectory_

    def set_trajectory(self, newdata):
        self.trajectory_ = newdata

    def firstderivative(self):
        shape = np.shape(self.firstderivative_)
        if shape == (0, 0):
            self.firstderivative_ = self.derivative(data)
        return self.firstderivative_

    def derivative(self, dframe, order=1):

        if order == 0:
            print('Zeroth order derivative detected')

        else:
            while order > 0:
                derivative = dframe.loc(1:,1:)
                derivative = dframe.loc(1:,1:) - dframe.loc(:-2,1:)
                dframe = derivative

        return dframe
               
