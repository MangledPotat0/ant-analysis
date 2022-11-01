import sys
sys.path.append('..\\common')

import argparse
import cv2 as cv
from datetime import date
import h5py
import json
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

from datahandler import TrajectoryData
import logmaker as lm


# TODO: WORK IN PROGRESS 

# This function works in the following way:
# 1. For each ant, segment the trajectory into consecutive periods for each
#    state
# 2. Use the duration of each activity period to construct an empirical
#    distribution of the active period duration
# 3. Using the active ant count as reference, identify the transient time and
#    remove the transient period from each trajectory
# 4. From the empirical distribution of active states, compute the character-
#    istic timescale of activity
# 5. Use this characteristic timescale and divide the steady state into discrete
#    intervals
# 6. Compute the activity level in each interval for each ant
# 7. Using the activity rate in each interval and the empirical distribution of
#    activity, perform Bayes theorem calculation to find the probability of
#    observing the activity levels that we did observe.


with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']


today = date.today()
today = today.strftime('%Y%m%d')

srcpath = str(datapath + 'preprocessed/')
outputpath = str(datapath + 'processed/state_tracking/')
figspath = str(datapath + 'processed/state_tracking/' + today + '/')

try:
    os.mkdir(outputpath)
except:
    pass

try:
    os.mkdir(figspath)
except:
    pass


# Segments the trajectory into a series of active periods
def extract_periods(dframe):
    
    groups = {}
    for ant in list(set(dframe['antID'].to_list())):
        active = dframe[dframe['antID'] == ant]
        active.sort_values(by=['frame'])
        frame_list = active['frame'].to_numpy()
        groups[ant] = list(groupc(frame_list))
        for bounds in groups[ant]:
            sequential = active.loc[
                    (active['frame']>=bounds[0]) & (active['frame']<=bounds[1])]
            yield sequential


# Helper function that gives us the indices for the bounds of the continuous
# active periods
def groupc(src):
    for x,y in it.groupby(src, lambda n, c=it.count(): n-next(c)):
        y = list(y)
        if len(np.shape(y)) == 1:
            yield y[0], y[-1]
        else:
            yield y[0][1], y[-1][1]


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', help='Experiment ID', nargs='+')

    args = vars(ap.parse_args())
    expids = args['expid']
    allvalues = pd.Series(dtype=float)

    for expid in expids:
        dtable = pd.read_hdf('{}{}/{}_active_ants.hdf5'.format(
                                                    srcpath, expid, expid))
        maxant = max(dtable['antID'])

        # Construct the empirical distribution of active time / total time
        values = []
        for ant in range(maxant):
            thisant = dtable[dtable['antID']==ant].copy()
            active_counts = len(thisant[thisant['state']=='active'])
            inactive_counts = len(thisant[thisant['state']=='inactive'])
            values.append(active_counts / (active_counts+inactive_counts))
        
        values = pd.Series(values)
        allvalues = allvalues.append(values)
        sns.histplot(data=values)
        plt.savefig('{}{}state_time_ratio.png'.format(figspath, expid))
        plt.close()
    
    sns.histplot(data=allvalues)
    plt.savefig('{}state_time_ratio.png'.format(figspath))
    plt.close()

# EOF
